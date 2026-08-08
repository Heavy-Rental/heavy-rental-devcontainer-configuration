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
3. REST API stack running so **`postgres-primary`** is healthy  
4. Haystack stack running (`db`, `db-sync`, `haystack-fast-api`)

## Start Haystack stack (summary)

```bash
# Rebuild/reopen the Haystack Fast API devcontainer, or:
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

| Service | Container | Role |
|---|---|---|
| `db` | `postgres-haystack` | Writable local Postgres |
| `db-sync` | `postgres-haystack-sync` | Merge scheduler |
| `haystack-fast-api` | `haystack-fast-api` | App (uses local `db`) |

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
- OpenSpec SoT: `openspec/specs/haystack-devcontainer/spec.md`  
- OpenSpec archive: `openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/`  
