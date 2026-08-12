# Data Model: Haystack Postgres Merge Sync

**Feature**: `001-haystack-postgres-merge-sync`  
**Status**: As-built (matches implementation)

This feature does not introduce a new application domain model. It manages **database instances**, **sync configuration**, and **merge rules** over the existing `heavy_rental` database owned by the REST API primary.

## Entities

### 1. Source Database Instance

| Attribute | Description |
|---|---|
| Identity | Docker container `postgres-primary` on `heavy-rental-network` |
| Engine | PostgreSQL 17 |
| Database name | `heavy_rental` |
| Schema scope (current) | `public` only |
| Role in feature | Authoritative source for shared rows during merge |
| Owned by | Heavy-Rental-REST-API Compose stack |

### 2. Local Database Instance

| Attribute | Description |
|---|---|
| Identity | Compose service `postgres-haystack`, container name `postgres-haystack` |
| Image | `pgvector/pgvector:pg17` (Postgres 17 + pgvector; Phase 5 T5/D4 — see `004`) |
| Engine | PostgreSQL 17 |
| Database name | `heavy_rental` |
| Volume | `postgres-haystack-data` (persistent across container recreate) |
| Host port | `5434:5432` (avoids REST API 5432/5433) |
| Role in feature | Writable store for Haystack app; merge target |
| Owned by | Haystack-Fast-API Compose stack |

### 3. Application Connection

| Attribute | Description |
|---|---|
| Consumer | `haystack-fast-api` service |
| Target | Local `postgres-haystack` service (in-compose DNS name `postgres-haystack`) |
| Example URL | `postgresql://postgres:postgres@postgres-haystack:5432/heavy_rental` |
| Privileges | Full read/write on local database |

### 4. Sync Job

| Attribute | Description |
|---|---|
| Identity | Compose service `postgres-haystack-sync`, container `postgres-haystack-sync` |
| Image | `postgres:17` (client tools + script) |
| Script | `.devcontainer/scripts/sync-from-primary.sh` |
| Lifecycle | Long-running loop until halt exit or container stop (`restart: unless-stopped` by default) |
| Dependencies | Local `postgres-haystack` healthy; source optional (checked each cycle) |
| Side effects | FDW staging; upserts; optional ADD/DROP COLUMN; optional indexes; logs |

### 5. Sync Configuration (environment)

| Key | Default | Meaning |
|---|---|---|
| `SOURCE_HOST` | `postgres-primary` | Primary hostname |
| `SOURCE_PORT` | `5432` | Primary port |
| `SOURCE_USER` | `postgres` | Source user |
| `SOURCE_PASSWORD` | `postgres` | Source password |
| `SOURCE_DB` | `heavy_rental` | Source database |
| `TARGET_HOST` | `postgres-haystack` | Local DB hostname from sync container |
| `TARGET_PORT` | `5432` | Local DB port |
| `TARGET_USER` | `postgres` | Local user |
| `TARGET_PASSWORD` | `postgres` | Local password |
| `TARGET_DB` | `heavy_rental` | Local database |
| `STAGING_SCHEMA` | `primary_snapshot` | FDW import staging schema name |
| `SYNC_INTERVAL_SECONDS` | `60` | Sleep between cycles after each attempt (near-RT poll) |
| `HALT_ON_PRIMARY_UNAVAILABLE` | `false` | Halt vs skip (default skip) |
| `PRIMARY_CHECK_RETRIES` | `5` | Connectivity retries |
| `PRIMARY_CHECK_DELAY_SECONDS` | `3` | Delay between retries |
| `SCHEMA_EVOLUTION` | `true` | CREATE missing tables + ADD COLUMN |
| `ALLOW_UNIQUE_MERGE_KEY` | `true` | Use UNIQUE when no PK |
| `SOURCE_SCHEMAS` | `public` | Documented; only `public` supported today |
| `SYNC_MODE` | `merge` | `merge` or `mirror` |
| `DROP_ORPHAN_COLUMNS` | `false` | Drop local cols missing on primary |
| `SYNC_INDEXES` | `false` | Non-unique secondary indexes |
| `SYNC_UNIQUE_INDEXES` | `false` | Unique secondary indexes |
| `SAFE_TYPE_WIDENINGS` | `false` | Whitelisted type widenings |
| `SYNC_FOREIGN_KEYS` | `false` | Reserved; not implemented |
| `SYNC_TABLE_ALLOWLIST` | `asset,booking,category` | Phase 4 T2 deterministic fleet tables; `all`/`*` = full public |

See full contract: [contracts/db-sync-env.md](./contracts/db-sync-env.md).  
D0 domain inventory: [contracts/schema-contract.md](./contracts/schema-contract.md).

### 6. Merge Key (per table)

| Attribute | Description |
|---|---|
| Kind | `pk` or `unique` |
| Selection | Prefer PK; else first usable UNIQUE (fewest columns, then name); else unique non-partial index |
| Usage | `ON CONFLICT (merge_key) DO UPDATE` |
| Missing key | Table skipped; warning logged |
| Local ensure | ADD PRIMARY KEY or ADD UNIQUE if missing |

### 7. Schema evolution effects

| Mode | Effect |
|---|---|
| Default (`SCHEMA_EVOLUTION=true`) | CREATE TABLE IF NOT EXISTS; ADD COLUMN for source-only cols |
| `DROP_ORPHAN_COLUMNS=true` | DROP local columns not on source |
| `SAFE_TYPE_WIDENINGS=true` | e.g. int→bigint, longer varchar |
| `SYNC_INDEXES` / `SYNC_UNIQUE_INDEXES` | CREATE missing secondary indexes (best-effort) |

### 8. Table allowlist (Phase 4 T2)

| Attribute | Description |
|---|---|
| Default | `asset`, `booking`, `category` (D0 schema contract v1.0) |
| Mode all | `SYNC_TABLE_ALLOWLIST=all` or `*` |
| Effect | FDW `LIMIT TO` when finite; non-listed public tables skipped |

### 9. Cycle metrics (Phase 4 T1, logged)

| Field | Description |
|---|---|
| `duration_ms` | Wall-clock cycle duration |
| `interval_seconds` | Configured poll interval |
| `expected_max_lag_seconds` | ≈ poll interval (not CDC) |
| allowlist counts | `merged`, `skipped_no_key`, `skipped_not_allowlisted`, `failed` |

### 10. Row Classification (runtime, not stored)

| Class | Definition | Merge action |
|---|---|---|
| Shared row | Merge key exists on source and target | Update target from source |
| Source-only row | Merge key on source only | Insert into target |
| Local-only row | Merge key on target only | **No change** (retain) under merge mode |
| Source-deleted | Key gone on source | **No delete** on target |

## Relationships

```text
[Sync Configuration] --configures--> [Sync Job]
[Sync Job] --reads--> [Source Database Instance]
[Sync Job] --upserts / evolves--> [Local Database Instance]
[Haystack App] --R/W--> [Local Database Instance]
```

## State transitions (Sync Job)

```text
START → apply_sync_mode
  → wait for local db ready
  → check source connectivity
       ├─ unavailable + halt → HALTED (terminal)
       ├─ unavailable + skip → SLEEP → (loop)
       └─ available → MERGE (FDW + evolve + upsert + optional indexes) → SLEEP → (loop)
```
