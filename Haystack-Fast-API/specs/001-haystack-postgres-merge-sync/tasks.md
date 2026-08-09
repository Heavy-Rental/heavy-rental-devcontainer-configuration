# Tasks: Haystack Postgres Merge Sync

**Input**: Design documents from `/specs/001-haystack-postgres-merge-sync/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/db-sync-env.md](./contracts/db-sync-env.md)

**Tests**: Manual verification per [verification.md](./verification.md) (automated tests not required for v1).  
**Code status**: Implemented. **Operator verification**: T007, T026, T028 remain open until runtime checks are run.

**Organization**: Tasks grouped by user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm layout and script directory

- [x] T001 Create `Haystack-Fast-API/.devcontainer/scripts/` directory
- [x] T002 [P] Add stub `Haystack-Fast-API/.devcontainer/scripts/sync-from-primary.sh` with `set -euo pipefail` and env default block per `contracts/db-sync-env.md`
- [x] T003 [P] Review existing `Haystack-Fast-API/.devcontainer/docker-compose.yml` and `devcontainer.json` for merge points

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Local writable Postgres available before sync logic

**⚠️ CRITICAL**: US2–US5 depend on this phase

- [x] T004 Add volume `postgres-haystack-data` to `Haystack-Fast-API/.devcontainer/docker-compose.yml`
- [x] T005 Add service `db` (`postgres:17`, container `postgres-haystack`, env for `heavy_rental`, healthcheck, network `heavy-rental-network`, ports `5434:5432`)
- [x] T006 Wire `haystack-fast-api` `depends_on: db` (service_healthy) and `DATABASE_URL` (or equivalent) to `postgresql://postgres:postgres@db:5432/heavy_rental`
- [ ] T007 Verify local R/W with `psql` against `postgres-haystack` (US1 smoke) — *run after rebuild*

**Checkpoint**: Local DB works without REST API stack

---

## Phase 3: User Story 1 - Local writable Postgres (Priority: P1) 🎯 MVP

**Goal**: Haystack has a durable, writable local database

**Independent Test**: Insert/select on local DB with app or `psql`

### Implementation for User Story 1

- [x] T008 [US1] Confirm app container resolves hostname `db` on `heavy-rental-network` (Compose wired)
- [x] T009 [US1] Optional: add `forwardPorts` / pgsql connection profile for local DB in `devcontainer.json`
- [x] T010 [US1] Document local connection string in comments or quickstart cross-link

**Checkpoint**: US1 complete without sync

---

## Phase 4: User Story 2 & 3 - Merge sync + halt/skip (Priority: P1)

**Goal**: Merge from primary when available; halt or skip when not

**Independent Test**: Quickstart merge + halt scenarios

### Implementation

- [x] T011 [US2] Implement local readiness wait (`pg_isready` on `TARGET_HOST`) in `sync-from-primary.sh`
- [x] T012 [US2] Implement source connectivity check with retries (`PRIMARY_CHECK_RETRIES` / `PRIMARY_CHECK_DELAY_SECONDS`)
- [x] T013 [US3] Implement halt vs skip branch for `HALT_ON_PRIMARY_UNAVAILABLE`
- [x] T014 [US2] Implement FDW setup on target (extension, server, user mapping) idempotently
- [x] T015 [US2] Implement staging schema refresh (`STAGING_SCHEMA` drop/create + `IMPORT FOREIGN SCHEMA` or dump fallback)
- [x] T016 [US2] Implement per-table merge-key detection (PK then unique) and `INSERT ... ON CONFLICT DO UPDATE` merge
- [x] T017 [US2] Skip tables without PK/unique merge key; log warnings
- [x] T018 [US2] Ensure merge does not delete local-only keys
- [x] T019 [US2][US3] Structured logging for merge success, skip, halt, failures
- [x] T020 [US2] Add Compose service `db-sync` mounting script, env defaults, `depends_on` healthy `db`, `restart: "no"`, network

**Checkpoint**: One successful merge with primary up; halt with primary down; local-only row retained

---

## Phase 5: User Story 4 - 24-hour schedule (Priority: P2)

**Goal**: Loop with first run at start, then interval sleep

**Independent Test**: Short interval override shows second cycle

### Implementation

- [x] T021 [US4] Wrap merge attempt in infinite loop with `sleep "${SYNC_INTERVAL_SECONDS}"` after each attempt (including skip)
- [x] T022 [US4] Ensure first attempt runs before first sleep
- [x] T023 [US4] Default `SYNC_INTERVAL_SECONDS=86400` in Compose env

**Checkpoint**: Two cycles observed with test interval (e.g. 60s)

---

## Phase 6: User Story 5 - Configurability (Priority: P3)

**Goal**: Interval and halt flag fully env-driven

### Implementation

- [x] T024 [US5] Document all env vars in script header and/or Compose comments
- [x] T025 [US5] Validate boolean parsing for `HALT_ON_PRIMARY_UNAVAILABLE` (`true`/`false`)
- [ ] T026 [US5] Smoke-test alternate `SYNC_INTERVAL_SECONDS` and halt flag values — *run after rebuild*

---

## Phase 7: Polish & Cross-Cutting

- [x] T027 [P] Align Spec Kit / OpenSpec docs with as-built behavior
- [ ] T028 [P] Run full [verification.md](./verification.md) checklist (SC-001–SC-007) — *operator after rebuild*
- [x] T029 Ensure failure mid-merge does not drop application schemas
- [x] T030 Schema-ensure: CREATE TABLE IF NOT EXISTS + ADD COLUMN (`SCHEMA_EVOLUTION`)

---

## Phase 8: Post-v1 enhancements (schema policy)

- [x] T031 Unique-key merge when no PK (`ALLOW_UNIQUE_MERGE_KEY`)
- [x] T032 Additive schema evolution defaults + contract
- [x] T033 Opt-in `DROP_ORPHAN_COLUMNS`, `SYNC_INDEXES`, `SYNC_UNIQUE_INDEXES`, `SAFE_TYPE_WIDENINGS`
- [x] T034 `SYNC_MODE=merge|mirror` mapping
- [x] T035 Spec Kit + OpenSpec docs aligned with as-built behavior
- [ ] T036 Multi-schema merge beyond `public` — *deferred*
- [ ] T037 FK sync (`SYNC_FOREIGN_KEYS` NOT VALID) — *deferred / flag reserved*
- [ ] T038 Column rename map — *deferred*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup** → **Foundational** → **US1** → **US2/US3** → **US4** → **US5** → **Polish**
- US4 builds on the single-cycle logic from US2/US3
- US5 is configuration polish on the same script

### Parallel Opportunities

- T002 and T003 in Setup
- Documentation tasks (T010, T024, T027) can parallel implementation when files differ

### MVP

Complete through **Phase 4** (local DB + one-shot merge loop with halt) for a viable demo; add US4 interval defaults if the loop is already present (T021–T023 should ship with Phase 4 if the script is already loop-based).

**Note**: Implementation may deliver T021 as part of Phase 4 since the designed process is inherently a loop; still verify SC-006 (24h default) explicitly.

---

## Implementation Strategy

1. Foundational `db` first so Haystack always has R/W storage  
2. Sync script next with halt-safe connectivity  
3. Confirm merge semantics (local-only retention) before relying on 24h cadence  
4. Lock defaults (86400, halt true) and document  

---

## Notes

- Do not use `pg_restore --clean` against the live app schema for merge under default mode  
- Source host must be `postgres-primary`, not `db-primary`  
- Keep REST API compose unchanged for FDW merge  
- Sandbox defaults: no drops/FKs/indexes/type changes unless opt-in or `SYNC_MODE=mirror`
