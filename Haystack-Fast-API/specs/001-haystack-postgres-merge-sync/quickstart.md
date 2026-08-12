# Quickstart: Haystack Postgres Merge Sync

**Feature**: `001-haystack-postgres-merge-sync`  
**Audience**: Developers verifying the feature after implementation

## Full runtime verification

For complete step-by-step checks (SC-001–SC-007), expected results, and a pass/fail checklist, use:

**→ [Running Verification](./verification.md)**

That document is the source of truth for runtime verification. This page is a short entry point only.

## Prerequisites (summary)

1. Docker with Compose v2  
2. Network (once): `docker network create heavy-rental-network`  
3. REST API stack running so **`postgres-primary`** is healthy (shared network)  
4. Haystack stack running (`postgres-haystack`, `postgres-haystack-sync`, `haystack-fast-api`, plus `neo4j` when full stack)

## Baseline runbook (T0)

| Check | Expect |
|---|---|
| Network exists | `docker network inspect heavy-rental-network` succeeds |
| Primary up | Container `postgres-primary` healthy on shared network |
| Local PG | `postgres-haystack` healthy; host port **5434** |
| Sync | `postgres-haystack-sync` running (`unless-stopped`); logs show merge or skip |
| Near-RT default | `SYNC_INTERVAL_SECONDS=60`, `HALT_ON_PRIMARY_UNAVAILABLE=false` |
| Fleet allowlist (T2) | `SYNC_TABLE_ALLOWLIST=asset,booking,category` (use `all` for full public) |
| Lag metrics (T1) | Logs include `METRICS cycle` with `duration_ms` |
| Halt path (optional) | Set halt `true` + recreate sync → job exits when primary down; local PG still R/W |
| Staging schema | After merge, `primary_snapshot` may exist (FDW staging; expected) |

## Start Haystack stack (summary)

```bash
# Rebuild/reopen the Haystack Fast API devcontainer, or:
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

| Service | Container | Role |
|---|---|---|
| `postgres-haystack` | `postgres-haystack` | Writable local Postgres |
| `postgres-haystack-sync` | `postgres-haystack-sync` | Near-RT merge scheduler (60s poll) |
| `haystack-fast-api` | `haystack-fast-api` | App (uses local `postgres-haystack`) |
| `neo4j` | `neo4j-haystack` | Graph / DocumentStore (see specs/002) |

## Minimal smoke (optional)

Local DB writable:

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT current_database(), pg_is_in_recovery();"
```

Sync logs:

```bash
docker logs postgres-haystack-sync
```

Then continue with **[verification.md](./verification.md)** for SC-001–SC-007.

## Related specs

- Feature: [spec.md](./spec.md)  
- Running verification: [verification.md](./verification.md)  
- Plan: [plan.md](./plan.md)  
- Env contract: [contracts/db-sync-env.md](./contracts/db-sync-env.md)  
- D0 schema contract: [contracts/schema-contract.md](./contracts/schema-contract.md)  
- OpenSpec SoT: `openspec/specs/haystack-devcontainer/spec.md`  
- OpenSpec archive: `openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/`  
- Phase 4 archive: `openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/`
