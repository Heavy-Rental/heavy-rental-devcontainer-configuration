# Tasks: Add Haystack Postgres merge sync

Implementation checklist for this OpenSpec change. Mirrors Spec Kit tasks in `specs/001-haystack-postgres-merge-sync/tasks.md` with a flatter structure.

## 1. Compose: local database

- [x] 1.1 Add volume `postgres-haystack-data`
- [x] 1.2 Add service `db` (Postgres 17, `postgres-haystack`, `heavy_rental`, healthcheck, `heavy-rental-network`, host port `5434`)
- [x] 1.3 Point `haystack-fast-api` at local `db` (`DATABASE_URL` or equivalent) and `depends_on` healthy `db`
- [ ] 1.4 Verify local read/write with `psql` — *after rebuild*

## 2. Sync script: core behavior

- [x] 2.1 Create `Haystack-Fast-API/.devcontainer/scripts/sync-from-primary.sh` with env defaults per contract
- [x] 2.2 Wait for target DB readiness
- [x] 2.3 Check source connectivity with retries
- [x] 2.4 Halt path when `HALT_ON_PRIMARY_UNAVAILABLE=true` and source down
- [x] 2.5 Skip + sleep path when halt is false and source down
- [x] 2.6 Implement FDW (or dump) staging into `STAGING_SCHEMA`
- [x] 2.7 Upsert merge by primary key; retain local-only rows; skip tables without keys
- [x] 2.8 Log cycle outcomes (ok / skip / halt / fail)

## 3. Compose: db-sync service

- [x] 3.1 Add `db-sync` service mounting the script
- [x] 3.2 Pass environment defaults (`SOURCE_HOST=postgres-primary`, interval `86400`, halt `true`)
- [x] 3.3 `depends_on` healthy `db`; network `heavy-rental-network`; `restart: "no"`

## 4. Scheduling

- [x] 4.1 Loop: attempt cycle → sleep `SYNC_INTERVAL_SECONDS` → repeat
- [x] 4.2 First attempt before first sleep
- [x] 4.3 Confirm default 24h interval

## 5. Devcontainer polish (optional)

- [x] 5.1 Forward port / VS Code Postgres profile for local DB
- [x] 5.2 Brief comment in Compose pointing to specs

## 6. Verification

Follow the full runbook:  
**[specs/001-haystack-postgres-merge-sync/verification.md](../../../../specs/001-haystack-postgres-merge-sync/verification.md)**

- [ ] 6.1 Primary up → merge brings rows (SC-002)
- [ ] 6.2 Local-only row survives merge (SC-003)
- [ ] 6.3 Shared key: primary wins (SC-004)
- [ ] 6.4 Primary down + halt → sync stops; local DB still R/W (SC-005)
- [ ] 6.5 Short interval → second cycle runs (SC-007)
- [ ] 6.6 Complete pass/fail checklist in `verification.md` (SC-001–SC-007)

## 7. Archive readiness (after implementation)

- [x] 7.1 Confirm delta specs match shipped behavior (implementation reviewed; known limitations documented in SoT)
- [x] 7.2 Archive change into `openspec/specs/haystack-devcontainer/spec.md` and `changes/archive/2026-08-08-add-haystack-postgres-merge-sync/`
