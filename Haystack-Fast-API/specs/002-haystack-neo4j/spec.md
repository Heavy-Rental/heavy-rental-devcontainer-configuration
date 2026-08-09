# Feature Specification: Haystack Neo4j Devcontainer Service

**Feature Branch**: `002-haystack-neo4j`

**Created**: 2026-08-08

**Status**: Implemented

**Input**: Install Neo4j in the Haystack Fast API devcontainer for tight integration with Haystack (`neo4j-haystack` DocumentStore).

## User Scenarios & Testing

### User Story 1 - Local Neo4j for Haystack (Priority: P1)

As a Haystack developer, I have a Neo4j instance on the same Docker network as my app so I can store documents and embeddings for RAG without an external cloud graph DB.

**Independent Test**: Start the stack; Neo4j healthy; Bolt and Browser reachable.

**Acceptance Scenarios**:

1. **Given** the Haystack Compose stack is started, **When** I check containers, **Then** `neo4j-haystack` is running and healthy.
2. **Given** Neo4j is healthy, **When** I open Neo4j Browser on host port 7474 (or connect Bolt on 7687), **Then** I can authenticate with the documented dev credentials.

### User Story 2 - App can connect via env (Priority: P1)

As a Haystack developer, the app container exposes `NEO4J_*` environment variables pointing at the Compose service so `neo4j-haystack` / the Neo4j driver work without hardcoding hosts.

**Independent Test**: `printenv NEO4J_URI` inside `haystack-fast-api` shows `bolt://neo4j:7687`.

**Acceptance Scenarios**:

1. **Given** the app container is running, **When** I read `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, **Then** they match the Neo4j service configuration.
2. **Given** those env vars, **When** a Python client uses them, **Then** a simple `RETURN 1` (or DocumentStore write) succeeds.

### User Story 3 - Package install path for neo4j-haystack (Priority: P2)

As a developer, I know how to install `neo4j-haystack` in the devcontainer (via `uv` and/or project dependencies).

**Independent Test**: Follow verification install steps; import `neo4j_haystack` succeeds.

### User Story 4 - Coexist with Postgres (Priority: P1)

As a developer, Neo4j does not replace Postgres; both run for domain SQL and Haystack documents respectively.

**Acceptance Scenarios**:

1. **Given** the full stack, **When** I list services, **Then** `db`, `db-sync`, `neo4j`, and `haystack-fast-api` are all present.

### User Story 5 - Neo4j for VS Code extension (Priority: P2)

As a Haystack developer, the devcontainer preinstalls the official **Neo4j for VS Code** extension so I can connect over Bolt and run Cypher without leaving the IDE (Neo4j Browser on 7474 remains available).

**Independent Test**: `devcontainer.json` lists `neo4j-extensions.neo4j-for-vscode`; after rebuild, the extension is available; connect with documented credentials.

**Acceptance Scenarios**:

1. **Given** `Haystack-Fast-API/.devcontainer/devcontainer.json`, **When** I inspect `customizations.vscode.extensions`, **Then** `neo4j-extensions.neo4j-for-vscode` is present.
2. **Given** Neo4j is healthy and I am in the app container network, **When** I connect the extension with URI `bolt://neo4j:7687` and dev credentials, **Then** a simple Cypher query can succeed.

## Edge Cases

- Neo4j first-start password/auth: use `NEO4J_AUTH` so no interactive password change is required in Compose.
- Healthcheck may fail briefly after start: use adequate `start_period`.
- Host ports 7474/7687 conflict: document remapping.
- Low-memory hosts: reduce heap env settings.

## Requirements

- **FR-001**: Compose MUST include a Neo4j 5 Community service on `heavy-rental-network`.
- **FR-002**: Neo4j MUST persist data in a dedicated Docker volume.
- **FR-003**: Host MUST map Bolt `7687` and HTTP Browser `7474` (or documented alternatives).
- **FR-004**: `haystack-fast-api` MUST receive `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`.
- **FR-005**: App MUST depend on Neo4j becoming healthy before considered ready (Compose `depends_on`).
- **FR-006**: Dev credentials MUST be documented as local-only.
- **FR-007**: Docs MUST describe installing `neo4j-haystack` with `uv` for Haystack DocumentStore usage.
- **FR-008**: Postgres services MUST remain available; Neo4j does not replace them.
- **FR-009**: Devcontainer MUST list `neo4j-extensions.neo4j-for-vscode` under `customizations.vscode.extensions`.
- **FR-010**: Docs MUST describe connecting Neo4j for VS Code (and Browser) with the documented Bolt URL and dev credentials.

### Key Entities

- **Neo4j service**: Graph + vector store for Haystack documents.
- **Connection config**: Env-based Bolt URL and auth.
- **neo4j-haystack**: Python integration package (app dependency).
- **Neo4j for VS Code**: IDE extension (`neo4j-extensions.neo4j-for-vscode`) for Cypher/Bolt.

## Success Criteria

- **SC-001**: Neo4j healthy within a few minutes of stack start (excluding image pull).
- **SC-002**: Bolt connect from app network with documented credentials succeeds.
- **SC-003**: Neo4j Browser reachable on host (or via port forward).
- **SC-004**: `NEO4J_*` env present in app container.
- **SC-005**: Postgres stack undisturbed.
- **SC-006**: `devcontainer.json` includes `neo4j-extensions.neo4j-for-vscode`.

## Assumptions

- External network `heavy-rental-network` exists.
- Dev-only password is acceptable.
- Application pipelines using DocumentStore live primarily in the workspace project, not only this config repo.
