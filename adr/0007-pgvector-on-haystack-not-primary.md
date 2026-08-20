# ADR-0007: pgvector lives on Haystack Postgres; FAISS is not default

- Status: accepted
- Date: 2026-08-20
- Tags: haystack, vector, pgvector

## Context

Haystack needs a durable vector platform for future DocumentStore (I0 factory, I1 pipeline writer). FAISS was explored as an in-process index (`specs/003-haystack-faiss`) but is a poor fit for multi-user durable project vectors. Installing `vector` on REST `postgres-primary` would couple OLTP operations to an AI extension and image.

## Decision

- Local Haystack Postgres image is **`pgvector/pgvector:pg17`** with extension **`vector`** on `heavy_rental`.
- App env documents **`INDEXING_EMBEDDING_DIM=768`**. Document/vector tables and I0/I1 wiring are **application** work, not this configuration pack.
- REST **`postgres-primary` MUST NOT** require pgvector or a pgvector image.
- **FAISS is not** in the default Compose / `postCreateCommand` path. Spec Kit `003-haystack-faiss` is historical only.

## Consequences

- Vector and fleet-mirror data share `postgres-haystack` (separate from OLTP).
- Existing volumes created with plain `postgres:17` need a healthcheck `CREATE EXTENSION` (same major 17) or recreate.
- Dim changes after I1 are application migrations.

## Related

- OpenSpec archive: `Haystack-Fast-API/openspec/changes/archive/2026-08-12-phase5-t5-d4-pgvector-platform/`
- Peer note: `Heavy-Rental-REST-API/openspec/changes/archive/2026-08-12-phase5-peer-pgvector-platform-note/`
- Spec Kit: `Haystack-Fast-API/specs/004-haystack-pgvector/`
