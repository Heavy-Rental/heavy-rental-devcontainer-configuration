# Design: Add Haystack Postgres merge sync

## Technical Approach

Introduce two Compose services beside `haystack-fast-api`:

1. **`db`** — standard PostgreSQL 17 primary (writable), persistent volume.
2. **`db-sync`** — `postgres:17` image used as a client+scheduler container running `sync-from-primary.sh`.

Merge uses **`postgres_fdw`** on the local database to import a staging schema from `postgres-primary`, then dynamic SQL upserts into local tables. This avoids wiping local data and preserves local-only keys.

## Architecture

```text
                    heavy-rental-network
         ┌──────────────────────────────────────┐
         │                                      │
  postgres-primary                      postgres-haystack (db)
  (REST API stack)  ◄── FDW / read ──   public schema (R/W)
         │                                      ▲
         │                                      │ upsert
         │                              postgres-haystack-sync
         │                              (db-sync loop)
         │                                      │
         └──────────────────────────────────────┘
                            ▲
                            │ JDBC/psycopg URL
                    haystack-fast-api
```

## Architecture Decisions

### Decision: Writable local primary, not streaming replica

Streaming hot standby is read-only. Product requires local writes.

### Decision: Merge upsert, not `pg_restore --clean`

Full replace removes local-only rows. Upsert by PK updates shared rows and inserts source-only rows without deleting local-only keys. Primary deletes are intentionally not mirrored.

### Decision: `postgres_fdw` for staging

- Re-import each cycle into `STAGING_SCHEMA` (default `primary_snapshot`).
- Generate `INSERT INTO public.t SELECT * FROM primary_snapshot.t ON CONFLICT DO UPDATE`.
- Fallback (if needed): `pg_dump`/`pg_restore` into staging schema.

### Decision: Separate `db-sync` service

Keeps client tools and halt lifecycle out of the app image. `restart: "no"` so halt does not thrash.

### Decision: Source hostname `postgres-primary`

Cross-compose DNS uses container names. Service name `db-primary` is not reliable from the Haystack project.

### Decision: Default halt on unavailable primary

Missing REST API stack should stop the sync job rather than appear as endless successful no-ops. Skip mode available via env.

## Data Flow (one cycle)

```text
1. pg_isready TARGET
2. pg_isready SOURCE (retries)
3. if fail → halt | skip+sleep
4. ensure FDW extension + server + user mapping
5. DROP SCHEMA staging CASCADE; CREATE; IMPORT FOREIGN SCHEMA
6. for each table with PK:
     INSERT ... ON CONFLICT (pk) DO UPDATE SET non_pk = EXCLUDED.non_pk
7. log summary
8. sleep SYNC_INTERVAL_SECONDS
```

## File Changes (planned)

| Path | Change |
|---|---|
| `Haystack-Fast-API/.devcontainer/docker-compose.yml` | Add `db`, `db-sync`, volume, app env, depends_on |
| `Haystack-Fast-API/.devcontainer/scripts/sync-from-primary.sh` | New scheduler/merge script |
| `Haystack-Fast-API/.devcontainer/scripts/merge_upsert.sql` | Optional SQL helpers |
| `Haystack-Fast-API/.devcontainer/devcontainer.json` | Optional port 5434 / connection profile |

## Configuration Surface

See Spec Kit contract: `specs/001-haystack-postgres-merge-sync/contracts/db-sync-env.md`.

Key defaults:

- `SYNC_INTERVAL_SECONDS=86400`
- `HALT_ON_PRIMARY_UNAVAILABLE=true`
- `SOURCE_HOST=postgres-primary`
- `TARGET_HOST=db`

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Schema drift | Re-import FDW; create missing tables before upsert when possible |
| Tables without PK | Skip + warn |
| Partial merge failure | Do not drop app schemas; abort cycle; next cycle retries |
| Primary never started | Halt default; local DB still usable |
| Port conflicts on host | Map `5434:5432` |

## Testing Strategy

Manual runtime verification per Spec Kit runbook:

**[specs/001-haystack-postgres-merge-sync/verification.md](../../../../specs/001-haystack-postgres-merge-sync/verification.md)**

Covers SC-001–SC-007:

1. Local write  
2. Merge with primary up  
3. Local-only retention  
4. Shared key primary wins  
5. Halt with primary down  
6. Default 24h schedule log  
7. Short interval double-cycle  

Entry point: `specs/001-haystack-postgres-merge-sync/quickstart.md` → links to the same runbook.

## Non-goals

- Promoting local DB to replace primary  
- Real-time replication lag SLAs  
- Encrypting dev passwords  
