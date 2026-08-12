# Implementation Plan: Haystack Postgres Merge Sync

**Branch**: `001-haystack-postgres-merge-sync` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Status**: **Implemented** (as-built)

**Input**: Feature specification from `/specs/001-haystack-postgres-merge-sync/spec.md`

## Summary

Haystack Fast API devcontainer Compose provides:

1. Writable **PostgreSQL 17** (`postgres-haystack`) for app R/W  
2. Long-running **`postgres-haystack-sync`** job that **merge-upserts** from REST API **`postgres-primary`** (`heavy_rental`) via **postgres_fdw**  
3. Default **60s** near-RT poll schedule (first attempt at start); **skip** if primary unreachable (configurable halt)  
4. Merge keys: **PK preferred**, else **UNIQUE**  
5. Default **additive** schema evolution; **opt-in** parity flags for drops, indexes, safe type widenings; `SYNC_MODE=mirror` enables parity set  
6. **Phase 4:** default `SYNC_TABLE_ALLOWLIST=asset,booking,category`; cycle `METRICS` lag/duration logs; D0 schema contract  

No physical streaming replica. Local-only rows retained under default merge mode.

## Technical Context

**Language/Version**: Bash (`sync-from-primary.sh`); SQL (FDW, dynamic upserts); Docker Compose YAML

**Primary Dependencies**: Docker Compose v2; `postgres:17`; `pg_isready`, `psql`; `postgres_fdw` on local DB

**Storage**: Docker volume `postgres-haystack-data`

**Testing**: Manual per [verification.md](./verification.md)

**Target Platform**: Local / Codespaces-style Linux Docker (devcontainers)

**Constraints**:
- Shared external network `heavy-rental-network`
- Source DNS: **`postgres-primary`** (container name)
- Host port `5434` for local DB
- Postgres major 17 aligned with REST API primary
- Dev-only credentials

**Scale/Scope**: Single local DB; single sync job; **`public` schema** merge; opt-in index/type/drop parity

## As-built structure

```text
Haystack-Fast-API/.devcontainer/
├── docker-compose.yml          # haystack-fast-api, postgres-haystack, postgres-haystack-sync
├── devcontainer.json           # forwardPorts 5434, pgsql profiles, uv postCreate
├── Dockerfile
└── scripts/
    └── sync-from-primary.sh    # merge loop + evolution + opt-in flags

Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/
├── spec.md, plan.md, research.md, data-model.md
├── contracts/db-sync-env.md
├── verification.md, quickstart.md, tasks.md, README.md

Haystack-Fast-API/openspec/
├── specs/haystack-devcontainer/spec.md
└── changes/archive/2026-08-08-add-haystack-postgres-merge-sync/
```

## Implementation status

| Area | Status |
|---|---|
| Local `postgres-haystack` + app `DATABASE_URL` | Done |
| `postgres-haystack-sync` + 60s near-RT loop + skip/halt | Done (T1) |
| Cycle lag/duration `METRICS` logs | Done (T1 lag) |
| `SYNC_TABLE_ALLOWLIST` default fleet tables | Done (T2) |
| D0 schema-contract.md (consumer) | Done (D0) |
| FDW staging + PK/unique upsert | Done |
| Additive schema evolution | Done |
| Opt-in drop / indexes / type widen / `SYNC_MODE` | Done |
| Multi-schema beyond `public` | Deferred (flag documented) |
| FK sync | Reserved flag only |
| Runtime verification SC-001–SC-012 | Operator (see verification.md) |

## Constitution Check

| Gate | Status |
|---|---|
| External `heavy-rental-network` | PASS |
| Sandbox defaults (no default drops/FKs) | PASS |
| Spec Kit + OpenSpec docs | PASS (this package) |
| REST API primary as read source only | PASS |

## Testing

See [verification.md](./verification.md) and [contracts/db-sync-env.md](./contracts/db-sync-env.md).
