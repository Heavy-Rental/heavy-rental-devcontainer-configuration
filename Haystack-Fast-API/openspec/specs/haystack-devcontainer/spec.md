# Haystack Devcontainer Specification

## Purpose

Behavior of the **Haystack Fast API** development container stack as configured in this repository (`Haystack-Fast-API/.devcontainer`). This is the OpenSpec **source of truth** for current agreed behavior.

The stack includes a **writable local PostgreSQL** database and a **merge-sync** job that periodically upserts data from the REST API primary (`postgres-primary` / `heavy_rental`).

**Default policy (sandbox merge):** additive schema evolution, PK or unique merge keys, retain local-only rows/columns, **skip** merge cycles if primary unreachable (retry after interval), **near-real-time poll** default **60s** (`SYNC_INTERVAL_SECONDS`; not CDC). **Table allowlist** default **`asset,booking,category`** (`SYNC_TABLE_ALLOWLIST`; Phase 4 T2 / D0); use `all` or `*` for full public merge. Cycle logs include **lag/duration metrics** (`duration_ms`, `expected_max_lag_seconds`). **Opt-in parity** flags and `SYNC_MODE=mirror` can enable drops, secondary indexes, and safe type widenings (see requirements below). Only the **`public`** schema is merged today. Set `HALT_ON_PRIMARY_UNAVAILABLE=true` to stop the job process when primary is down.

**Neo4j:** local Community 5 instance for Haystack DocumentStore (`neo4j-haystack`), complementary to Postgres. Devcontainer installs the **Neo4j for VS Code** extension (`neo4j-extensions.neo4j-for-vscode`) for Cypher/Bolt in the IDE (Browser remains on port 7474). IDE connections are UI-managed (not a `pgsql.connections`-style settings array).

**Pgvector (Phase 5 T5 / D4):** local Postgres uses image **`pgvector/pgvector:pg17`** with extension **`vector`** on `heavy_rental` (initdb + healthcheck ensure). App env documents **`INDEXING_EMBEDDING_DIM=768`** for future DocumentStore cutover. **I0/I1** (factory + pipeline writer) remain application work — not required for this platform requirement.

**FAISS:** not part of the default stack (env and postCreate install removed). Spec Kit `003` retained as historical only.

Change history:
- `openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/`
- `openspec/changes/archive/2026-08-08-add-haystack-neo4j/`
- `openspec/changes/archive/2026-08-09-add-haystack-faiss/` (later removed from default stack)
- `openspec/changes/archive/2026-08-09-add-neo4j-vscode-extension/`
- `openspec/changes/archive/2026-08-09-document-neo4j-vscode-ui-connections/`
- 2026-08-10: Feasibility_Study §11 **T1** — near-RT default `SYNC_INTERVAL_SECONDS=60`, skip-by-default when primary down, `restart: unless-stopped`; service names `postgres-haystack` / `postgres-haystack-sync`
- 2026-08-10: **FAISS removed** from compose env and `postCreateCommand` (no longer SoT)
- 2026-08-12: Phase 4 / S4 — `SYNC_TABLE_ALLOWLIST` (T2), cycle lag `METRICS` (T1), D0 schema-contract.md; archive `2026-08-12-phase4-fleet-mirror-allowlist-d0`
- 2026-08-12: Phase 5 Step 5.1 — T5 / D4 pgvector platform ready; archive `2026-08-12-phase5-t5-d4-pgvector-platform`

Spec Kit (active): `specs/001-haystack-postgres-merge-sync/`, `specs/002-haystack-neo4j/`, `specs/004-haystack-pgvector/`. Historical: `specs/003-haystack-faiss/`.

## Requirements

### Requirement: Devcontainer Compose stack

The Haystack Fast API development environment MUST start via Docker Compose using `Haystack-Fast-API/.devcontainer/docker-compose.yml`, attach to the external network `heavy-rental-network`, and include the application service, local Postgres (`postgres-haystack` / `postgres-haystack-sync`), and Neo4j services.

#### Scenario: Stack services

- **GIVEN** this configuration is deployed
- **WHEN** a developer inspects Compose services
- **THEN** `haystack-fast-api`, `postgres-haystack`, `postgres-haystack-sync`, and `neo4j` are defined
- **AND** all join `heavy-rental-network`

#### Scenario: App service joins shared network

- **GIVEN** the external network `heavy-rental-network` exists
- **WHEN** the Haystack Compose stack is started
- **THEN** the `haystack-fast-api` service is attached to `heavy-rental-network`

### Requirement: Workspace ownership on create

The devcontainer MUST run a post-create command that ensures the workspace directory is owned by the non-root `vscode` user and MAY install developer tooling (e.g. `uv`) on container create/rebuild.

#### Scenario: Rebuild installs tooling

- **GIVEN** a new or rebuilt Haystack devcontainer
- **WHEN** `postCreateCommand` completes
- **THEN** workspace ownership is corrected for `vscode` and configured install steps have run

### Requirement: Neo4j graph store for Haystack

The Haystack Compose stack MUST include a Neo4j 5 Community service on `heavy-rental-network` with a persistent volume, host-mapped Bolt (7687) and HTTP Browser (7474) ports, and documented dev authentication. The application service MUST expose `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` for neo4j-haystack / driver clients. Neo4j MUST NOT replace Postgres as the relational domain store.

#### Scenario: Neo4j service present

- **GIVEN** the Haystack stack is started
- **WHEN** services are inspected
- **THEN** a healthy `neo4j` service (`neo4j-haystack`) exists alongside Postgres services

#### Scenario: App connection env for Neo4j

- **GIVEN** the app container is running
- **WHEN** environment variables are read
- **THEN** `NEO4J_URI` is `bolt://neo4j:7687` and credentials match Neo4j service auth

### Requirement: Neo4j VS Code extension

The Haystack Fast API `devcontainer.json` MUST list the official Neo4j for VS Code extension (`neo4j-extensions.neo4j-for-vscode`) under `customizations.vscode.extensions` so developers get Cypher/Bolt tooling in the IDE. Neo4j Browser on port 7474 remains available and is NOT replaced by the extension.

Unlike Postgres (`pgsql.connections`), this extension does **not** support preconfigured connection profiles in workspace/`devcontainer.json` settings. Connections are created in the extension UI (sidebar / Command Palette) and stored in extension global state and SecretStorage. Spec Kit docs MUST document the recommended **Haystack Local Neo4j** connection parameters for use inside the container (`bolt` / host `neo4j` / port `7687` / user `neo4j` / password `heavyrental` / database `neo4j`).

The devcontainer MAY set only the extension’s supported settings keys (e.g. `neo4j.features.linting`, `neo4j.trace.server`). It MUST NOT invent a settings array such as `neo4j.connections` that the extension ignores.

#### Scenario: Extension configured for install

- **GIVEN** `Haystack-Fast-API/.devcontainer/devcontainer.json`
- **WHEN** a developer inspects `customizations.vscode.extensions`
- **THEN** `neo4j-extensions.neo4j-for-vscode` is present (alongside the Postgres extension)

#### Scenario: Connection is UI-managed, not settings profiles

- **GIVEN** the official Neo4j for VS Code extension
- **WHEN** a developer looks for a `pgsql.connections`-style settings array for Neo4j
- **THEN** no such supported key exists; they MUST use **Neo4j: Create new connection** (or the Connections pane) with the documented Haystack values

### Requirement: Local writable database

The Haystack Compose stack MUST provide a local PostgreSQL 17 service that is fully writable and persists data in a dedicated Docker volume. The Haystack application service MUST use this local database as its default **relational** read/write data source. Graph DocumentStore MAY use Neo4j. Durable project-chunk vectors target **pgvector on this same local Postgres** (platform ready; app I0/I1 cutover separate).

#### Scenario: Local database accepts writes

- **GIVEN** the Haystack stack is running and the local database service is healthy
- **WHEN** a client connects with the configured local credentials to database `heavy_rental`
- **THEN** the client can insert, update, select, and delete rows
- **AND** the instance is not a read-only standby (`pg_is_in_recovery()` is false)

#### Scenario: Application uses local database

- **GIVEN** the `haystack-fast-api` service is configured via environment
- **WHEN** the application opens its default database connection
- **THEN** it connects to the local Compose database service (not `postgres-primary`)

### Requirement: Pgvector platform on local Postgres (Phase 5 T5 / D4)

The local Postgres service (`postgres-haystack`) MUST use a PostgreSQL 17 image that includes **pgvector** (default: `pgvector/pgvector:pg17`). Database `heavy_rental` MUST have extension **`vector`** available when the service is healthy (bootstrap via initdb for fresh volumes; idempotent ensure for upgraded volumes). The application service MUST expose **`INDEXING_EMBEDDING_DIM`** (default **768**) as the platform embedding-dimension contract for a future `PgvectorDocumentStore` cutover.

This requirement is **platform-only**: the stack MUST NOT require application DocumentStore factory wiring (`INDEXING_DOCUMENT_STORE`), indexing pipeline writers, document tables, or tenant isolation tests (I0/I1 and later). REST API `postgres-primary` MUST NOT be required to install pgvector.

#### Scenario: Vector extension present

- **GIVEN** `postgres-haystack` is healthy
- **WHEN** an operator queries `pg_extension` for `vector` on `heavy_rental`
- **THEN** the extension is present

#### Scenario: Embedding dim contract on app env

- **GIVEN** the `haystack-fast-api` service is running
- **WHEN** environment variables are read
- **THEN** `INDEXING_EMBEDDING_DIM` is set (default `768`)

#### Scenario: Platform does not force DocumentStore cutover

- **GIVEN** only this platform requirement is satisfied
- **WHEN** an operator inspects Compose
- **THEN** no app-owned document vector tables are required to exist yet

### Requirement: Shared network reachability to REST API primary

The local database and sync components MUST join external network `heavy-rental-network` so they can reach container `postgres-primary` when the REST API stack is running.

#### Scenario: Source host resolution

- **GIVEN** both stacks are attached to `heavy-rental-network` and primary is running
- **WHEN** the sync process resolves `postgres-primary`
- **THEN** a TCP connection to port 5432 succeeds for connectivity checks

### Requirement: Merge sync from REST API primary

The system MUST provide a sync process that merge-refreshes data from `postgres-primary` database `heavy_rental` into the local database using upserts. The merge key MUST be the table **primary key** when present; otherwise a usable **unique** constraint (or unique non-partial index) when unique-key merge is enabled. Primary MUST win on key conflicts. Local-only rows MUST be retained. Default behavior MUST NOT wipe local application tables.

#### Scenario: Source rows appear locally

- **GIVEN** primary is reachable and contains rows in mergeable tables
- **WHEN** a successful sync cycle completes
- **THEN** those rows are present locally (inserted if new, updated if same merge key)

#### Scenario: Local-only rows retained

- **GIVEN** a row exists only on the local database for a merge key not present on primary
- **WHEN** a successful sync cycle completes
- **THEN** that row still exists locally

#### Scenario: Shared key primary wins

- **GIVEN** the same merge key exists on primary and local with different non-key values
- **WHEN** a successful sync cycle completes
- **THEN** local non-key values match primary

#### Scenario: Primary deletes not mirrored

- **GIVEN** a row was removed on primary but still exists locally
- **WHEN** a successful sync cycle completes
- **THEN** the local row is not required to be deleted

#### Scenario: Unique-key merge without primary key

- **GIVEN** a source table has no primary key but has a unique constraint on one or more columns
- **WHEN** a successful sync cycle completes with unique-key merge enabled
- **THEN** the table is merged using that unique key (not skipped solely for lack of a PK)

### Requirement: Additive schema evolution

When schema evolution is enabled (default), the sync process MUST create missing local tables from source and MUST **add** columns that exist on the source but not on an existing local table before upserting. Under default merge mode the process MUST NOT drop local columns, rename columns, or apply non-whitelisted type changes. Opt-in flags may enable drops or safe type widenings.

#### Scenario: New column on primary is added locally

- **GIVEN** a local table already exists and primary adds a new column with data
- **WHEN** a successful sync cycle completes with schema evolution enabled
- **THEN** the local table has the new column and upserted rows include source values for that column

#### Scenario: Local-only columns retained

- **GIVEN** a local table has a column that does not exist on primary
- **WHEN** a successful sync cycle completes with default merge mode (`DROP_ORPHAN_COLUMNS` false)
- **THEN** the local-only column remains

### Requirement: Opt-in schema parity flags

The sync process MUST support opt-in flags that are **off by default** so sandbox merge remains safe:

- `DROP_ORPHAN_COLUMNS` — drop local columns absent on primary (data loss)
- `SYNC_INDEXES` / `SYNC_UNIQUE_INDEXES` — create secondary indexes from primary
- `SAFE_TYPE_WIDENINGS` — apply only whitelisted type widenings
- `SYNC_FOREIGN_KEYS` — reserved; when true, implementation MUST log that FK sync is not available until implemented
- `SOURCE_SCHEMAS` — documented; current implementation supports **`public` only**
- `SYNC_MODE=mirror` — enables drop, type widen, index, and FK flags (FK still not implemented)

#### Scenario: Default merge does not drop local columns

- **GIVEN** default configuration (`SYNC_MODE=merge`, `DROP_ORPHAN_COLUMNS=false`)
- **WHEN** primary no longer has a column that still exists locally
- **THEN** the local column is not dropped

#### Scenario: Opt-in index sync

- **GIVEN** `SYNC_INDEXES=true` and primary has a non-unique secondary index
- **WHEN** a successful sync cycle completes
- **THEN** the index is created on the local table if missing (best-effort; failures logged)

#### Scenario: Mirror mode enables parity flags

- **GIVEN** `SYNC_MODE=mirror`
- **WHEN** the sync process starts
- **THEN** drop-orphan, safe type widenings, and index sync flags are treated as enabled (FK flag may be set but FK creation remains unimplemented)

### Requirement: Connectivity check before merge

Before modifying local application data, the sync process MUST detect whether `postgres-primary` is available, with configurable retries.

#### Scenario: Successful detection

- **GIVEN** primary accepts connections with configured credentials
- **WHEN** the sync process runs its connectivity check
- **THEN** the check succeeds and a merge cycle may proceed

#### Scenario: Failed detection after retries

- **GIVEN** primary is stopped or unreachable
- **WHEN** retries are exhausted
- **THEN** the process treats the source as unavailable and MUST NOT merge application tables in that cycle

### Requirement: Halt on primary unavailability

When the source is unavailable and halt mode is enabled (`HALT_ON_PRIMARY_UNAVAILABLE=true`), the sync process MUST leave local application data unchanged and MUST stop further scheduled merges for that process lifetime. Halt is **opt-in**; the Compose default is skip mode (see skip requirement).

#### Scenario: Explicit halt

- **GIVEN** `HALT_ON_PRIMARY_UNAVAILABLE` is true and primary cannot be detected
- **WHEN** the sync process evaluates connectivity
- **THEN** it logs a halt condition
- **AND** it does not modify local application tables
- **AND** the sync job stops scheduling further cycles

#### Scenario: Local database remains usable after halt

- **GIVEN** the sync job has halted
- **WHEN** the developer uses the Haystack app or `psql` against the local database
- **THEN** read and write operations still succeed

### Requirement: Skip cycle when primary unavailable (default)

When the source is unavailable and halt mode is disabled (default), the sync process MUST skip the merge, leave local data intact, wait for the configured interval, and retry. The Compose service SHOULD use `restart: unless-stopped` so the long-running loop survives container engine restarts without pairing halt+restart storms.

#### Scenario: Default skip and wait

- **GIVEN** `HALT_ON_PRIMARY_UNAVAILABLE` is false (default) and primary cannot be detected
- **WHEN** the sync process evaluates connectivity
- **THEN** it logs a skip
- **AND** it sleeps for `SYNC_INTERVAL_SECONDS`
- **AND** it attempts another cycle afterward

### Requirement: Near-real-time scheduled refresh

The sync process MUST attempt a merge cycle when it starts (after local DB readiness) and MUST wait **60 seconds** by default between subsequent attempts (near-real-time **poll**, not CDC/logical replication). The interval MUST be overridable via `SYNC_INTERVAL_SECONDS` (e.g. `300` or `86400` for lighter load).

#### Scenario: Initial attempt at start

- **GIVEN** the sync service starts and the local database is ready
- **WHEN** initialization completes
- **THEN** the process attempts a connectivity check and merge (or halt/skip) before the first full interval sleep

#### Scenario: Default interval

- **GIVEN** default configuration
- **WHEN** a cycle attempt finishes
- **THEN** the next attempt is scheduled after 60 seconds

#### Scenario: Custom interval

- **GIVEN** `SYNC_INTERVAL_SECONDS` is set to a positive integer N
- **WHEN** a cycle attempt finishes
- **THEN** the next attempt is scheduled after N seconds

### Requirement: Operational logging

The sync process MUST log cycle outcomes including connectivity result, halt, skip, merge success/failure, and tables skipped (e.g. missing primary key or not on allowlist).

#### Scenario: Operator can diagnose halt

- **GIVEN** primary is unavailable and halt mode is enabled
- **WHEN** the operator reads sync container logs
- **THEN** the logs clearly state that primary could not be detected and that the job is halting

### Requirement: Deterministic fleet table allowlist (Phase 4 T2)

The sync process MUST default to merging only tables listed in `SYNC_TABLE_ALLOWLIST` (default `asset,booking,category` per D0 schema contract). Values `all` or `*` MUST enable full `public` schema merge. Non-allowlisted tables MUST be skipped (and SHOULD be excluded from FDW import via `LIMIT TO` when the list is finite).

#### Scenario: Default allowlist merges fleet tables only

- **GIVEN** default `SYNC_TABLE_ALLOWLIST=asset,booking,category`
- **WHEN** a successful sync cycle completes
- **THEN** only allowlisted, mergeable tables are required to be merged
- **AND** other public tables are not required to appear or update locally

#### Scenario: Full public override

- **GIVEN** `SYNC_TABLE_ALLOWLIST` is `all` or `*`
- **WHEN** the sync process runs
- **THEN** all mergeable public tables are eligible for merge

### Requirement: Cycle lag and duration metrics (Phase 4 T1)

Each sync cycle MUST log wall-clock duration (`duration_ms`) and a poll-based lag expectation (`expected_max_lag_seconds` approximately equal to `SYNC_INTERVAL_SECONDS`). Merge cycles SHOULD log allowlist-related counts (`merged`, `skipped_not_allowlisted`, etc.). Prometheus exposition is not required.

#### Scenario: Metrics line after cycle

- **GIVEN** a sync cycle completes (success, skip, fail, or halt)
- **WHEN** the operator reads sync container logs
- **THEN** a metrics line includes `duration_ms` and interval / expected lag fields

### Requirement: D0 schema contract published

Spec Kit MUST publish a versioned fleet domain schema contract (`specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`) that binds default allowlist tables to the REST API producer contract.

#### Scenario: Contract present

- **GIVEN** a checkout of this repository
- **WHEN** an operator opens the Haystack merge-sync contracts folder
- **THEN** `schema-contract.md` exists at version 1.0 and documents default allowlist tables
