# Implementation Plan: Haystack pgvector platform

**Branch**: `004-haystack-pgvector` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Status**: **Implemented** (platform ready — T5 / D4)

**Input**: Feasibility Phase 5 Step 5.1 — T5 / D4; dual-plane §11.4 T5

## Summary

1. Switch `postgres-haystack` image to **`pgvector/pgvector:pg17`**
2. Bootstrap **`vector`** extension (initdb + healthcheck ensure)
3. Document **`INDEXING_EMBEDDING_DIM=768`** on the app service for later I0/I1
4. Spec Kit + OpenSpec + operator README; peer notes on REST / portal

No application DocumentStore factory or indexing pipeline changes in this config repo.

## Technical Context

**Primary Dependencies**: Docker Compose v2; `pgvector/pgvector:pg17`; `psql`

**Storage**: Existing volume `postgres-haystack-data` (Postgres 17 major)

**Testing**: Manual per [verification.md](./verification.md)

## As-built structure

```text
Haystack-Fast-API/.devcontainer/
├── docker-compose.yml          # postgres-haystack → pgvector/pgvector:pg17
├── initdb/
│   └── 01-create-vector-extension.sql
├── scripts/sync-from-primary.sh
└── …

Haystack-Fast-API/specs/004-haystack-pgvector/
├── spec.md, plan.md, research.md, data-model.md
├── contracts/pgvector-env.md
├── verification.md, quickstart.md, tasks.md, README.md

Haystack-Fast-API/openspec/
├── specs/haystack-devcontainer/spec.md
└── changes/archive/2026-08-12-phase5-t5-d4-pgvector-platform/
```

## Implementation status

| Area | Status |
|---|---|
| pgvector image on `postgres-haystack` | Done |
| initdb `CREATE EXTENSION vector` | Done |
| Healthcheck idempotent ensure | Done |
| `INDEXING_EMBEDDING_DIM` on app env | Done |
| Spec Kit 004 + OpenSpec SoT/archive | Done |
| Peer REST / portal docs | Done |
| I0 factory / I1 pipeline (app) | Deferred |

## Constitution Check

| Gate | Status |
|---|---|
| External `heavy-rental-network` | PASS |
| Primary remains pull source only | PASS |
| No FAISS re-introduction | PASS |
| Platform-only (no app DocumentStore) | PASS |

## Testing

See [verification.md](./verification.md) and [contracts/pgvector-env.md](./contracts/pgvector-env.md).
