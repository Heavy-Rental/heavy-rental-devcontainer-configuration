# Feature Specification: Haystack Postgres Merge Sync

**Feature Branch**: `001-haystack-postgres-merge-sync`

**Created**: 2026-08-08

**Status**: Implemented

**Input**: User description: "Add a writable PostgreSQL database to the Haystack Fast API devcontainer that merge-syncs from Heavy-Rental-REST-API `postgres-primary` (`heavy_rental`) every 24 hours, with an option to halt when the primary connection cannot be detected. Local-only rows must be retained on sync."

**As-built notes**: FDW-based merge upsert; PK or unique merge keys; additive schema evolution by default; opt-in parity flags (`DROP_ORPHAN_COLUMNS`, indexes, safe type widenings, `SYNC_MODE=mirror`). Runtime checks: [verification.md](./verification.md). OpenSpec SoT: `openspec/specs/haystack-devcontainer/spec.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local writable Postgres for Haystack (Priority: P1)

As a Haystack developer, I open the Haystack Fast API devcontainer and have a local PostgreSQL database I can fully read and write without depending on the REST API database remaining the only store for my local experiments.

**Why this priority**: Without a local writable database, merge sync and local development against Postgres are impossible.

**Independent Test**: Start only the Haystack Compose stack’s `db` service (or full stack). Connect as the app user and successfully `INSERT`, `SELECT`, `UPDATE`, and `DELETE` rows.

**Acceptance Scenarios**:

1. **Given** the Haystack stack is started and the local database service is healthy, **When** the Haystack app (or a client) connects using the configured local connection string, **Then** it can create and query data in database `heavy_rental`.
2. **Given** a row was inserted only on the local database, **When** no sync has run, **Then** that row remains available for read/write on the local database.

---

### User Story 2 - Merge refresh from REST API primary (Priority: P1)

As a Haystack developer, when the REST API primary is available, I can refresh my local database so it receives new and updated rows from `postgres-primary` without wiping rows that exist only on my local database.

**Why this priority**: Merge sync is the core value of connecting Haystack data to the shared rental domain data.

**Independent Test**: With both stacks on `heavy-rental-network` and primary healthy, run one sync cycle; verify primary rows appear locally, a pre-inserted local-only row remains, and a shared-key row reflects primary values after sync.

**Acceptance Scenarios**:

1. **Given** `postgres-primary` is reachable and contains table rows in `heavy_rental`, **When** a successful sync cycle completes, **Then** those rows are present in the local database (inserted if missing, updated if the same primary key exists).
2. **Given** a row exists only on the local database (primary key not present on primary), **When** a successful sync cycle completes, **Then** that local-only row is still present.
3. **Given** a row with the same primary key exists on both databases with different non-key column values, **When** a successful sync cycle completes, **Then** the local row’s non-key columns match the primary’s values (primary wins on conflict).
4. **Given** a row was deleted on the primary but still exists locally, **When** a successful sync cycle completes, **Then** the local row is **not** required to be deleted (deletes on primary are not mirrored).

---

### User Story 3 - Halt or skip when primary is unreachable (Priority: P1)

As a Haystack developer, if the REST API primary cannot be detected, the sync process must not destroy or partially wipe local data; I can choose to halt the sync job or skip the cycle and try later.

**Why this priority**: Failed connectivity must not corrupt the local sandbox or leave the developer without a database.

**Independent Test**: Stop or disconnect `postgres-primary`, run sync with halt enabled and with halt disabled; observe halt vs skip behavior and confirm local data and local DB service remain usable.

**Acceptance Scenarios**:

1. **Given** `HALT_ON_PRIMARY_UNAVAILABLE` is `true` and `postgres-primary` cannot be detected after the configured retries, **When** the sync process evaluates connectivity, **Then** it does not modify local application tables and the sync job stops (halts).
2. **Given** `HALT_ON_PRIMARY_UNAVAILABLE` is `false` and `postgres-primary` cannot be detected, **When** the sync process evaluates connectivity, **Then** it skips the merge for that cycle, leaves local data intact, and waits for the next interval.
3. **Given** the sync job has halted or skipped, **When** the developer continues using the Haystack app against the local database, **Then** the local database remains healthy and accepts read/write operations.

---

### User Story 4 - Automatic refresh every 24 hours (Priority: P2)

As a Haystack developer, my local database is refreshed from primary on a 24-hour cadence without manual intervention, after an initial attempt when the sync service starts.

**Why this priority**: Periodic refresh keeps local data useful over multi-day sessions; less critical than first-run merge and local DB availability.

**Independent Test**: Configure a short interval for test (e.g. 60 seconds); observe at least two successful merge cycles; restore default 24h for production of the config.

**Acceptance Scenarios**:

1. **Given** the sync service starts and primary is reachable, **When** the service finishes initialization, **Then** it attempts a merge cycle before sleeping for the configured interval.
2. **Given** the default configuration, **When** a successful cycle completes, **Then** the next automatic attempt occurs after 24 hours (86400 seconds), unless the interval environment variable is overridden.
3. **Given** primary remains reachable across intervals, **When** each interval elapses, **Then** another merge cycle runs without requiring the developer to run a command.

---

### User Story 5 - Configurable interval and halt behavior (Priority: P3)

As a Haystack developer, I can adjust sync interval and halt-on-unavailable behavior via environment variables without changing script source.

**Why this priority**: Improves operability and testing; defaults already satisfy the main product requirement.

**Independent Test**: Set `SYNC_INTERVAL_SECONDS` and `HALT_ON_PRIMARY_UNAVAILABLE` in Compose; confirm observed behavior matches.

**Acceptance Scenarios**:

1. **Given** `SYNC_INTERVAL_SECONDS` is set to a non-default positive integer, **When** a cycle completes, **Then** the wait before the next cycle equals that value in seconds.
2. **Given** `HALT_ON_PRIMARY_UNAVAILABLE` is toggled between `true` and `false`, **When** primary is unreachable, **Then** the process either halts or skips according to the flag.

---

### Edge Cases

- What happens when primary is reachable but authentication fails? Treat as unavailable for merge; do not modify local app tables; apply halt/skip policy.
- What happens when a table has no primary key or unique constraint? Skip that table with a clear log warning by default (do not truncate unless an explicit optional mode is enabled later).
- What happens if local schema is missing tables that exist on primary? Sync creates missing tables (`LIKE` staging) before data merge when schema evolution is enabled (default).
- What happens if primary adds a column to an existing table? With `SCHEMA_EVOLUTION=true` (default), local table gets `ADD COLUMN` then upsert fills data.
- What happens if primary removes a column? With default merge mode, local column is **kept**. With `DROP_ORPHAN_COLUMNS=true` or `SYNC_MODE=mirror`, local column may be dropped (data loss).
- What happens if sync fails mid-merge? Prefer failing the cycle without dropping local application tables; staging artifacts may be cleaned up; local data from previous successful cycles remains.
- What happens if REST API stack was never started? Same as primary unreachable (halt or skip).
- What happens on first local DB init with empty data? Successful merge populates from primary; local-only rows do not exist yet.
- Multi-schema: only `public` is supported; `SOURCE_SCHEMAS` is documented for future use.
- Foreign keys: `SYNC_FOREIGN_KEYS` is reserved and not implemented (logs WARN if enabled).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Haystack devcontainer Compose stack MUST provide a local PostgreSQL 17 service that is fully writable by the Haystack application.
- **FR-002**: The local database service MUST join the external Docker network `heavy-rental-network` so it can reach `postgres-primary` when that container is running.
- **FR-003**: The Haystack application service MUST be configured to use the local database (not `postgres-primary`) as its default read/write data source.
- **FR-004**: The system MUST provide a sync process that merge-refreshes data from `postgres-primary` database `heavy_rental` into the local database.
- **FR-005**: Merge sync MUST insert rows that exist on primary but not locally, matched by **merge key**: primary key if present, else a usable unique constraint/index when `ALLOW_UNIQUE_MERGE_KEY` is true (default).
- **FR-006**: Merge sync MUST update non-key columns on local rows when the same merge key exists on primary (primary wins).
- **FR-007**: Merge sync MUST retain local rows whose merge keys are not present on primary (local-only rows), under default merge mode.
- **FR-008**: Merge sync MUST NOT be required to delete local rows that were deleted on primary.
- **FR-009**: Merge sync MUST NOT use a full wipe/replace of local application tables as the default strategy (no `pg_restore --clean` of the live app schema as the merge mechanism).
- **FR-010**: Before each merge attempt, the sync process MUST detect connectivity to `postgres-primary` (e.g. readiness check and/or simple query).
- **FR-011**: When primary cannot be detected and halt mode is enabled, the sync process MUST NOT modify local application table data and MUST stop further scheduled merges in that process lifetime (halt).
- **FR-012**: When primary cannot be detected and halt mode is disabled, the sync process MUST skip the merge for that cycle, leave local data intact, and wait for the next interval.
- **FR-013**: The sync process MUST attempt a merge cycle at service start (when local DB is ready), then wait for the configured interval before subsequent attempts.
- **FR-014**: The default sync interval MUST be 24 hours (86400 seconds).
- **FR-015**: Sync interval and halt-on-unavailable behavior MUST be configurable via environment variables.
- **FR-016**: Local database host port mapping, if published, MUST avoid conflict with REST API primary host port `5432` and replica host port `5433` (recommended host port `5434`).
- **FR-017**: Credentials and connection settings for local development MAY use simple shared dev defaults aligned with the REST API stack; they are not production secrets.
- **FR-018**: The system MUST log clear outcomes for: primary unreachable, halt, skip, merge success, and per-table skip (e.g. no merge key).
- **FR-019**: With schema evolution enabled (default), the system MUST create missing local tables and MUST ADD columns present on source but missing locally before upsert.
- **FR-020**: Under default merge mode, the system MUST NOT drop local-only columns, MUST NOT auto-rename columns, and MUST NOT apply arbitrary type changes.
- **FR-021**: Opt-in flags MUST exist (default off) for: `DROP_ORPHAN_COLUMNS`, `SYNC_INDEXES`, `SYNC_UNIQUE_INDEXES`, `SAFE_TYPE_WIDENINGS`; `SYNC_MODE=mirror` MAY enable the parity set.
- **FR-022**: `SYNC_FOREIGN_KEYS` MAY be accepted as configuration but MUST NOT silently invent validated FKs until implemented (current: log and skip).

### Key Entities

- **Source database (`postgres-primary`)**: REST API primary PostgreSQL instance on `heavy-rental-network`; database name `heavy_rental`; authoritative for shared domain rows during merge.
- **Local database (`postgres-haystack` / Compose service `db`)**: Writable PostgreSQL owned by the Haystack stack; target of app R/W and merge upserts.
- **Sync job (`db-sync`)**: Long-running process that checks connectivity, merges, and sleeps on an interval.
- **Sync configuration**: Environment-driven settings (hosts, credentials, interval, halt, evolution, opt-in parity flags). See [contracts/db-sync-env.md](./contracts/db-sync-env.md).
- **Merge key**: Primary key columns, or a designated unique constraint/index when no PK; used for `ON CONFLICT`.
- **Local-only row**: A row in the local database whose merge key does not exist on the source at sync time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can start the Haystack stack and perform a successful local write within 5 minutes of a healthy `db` service (excluding image pull time).
- **SC-002**: With primary available, one successful sync cycle results in sampled primary rows being readable on the local database.
- **SC-003**: After inserting a local-only row and running sync, that row is still present (100% retention of the tested local-only key).
- **SC-004**: After changing a shared-key row on primary and syncing, local non-key values match primary for that key.
- **SC-005**: With primary stopped and halt enabled, the sync process stops without deleting pre-existing local rows; local DB remains accepting connections.
- **SC-006**: Default configuration schedules merges 24 hours apart after the initial start-of-service attempt.
- **SC-007**: Changing `SYNC_INTERVAL_SECONDS` to 60 produces a second merge attempt within approximately 60–90 seconds after the first successful cycle (allowing for merge duration).
- **SC-008** (optional extended): Unique-only table merges when `ALLOW_UNIQUE_MERGE_KEY=true`; new source columns appear locally when `SCHEMA_EVOLUTION=true`.
- **SC-009** (optional extended): With default flags, orphan local columns are not dropped; startup logs show `mode=merge` and opt-in flags false.

## Assumptions

- External Docker network `heavy-rental-network` is created before either stack starts.
- REST API devcontainer stack defines `postgres-primary` with database `heavy_rental` and network access for password auth (as in current REST API Compose).
- Cross-compose DNS uses **container name** `postgres-primary`, not the Compose service name `db-primary` from the other project.
- PostgreSQL major version for local DB matches primary (17).
- Tables intended for merge have primary keys (or unique constraints); tables without keys are skipped by default.
- Dev-only credentials (`postgres` / `postgres`) are acceptable for this repository’s local stacks.
- Haystack application code changes beyond connection environment variables are out of scope for the devcontainer feature unless already required by the app.
- Bidirectional sync, logical replication setup on primary, and production hardening are out of scope.
- Only the `public` schema is merged today; non-public multi-schema support is deferred.
- Full FK sync and auto column renames are out of scope for the current implementation.
