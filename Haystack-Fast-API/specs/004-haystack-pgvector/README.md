# Spec Kit: Haystack pgvector platform (T5 / D4)

**Feature**: `004-haystack-pgvector`  
**Status**: **Platform ready** (Phase 5 Step 5.1 — T5 / D4)  
**Date**: 2026-08-12

Postgres-Haystack (`postgres-haystack`) runs **PostgreSQL 17 + pgvector** so the Haystack app can later cut over indexing DocumentStore to `PgvectorDocumentStore` (I0/I1 in the **application** repo). This pack only ensures the **extension is present** and documents the **embedding dim** contract.

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Requirements and success criteria |
| [plan.md](./plan.md) | As-built plan |
| [research.md](./research.md) | Image / extension decisions |
| [data-model.md](./data-model.md) | Platform entities and dim contract |
| [contracts/pgvector-env.md](./contracts/pgvector-env.md) | Image, extension, env contract |
| [verification.md](./verification.md) | Runtime checks |
| [quickstart.md](./quickstart.md) | Operator entry |
| [tasks.md](./tasks.md) | Task list |

**Implementation:** `Haystack-Fast-API/.devcontainer/docker-compose.yml`, `initdb/01-create-vector-extension.sql`  
**OpenSpec:** `openspec/specs/haystack-devcontainer/spec.md` + archive `2026-08-12-phase5-t5-d4-pgvector-platform`

**Out of scope here (app follow-on):**

- `INDEXING_DOCUMENT_STORE` factory (I0)
- Pipeline writer → Pgvector (I1)
- Tenant isolation / TTL jobs

**Related:** [001 merge-sync](../001-haystack-postgres-merge-sync/) · [002 Neo4j](../002-haystack-neo4j/) · historical [003 FAISS](../003-haystack-faiss/)
