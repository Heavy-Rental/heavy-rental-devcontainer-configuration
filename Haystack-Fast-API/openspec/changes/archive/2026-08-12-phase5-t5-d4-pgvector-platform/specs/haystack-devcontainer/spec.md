# Delta: haystack-devcontainer — Phase 5 T5 / D4 pgvector platform

## ADDED Requirements

### Requirement: Pgvector platform on local Postgres (Phase 5 T5 / D4)

The local Postgres service (`postgres-haystack`) MUST use a PostgreSQL 17 image that includes **pgvector** (default: `pgvector/pgvector:pg17`). Database `heavy_rental` MUST have extension **`vector`** available when the service is healthy (bootstrap via initdb for fresh volumes; idempotent ensure for upgraded volumes). The application service MUST expose **`INDEXING_EMBEDDING_DIM`** (default **768**) as the platform embedding-dimension contract for a future `PgvectorDocumentStore` cutover.

This requirement is **platform-only**: the stack MUST NOT require application DocumentStore factory wiring (`INDEXING_DOCUMENT_STORE`), indexing pipeline writers, document tables, or tenant isolation tests (I0/I1 and later). REST API `postgres-primary` MUST NOT be required to install pgvector.

#### Scenario: Vector extension present

- **GIVEN** `postgres-haystack` is healthy
- **WHEN** an operator queries `pg_extension` for `vector` on `heavy_rental`
- **THEN** the extension is present

#### Scenario: Embedding dim contract on app env

- **GIVEN** the `haystack-fast-api` service is running
- **WHEN** environment variables are read
- **THEN** `INDEXING_EMBEDDING_DIM` is set (default `768`)

#### Scenario: Platform does not force DocumentStore cutover

- **GIVEN** only this platform requirement is satisfied
- **WHEN** an operator inspects Compose
- **THEN** no app-owned document vector tables are required to exist yet

## MODIFIED Requirements

### Requirement: Local writable database

Clarify that durable project-chunk vectors target **pgvector on local Postgres** (platform ready); Neo4j remains available for graph DocumentStore. Relational R/W and fleet mirror behavior unchanged.
