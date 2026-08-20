# Feature Specification: Heavy Rental Web Portal Devcontainer

**Feature Branch**: `001-web-portal-devcontainer`

**Created**: 2026-08-20

**Status**: Specified (as-built)

**Input**: Document the React Web Portal Dev Container pack: one app service on `heavy-rental-network`, no local database, product HTTP to Spring REST only.

## User Scenarios & Testing

### User Story 1 - Open the portal pack (Priority: P1)

As a UI developer, I open `Heavy-Rental-Web-Portal` in VS Code Dev Containers without moving a nested pack.

**Independent Test**: `.devcontainer/devcontainer.json` exists at pack root; container `heavy-rental-web-portal` starts.

**Acceptance Scenarios**:

1. **Given** a checkout of this repository, **When** I list `Heavy-Rental-Web-Portal/`, **Then** `.devcontainer` is already at that root.
2. **Given** `heavy-rental-network` exists, **When** I reopen in a container, **Then** service `heavy-rental-web-portal` is running.

### User Story 2 - No local database (Priority: P1)

As a UI developer, this pack does not start Postgres or Neo4j; I use the REST pack for data.

**Acceptance Scenarios**:

1. **Given** only the portal stack is up, **When** I list Compose services, **Then** I am not required to have `postgres-primary` or `neo4j` in this project.
2. **Given** REST is down, **When** the portal container is running, **Then** the container still runs; product API calls fail until REST is healthy.

### User Story 3 - Call Spring, not Haystack (Priority: P1)

As a product user of the UI, browser traffic goes to the REST API. Haystack is not a second public backend.

**Acceptance Scenarios**:

1. **Given** REST is on `heavy-rental-network`, **When** the app is configured with the REST base URL, **Then** the portal can reach `heavy-rental-rest-api:8080` from the container network.
2. **Given** Haystack is down, **When** the portal talks only to REST for CRUD, **Then** CRUD does not require Haystack.

## Edge Cases

- External network missing → Compose fails until `docker network create heavy-rental-network`.
- Port 5173 already bound on the host → operator frees the port or remaps.
- API base URL unset in app sources → pack still starts; UI cannot load real data.

## Requirements

- **FR-001**: Pack MUST define Compose service `heavy-rental-web-portal` on external `heavy-rental-network`.
- **FR-002**: Pack MUST NOT define Postgres, Neo4j, merge-sync, or populate services.
- **FR-003**: Devcontainer MUST use non-root `node` and fix workspace ownership in `postCreateCommand`.
- **FR-004**: Forward ports MUST include **5173** (Vite/React dev server).
- **FR-005**: Workspace mount MUST be `/workspaces/heavy-rental-web-portal`.
- **FR-006**: Product HTTP MUST be documented as REST-only; Haystack is optional dual-hop behind Spring.
- **FR-007**: `.devcontainer` MUST sit at pack root (no promote step).
- **FR-008**: Spec Kit / OpenSpec names MUST match as-built service and port identifiers.

### Key Entities

- **Portal container**: `heavy-rental-web-portal`
- **Peer REST**: `heavy-rental-rest-api` / host **8080**
- **Network**: `heavy-rental-network`

## Success Criteria

- **SC-001**: README + quickstart enable open-folder-in-container without a promote step.
- **SC-002**: Container `heavy-rental-web-portal` is defined and joins the external network.
- **SC-003**: No pack-local database service is required.
- **SC-004**: Docs state product HTTP goes to Spring REST only.
- **SC-005**: OpenSpec SoT exists at `openspec/specs/web-portal-devcontainer/spec.md`.

## Assumptions

- Operators use VS Code Dev Containers (or compatible tooling).
- Portal application sources live in the mounted workspace volume.
- Vite is the typical dev server (port 5173); the app may bind that port after sources exist.
