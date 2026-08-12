# Proposal: Phase 5 T5 / D4 — pgvector platform ready

## Intent

Close **Phase 5 Step 5.1** (feasibility T5 / D4) for the Haystack Fast API devcontainer:

1. Run local Postgres with **pgvector** (`pgvector/pgvector:pg17`).
2. Ensure **`CREATE EXTENSION vector`** on `heavy_rental`.
3. Document **`INDEXING_EMBEDDING_DIM`** (default 768) for later app I0/I1.

## Scope

### In scope

- Compose image + initdb + healthcheck ensure for `postgres-haystack`
- App env dim contract
- Spec Kit `004-haystack-pgvector`
- OpenSpec SoT + this archive
- Operator README; peer notes on REST API and Web Portal packs

### Out of scope

- `INDEXING_DOCUMENT_STORE` factory (I0) — application repo
- Indexing pipeline → PgvectorDocumentStore (I1) — application repo
- Tenant isolation / TTL jobs
- Neo4j populate (Phase 8)
- pgvector on REST `postgres-primary`
- FAISS re-introduction

## Approach

1. Switch `postgres-haystack` to `pgvector/pgvector:pg17`.
2. Bootstrap extension on first init; healthcheck `CREATE EXTENSION IF NOT EXISTS` for upgrades.
3. Publish Spec Kit + OpenSpec requirements as platform-only.

## Related artifacts

- Spec Kit: `specs/004-haystack-pgvector/`
- SoT: `openspec/specs/haystack-devcontainer/spec.md`
- Feasibility: Phase 5 Step 5.1; dual-plane §11.4 T5
