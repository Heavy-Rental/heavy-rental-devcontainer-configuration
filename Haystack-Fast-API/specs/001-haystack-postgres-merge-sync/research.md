# Research: Haystack Postgres Merge Sync

**Feature**: `001-haystack-postgres-merge-sync`  
**Date**: 2026-08-08

## 1. Local database vs connect-only vs streaming replica

| Option | Writable local? | Continuous sync? | Complexity |
|---|---|---|---|
| A. Connect Haystack to `postgres-primary` only | No local sandbox | N/A (live) | Lowest |
| B. Physical streaming replica in Haystack | **No** (hot standby) | Yes | Medium |
| C. Writable local DB + periodic merge | **Yes** | Periodic | Medium |

**Decision**: Option C — matches requirement for local R/W and retention of local-only rows.

**Rejected**:
- A: no local DB service in Haystack devcontainer.
- B: read-only; cannot satisfy local write requirement.

## 2. Merge semantics vs full replace

| Strategy | Local-only rows | Shared keys | Primary deletes |
|---|---|---|---|
| `pg_restore --clean` / truncate+reload | **Removed** | Replaced | Mirrored |
| Upsert merge (PK) | **Kept** | Primary wins | **Not mirrored** |
| Logical replication | Local-only tables OK; same-table writes conflict | Applied as deltas | Usually mirrored |

**Decision**: Upsert merge on primary key (or unique constraint). Primary wins on conflict. Do not delete local keys missing on primary.

**Rationale**: User explicitly chose merge/upsert and local-only row retention.

## 3. Transport for source data

| Approach | Pros | Cons |
|---|---|---|
| `postgres_fdw` + `IMPORT FOREIGN SCHEMA` | Live read of primary; no dump files; clean staging schema | Requires extension on local DB; network from local DB → primary |
| `pg_dump` / `pg_restore` into staging schema | No FDW; familiar tools | Schema mapping, dump size, restore flags |
| Per-table `COPY` over `psql` | Simple for few tables | Poor for unknown/evolving schemas |

**Decision**: Prefer **`postgres_fdw`** on the local database with a disposable staging schema (e.g. `primary_snapshot`), then generate `INSERT ... ON CONFLICT DO UPDATE` per table with a PK. Fallback path: dump/restore into staging if FDW is blocked.

## 4. Scheduling model

| Approach | Pros | Cons |
|---|---|---|
| Host cron | Familiar | Not portable inside Compose-only workflow |
| `postStartCommand` only | Simple | No continuous loop |
| Long-running `postgres-haystack-sync` container loop | Portable; same network; env-configurable | Must design halt/restart carefully |

**Decision**: Always-on **`postgres-haystack-sync`** service: check → merge → sleep `SYNC_INTERVAL_SECONDS` (default **60** for near-RT poll per Feasibility_Study §11 T1; not CDC). First merge attempt at startup after local DB is healthy.

## 5. Halt vs skip when primary unavailable

| Mode | Behavior |
|---|---|
| Halt (`HALT_ON_PRIMARY_UNAVAILABLE=true`) | Log error; do not modify app tables; exit process (stop scheduling) |
| Skip (`false`) | Log warning; sleep interval; retry |

**Decision**: Support both; **default halt = false** (skip+sleep) so near-RT sync keeps retrying when the REST API stack is temporarily down, without exit/restart storms. Operators MAY set `HALT_ON_PRIMARY_UNAVAILABLE=true` for fail-fast. Local `postgres-haystack` and app continue running either way.

**Restart policy**: Prefer `restart: unless-stopped` with **skip** default. If using halt mode, set `restart: "no"` (or accept restart loops) so halt does not thrash.

## 6. Cross-project networking

- Both stacks already declare external network `heavy-rental-network`.
- REST API primary **container_name**: `postgres-primary`.
- Compose service name `db-primary` is **not** a reliable DNS name from the Haystack project.
- **Decision**: `SOURCE_HOST=postgres-primary`.

## 7. Version and ports

- Match primary image major version: **Postgres 17**.
- Host ports: primary `5432`, existing replica `5433` → local Haystack DB **`5434:5432`**.

## 8. Tables without primary keys

**Decision (updated)**: Prefer **PK**; else use a usable **UNIQUE** constraint/index when `ALLOW_UNIQUE_MERGE_KEY=true` (default). Skip only if neither exists. Truncate+reload for keyless tables remains out of scope.

## 9. Open questions resolved by product decisions

| Question | Resolution |
|---|---|
| Replace or merge? | Merge |
| Interval? | 60s default (near-RT poll; override for lighter load) |
| Halt if primary missing? | Configurable; default **skip** (near-RT); halt opt-in |
| Writable local? | Yes |
| Unique without PK? | Yes (default on) |
| Schema evolution? | Additive by default (ADD COLUMN / CREATE TABLE) |
| Column drops / FKs / full type changes? | Opt-in or deferred; not default |

## 10. Risks

| Risk | Mitigation |
|---|---|
| Schema drift (new columns/tables on primary) | `SCHEMA_EVOLUTION`: CREATE + ADD COLUMN; re-import FDW each cycle |
| Local-only data loss | Default merge mode; drops/indexes only via explicit flags or `SYNC_MODE=mirror` |
| Large tables / long merge | Accept for local dev; log duration; no production SLA |
| Partial failure mid-upsert | Abort remaining tables; do not drop app schemas; staging disposable |
| Credential mismatch | Align dev defaults with REST API stack documentation |

## 11. Post-v1 decisions (as-built)

### Unique-key merge

**Decision**: Implemented. PK first; else first usable UNIQUE (fewest columns, then name).

### Additive vs destructive schema evolution

**Decision**: Default **additive only**. Opt-in:

| Flag | Default | Purpose |
|---|---|---|
| `DROP_ORPHAN_COLUMNS` | false | Drop local cols missing on primary |
| `SYNC_INDEXES` / `SYNC_UNIQUE_INDEXES` | false | Secondary indexes |
| `SAFE_TYPE_WIDENINGS` | false | Whitelisted widenings only |
| `SYNC_MODE=mirror` | merge | Bundle enabling the above (+ FK flag) |

### Multi-schema

**Decision**: Deferred. `SOURCE_SCHEMAS` defaults to `public`; non-public ignored with WARN.

### Foreign keys

**Decision**: Deferred. `SYNC_FOREIGN_KEYS=true` logs WARN; no constraint creation yet.

### Why not full mirror by default

Local sandbox requires retaining local-only rows/columns. Full dump/restore or validated FKs fight that model. Use `SYNC_MODE=mirror` only when parity matters more than sandbox data.
