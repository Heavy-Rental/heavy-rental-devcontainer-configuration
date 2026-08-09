# Feature Specification: Haystack FAISS DocumentStore Devcontainer Support

**Feature Branch**: `003-haystack-faiss`

**Created**: 2026-08-09

**Status**: Implemented

**Input**: Include FAISSDocumentStore support in the Haystack Fast API devcontainer (alongside existing Neo4j-Haystack) via package install, env contract, and optional index persistence path.

## User Scenarios & Testing

### User Story 1 - Package ready for FAISS (Priority: P1)

As a Haystack developer, after opening or rebuilding the devcontainer I can import and construct `FAISSDocumentStore` without hunting for install steps.

**Independent Test**: Follow verification install/import steps; import succeeds.

**Acceptance Scenarios**:

1. **Given** the app container has completed `postCreateCommand` (or documented install), **When** I run a Python import of `FAISSDocumentStore`, **Then** the import succeeds.
2. **Given** install docs, **When** I prefer project-managed deps, **Then** `uv add faiss-haystack` (or equivalent) is documented.

### User Story 2 - Configured index path via env (Priority: P1)

As a Haystack developer, the app container exposes `FAISS_INDEX_PATH` (and optional dim/index defaults) so I can construct a store without hardcoding paths.

**Independent Test**: `printenv FAISS_INDEX_PATH` inside `haystack-fast-api` shows a non-empty writable path under the workspace.

**Acceptance Scenarios**:

1. **Given** the app container is running, **When** I read `FAISS_INDEX_PATH`, **Then** it points at a path under the workspace volume (default documented in the env contract).
2. **Given** that path, **When** a Python client constructs `FAISSDocumentStore` with `index_path` from the env, **Then** construction succeeds.

### User Story 3 - Persist index across process restart (Priority: P2)

As a developer, I can save a FAISS index to the configured path and reload it later in the same container/workspace.

**Independent Test**: Write dummy documents with embeddings, save, construct/load from the same path, count documents.

**Acceptance Scenarios**:

1. **Given** a writable `FAISS_INDEX_PATH` parent directory, **When** I save an index and reopen the store from that path, **Then** the persisted files are readable.

### User Story 4 - Coexist with Postgres and Neo4j (Priority: P1)

As a developer, FAISS does not replace Postgres or Neo4j; all remain available for their roles.

**Acceptance Scenarios**:

1. **Given** the full stack, **When** I list Compose services, **Then** `db`, `db-sync`, `neo4j`, and `haystack-fast-api` are still present (no FAISS Compose service required).

## Edge Cases

- First create with empty workspace: parent directory for the index path may need `mkdir -p`.
- FAISS wheel install failure on base image: document conda/apt fallbacks in research/verification.
- OpenMP runtime conflicts (more common on macOS host tooling): document `OMP_NUM_THREADS` only if needed inside the Linux container.
- Large indexes: disk lives on the workspace volume; developers manage size.

## Requirements

- **FR-001**: Devcontainer MUST install (or document install of) `faiss-haystack` (CPU) for FAISSDocumentStore.
- **FR-002**: App service MUST expose `FAISS_INDEX_PATH` pointing at a writable path under the workspace volume.
- **FR-003**: Docs MUST show import/construct smoke using `haystack_integrations.document_stores.faiss.FAISSDocumentStore`.
- **FR-004**: Stack MUST continue to provide Neo4j and Postgres; FAISS does not replace them.
- **FR-005**: No separate FAISS Compose service is required (in-process store).
- **FR-006**: Optional env defaults `FAISS_EMBEDDING_DIM` and `FAISS_INDEX_STRING` MAY be set for convenience.

### Key Entities

- **FAISSDocumentStore**: In-process local vector DocumentStore (Haystack integration).
- **Index path**: Disk prefix for `.faiss` / `.json` persistence.
- **faiss-haystack**: Python integration package (app dependency).

## Success Criteria

- **SC-001**: `faiss-haystack` import succeeds after create/install steps.
- **SC-002**: `FAISS_INDEX_PATH` present and parent path creatable/writable in app container.
- **SC-003**: Optional save/load smoke succeeds using the configured path.
- **SC-004**: Postgres and Neo4j stack undisturbed; no extra FAISS service.

## Assumptions

- Application pipelines using DocumentStore live primarily in the workspace project, not only this config repo.
- CPU FAISS is sufficient for local development.
- Workspace volume `haystack-fast-api-data` (or bind) provides durability for index files under the workspace path.
