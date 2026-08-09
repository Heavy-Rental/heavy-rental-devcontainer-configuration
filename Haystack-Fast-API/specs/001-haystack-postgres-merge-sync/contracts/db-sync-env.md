# Contract: `db-sync` operational interface

**Feature**: `001-haystack-postgres-merge-sync`  
**Consumer**: Compose service `db-sync` (and operators reading logs)  
**Provider**: `sync-from-primary.sh` (or equivalent)

## Purpose

Define the environment contract and observable behaviors for the merge-sync job so Compose, scripts, and operators stay aligned.

## Inputs (environment variables)

All values are strings in Compose; parsers MUST coerce integers/bools as documented.

| Name | Required | Default | Validation |
|---|---|---|---|
| `SOURCE_HOST` | no | `postgres-primary` | non-empty |
| `SOURCE_PORT` | no | `5432` | positive integer |
| `SOURCE_USER` | no | `postgres` | non-empty |
| `SOURCE_PASSWORD` | no | `postgres` | may be empty only if auth allows |
| `SOURCE_DB` | no | `heavy_rental` | non-empty |
| `TARGET_HOST` | no | `db` | non-empty |
| `TARGET_PORT` | no | `5432` | positive integer |
| `TARGET_USER` | no | `postgres` | non-empty |
| `TARGET_PASSWORD` | no | `postgres` | — |
| `TARGET_DB` | no | `heavy_rental` | non-empty |
| `STAGING_SCHEMA` | no | `primary_snapshot` | valid Postgres identifier |
| `SYNC_INTERVAL_SECONDS` | no | `86400` | integer ≥ 1 |
| `HALT_ON_PRIMARY_UNAVAILABLE` | no | `true` | `true` / `false` (case-insensitive) |
| `PRIMARY_CHECK_RETRIES` | no | `5` | integer ≥ 1 |
| `PRIMARY_CHECK_DELAY_SECONDS` | no | `3` | integer ≥ 0 |
| `SCHEMA_EVOLUTION` | no | `true` | `true` / `false` — ADD COLUMN for missing source columns |
| `ALLOW_UNIQUE_MERGE_KEY` | no | `true` | `true` / `false` — use UNIQUE when table has no PK |
| `SOURCE_SCHEMAS` | no | `public` | comma-list; **only `public` supported** in current script |
| `SYNC_MODE` | no | `merge` | `merge` \| `mirror` |
| `DROP_ORPHAN_COLUMNS` | no | `false` | drop local columns absent on primary (**data loss**) |
| `SYNC_INDEXES` | no | `false` | create non-unique secondary indexes from primary |
| `SYNC_UNIQUE_INDEXES` | no | `false` | create unique secondary indexes from primary |
| `SAFE_TYPE_WIDENINGS` | no | `false` | whitelisted type widenings only |
| `SYNC_FOREIGN_KEYS` | no | `false` | reserved; not implemented (logs WARN if true) |

## Policy matrix (default-on vs opt-in)

| Feature | Default | Notes |
|---|---|---|
| Create tables + ADD COLUMN | **ON** | Sandbox-safe |
| Unique-key merge | **ON** | Sandbox-safe |
| Multi-schema | `public` only | Non-public deferred |
| Drop orphan columns | **OFF** | Opt-in / mirror |
| Secondary indexes | **OFF** | Opt-in / mirror |
| Safe type widenings | **OFF** | Opt-in / mirror |
| Foreign keys | **OFF** | Not implemented yet |
| Auto renames | **OFF** | Not supported |

### `SYNC_MODE=mirror`

Forces: `DROP_ORPHAN_COLUMNS`, `SAFE_TYPE_WIDENINGS`, `SYNC_INDEXES`, `SYNC_UNIQUE_INDEXES`, `SYNC_FOREIGN_KEYS` = true.  
Use only when accepting loss of local-only columns and stricter parity.

## Merge key contract

1. Prefer source **primary key** columns.
2. Else if `ALLOW_UNIQUE_MERGE_KEY` is true: first usable **UNIQUE** constraint (fewest columns, then name), else unique non-partial non-expression index.
3. Else skip the table (log clearly).

## Schema evolution contract

When `SCHEMA_EVOLUTION` is true:

1. Create missing local tables from staging (`LIKE`).
2. For existing tables, **ADD COLUMN** for each source column not present locally (type from source `format_type`; NOT NULL without default → add nullable + warn).
3. By default MUST NOT drop or rename local columns; MUST NOT auto-change types.
4. If `SAFE_TYPE_WIDENINGS=true`, apply only whitelisted widenings (e.g. int→bigint, longer varchar).
5. If `DROP_ORPHAN_COLUMNS=true`, drop local columns missing on source (`RESTRICT`; WARN on failure).

## Connectivity check contract

**Success**: Source accepts a readiness probe (`pg_isready`) and optionally `SELECT 1` with provided credentials.

**Failure**: After `PRIMARY_CHECK_RETRIES` attempts spaced by `PRIMARY_CHECK_DELAY_SECONDS`, source is **unavailable**.

### On unavailable source

| `HALT_ON_PRIMARY_UNAVAILABLE` | Required behavior | Process exit | Local app tables |
|---|---|---|---|
| `true` | Log halt reason | Exit 0 (preferred) or non-zero; container SHOULD NOT restart-loop | Unchanged |
| `false` | Log skip; sleep `SYNC_INTERVAL_SECONDS`; continue loop | No exit | Unchanged |

## Merge contract (when source available)

1. Ensure local target is ready.
2. Ensure staging mechanism ready (FDW server/mapping or dump path).
3. Refresh staging view of source public schema (or configured schemas).
4. For each mergeable table with a primary key (or unique merge key):
   - `INSERT ... SELECT ... ON CONFLICT (merge_key) DO UPDATE SET ...` for non-key columns.
5. Do not `DELETE` local keys absent from source.
6. Skip tables without merge keys; log warning.
7. Log success summary (tables processed, skipped, errors).

### Failure mid-merge

- MUST NOT drop local application schemas as a recovery step.
- SHOULD abort remaining tables in the cycle after a hard error.
- Staging schema MAY be dropped/recreated next cycle.

## Scheduling contract

```text
on_start:
  wait_for_target()
  attempt_cycle()   # includes connectivity + optional merge
  loop:
    sleep(SYNC_INTERVAL_SECONDS)
    attempt_cycle()
```

- First attempt happens **before** the first full interval sleep.
- Default interval is **86400** seconds (24 hours).

## Logging contract (minimum)

Each cycle MUST emit human-readable logs including:

- Timestamp / cycle start
- Connectivity result (ok / fail after N retries)
- Decision: merge | skip | halt
- On merge: tables upserted / skipped / failed
- Cycle end status: success | skipped | halted | failed

## Network contract

| Endpoint | Direction | Port |
|---|---|---|
| `db-sync` → `TARGET_HOST` | TCP | `TARGET_PORT` |
| `db-sync` or `db` → `SOURCE_HOST` | TCP | `SOURCE_PORT` |

Both endpoints MUST be on Docker network `heavy-rental-network` (or equivalent shared network providing those DNS names).

## Non-goals (this contract)

- HTTP/gRPC API surface
- Metrics exposition format (Prometheus) — optional later
- Authentication beyond Postgres password env vars
