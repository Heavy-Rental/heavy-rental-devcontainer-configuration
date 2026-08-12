# Feature Specification: Haystack pgvector platform (T5 / D4)

**Feature Branch**: `004-haystack-pgvector`  
**Created**: 2026-08-12  
**Status**: Implemented (platform ready)  
**Feasibility**: Phase 5 Step 5.1 — T5 / D4 (`CREATE EXTENSION vector` / pgvector image)

## User Scenarios & Testing

### User Story 1 - Local Postgres has pgvector (Priority: P1)

As a Haystack developer, I need `postgres-haystack` to expose the PostgreSQL **`vector`** extension so I can later wire `PgvectorDocumentStore` without changing OLTP primary or rebuilding the fleet mirror path.

**Acceptance:**

1. **Given** the Haystack stack is healthy, **When** I query `pg_extension` for `vector`, **Then** the extension is present on database `heavy_rental`.
2. **Given** a fresh data volume, **When** Postgres initializes, **Then** init SQL creates the extension.
3. **Given** an existing volume upgraded from plain `postgres:17`, **When** healthcheck / operator ensure runs, **Then** `CREATE EXTENSION IF NOT EXISTS vector` succeeds.

### User Story 2 - Embedding dim contract documented (Priority: P1)

As an app implementer of I0/I1, I need a single documented default for `INDEXING_EMBEDDING_DIM` that matches future Pgvector column and embedder configuration.

**Acceptance:**

1. **Given** the `haystack-fast-api` container, **When** I inspect env, **Then** `INDEXING_EMBEDDING_DIM` is set (default **768**).
2. **Given** Spec Kit contracts, **When** I read [contracts/pgvector-env.md](./contracts/pgvector-env.md), **Then** dim, image tag, and non-goals (no factory yet) are explicit.

### User Story 3 - Fleet merge and Neo4j unchanged (Priority: P2)

As an operator, enabling pgvector must not break merge-sync or Neo4j.

**Acceptance:**

1. **Given** the full stack, **When** services are listed, **Then** `postgres-haystack`, `postgres-haystack-sync`, `neo4j`, and `haystack-fast-api` remain defined.
2. **Given** primary is up, **When** a sync cycle runs, **Then** allowlist merge behavior is unchanged.
3. **Given** Neo4j is healthy, **When** I run `RETURN 1`, **Then** it still succeeds.

## Requirements

- **FR-001**: Compose service `postgres-haystack` MUST use image **`pgvector/pgvector:pg17`** (or a documented equivalent Postgres 17 image that ships pgvector).
- **FR-002**: Database `heavy_rental` on `postgres-haystack` MUST have extension **`vector`** available after the service is healthy.
- **FR-003**: Fresh volumes MUST bootstrap via `/docker-entrypoint-initdb.d` (`CREATE EXTENSION IF NOT EXISTS vector`).
- **FR-004**: The stack MUST ensure the extension on upgraded volumes (idempotent healthcheck ensure and/or documented one-shot).
- **FR-005**: App service MUST expose `INDEXING_EMBEDDING_DIM` (default **768**) as the platform dim contract for future I0/I1.
- **FR-006**: This feature MUST NOT require `INDEXING_DOCUMENT_STORE`, pipeline wiring, or document tables (I0/I1 remain app work).
- **FR-007**: REST API `postgres-primary` MUST NOT be required to install pgvector; fleet SoT stays plain Postgres.
- **FR-008**: Host port **5434**, credentials, and merge-sync job image MAY remain as before (`postgres-haystack-sync` may stay on `postgres:17`).

## Success Criteria

- **SC-001**: `SELECT extname FROM pg_extension WHERE extname = 'vector'` returns a row.
- **SC-002**: `pg_is_in_recovery()` is false; app `DATABASE_URL` still targets `postgres-haystack`.
- **SC-003**: `INDEXING_EMBEDDING_DIM=768` visible in app env (or documented override).
- **SC-004**: Merge-sync and Neo4j health paths still pass their existing checks.
- **SC-005**: Spec Kit + OpenSpec describe platform-only scope and peer impact.

## Assumptions

- Embedding model/dim for production may change later; operators update `INDEXING_EMBEDDING_DIM` and migrate vector tables when I1 lands.
- Neo4j remains available for graph DocumentStore; pgvector is the durable **project-chunk** vector path target.
- FAISS remains historical only (`003`).

## Out of scope

- DocumentStore factory (I0), indexing cutover (I1), isolation tests, TTL cleanup, production default pgvector (I2).
