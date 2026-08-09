# Proposal: Add Haystack Postgres merge sync

## Intent

Haystack Fast API developers need a **local, writable PostgreSQL** database inside the Haystack devcontainer stack, while still being able to **pull shared domain data** from the Heavy Rental REST API primary database (`postgres-primary` / `heavy_rental`).

Sync must:

- Run on a **24-hour** cadence (plus an attempt at sync service start)
- **Merge** (upsert) rather than wipe, so **local-only rows are kept**
- **Halt** when `postgres-primary` cannot be detected (with a configurable skip alternative)

## Scope

### In scope

- Writable Postgres 17 service in `Haystack-Fast-API/.devcontainer/docker-compose.yml`
- Haystack app default connection to the local database
- `db-sync` long-running job + script implementing merge upsert
- Connectivity check, halt/skip policy, env configuration
- Spec Kit + OpenSpec documentation for the change

### Out of scope

- Physical streaming replication (read-only standby)
- Bidirectional sync or conflict UI
- Logical replication publication changes on REST API primary (not required for FDW/dump merge)
- Production secret management / HA
- Haystack application feature code beyond connection environment variables

## Approach

1. Add Compose service `db` (`postgres-haystack`) on `heavy-rental-network`.
2. Point the app at `db` for all R/W.
3. Add `db-sync` that:
   - waits for local DB
   - probes `postgres-primary`
   - on failure: halt (default) or skip+sleep
   - on success: load source snapshot (prefer `postgres_fdw`) and **UPSERT** by primary key
   - sleeps `SYNC_INTERVAL_SECONDS` (default 86400) and repeats
4. Keep REST API stack as the source of truth for shared keys; local DB is a sandbox that can diverge with local-only rows.

## Rationale

- Streaming replica cannot satisfy local writes.
- Full dump/restore with `--clean` violates local-only retention.
- Shared external network already connects both projects; container DNS `postgres-primary` is the correct source host.

## Related artifacts

- Spec Kit feature: `specs/001-haystack-postgres-merge-sync/`
- Delta specs: `openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/specs/`
- Design: `design.md`
- Tasks: `tasks.md`
- Archived: 2026-08-08 into `openspec/specs/haystack-devcontainer/spec.md`
