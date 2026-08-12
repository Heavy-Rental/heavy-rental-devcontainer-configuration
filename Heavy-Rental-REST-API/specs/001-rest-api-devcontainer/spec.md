# Feature Specification: Heavy Rental REST API Devcontainer Packs

**Feature Branch**: `001-rest-api-devcontainer`

**Created**: 2026-08-09

**Status**: Specified (as-built)

**Input**: Document and govern two Spring Boot REST API devcontainer packs—with and without PostgreSQL streaming read replica—and require operators to promote the chosen pack’s `.devcontainer` one level up under `Heavy-Rental-REST-API/`.

## User Scenarios & Testing

### User Story 1 - Choose a pack by preference (Priority: P1)

As a developer, I understand the difference between the **with read replica** and **without read replica** packs and pick one based on whether I need a local standby.

**Independent Test**: README comparison table matches as-built Compose (services and host ports).

**Acceptance Scenarios**:

1. **Given** both pack folders exist, **When** I read the README difference section, **Then** I can name which services and ports each pack provides.
2. **Given** I only need a single writable Postgres, **When** I choose the without-replica pack, **Then** I am not required to run `db-replica-one`.

### User Story 2 - Promote `.devcontainer` one level up (Priority: P1)

As a developer, I move the chosen pack’s `.devcontainer` directory so it sits **directly under** `Heavy-Rental-REST-API/`, which is the folder I open in VS Code Dev Containers.

**Independent Test**: After `mv`, `Heavy-Rental-REST-API/.devcontainer/devcontainer.json` and `docker-compose.yml` exist.

**Acceptance Scenarios**:

1. **Given** no active `.devcontainer` at `Heavy-Rental-REST-API/`, **When** I move the chosen pack’s `.devcontainer` to `./.devcontainer`, **Then** Dev Containers can detect the configuration at the project root.
2. **Given** an old active `.devcontainer` exists, **When** I replace it with another pack, **Then** documentation warns me to remove or rename the previous active config first.

### User Story 3 - Open in Dev Containers (Priority: P1)

As a developer, after promoting the pack, I open `Heavy-Rental-REST-API` in VS Code and reopen in a container.

**Independent Test**: App container `heavy-rental-rest-api` is running; primary is healthy.

### User Story 4 - Primary writable Postgres (Priority: P1)

As a developer, the REST API app and tools use **primary** Postgres (`db-primary` / `postgres-primary`) for default R/W, database `heavy_rental`.

**Acceptance Scenarios**:

1. **Given** the stack is up, **When** I connect as `postgres` to primary, **Then** I can insert and select data.
2. **Given** the app container environment, **When** I read `SPRING_DATASOURCE_URL`, **Then** it points at `db-primary:5432/heavy_rental`.

### User Story 5 - Streaming read replica (with-replica pack only) (Priority: P2)

As a developer using the **with replica** pack, I have a second Postgres instance that is a streaming standby, reachable as `db-replica-one` and on host port **5433**.

**Acceptance Scenarios**:

1. **Given** the with-replica pack is active and healthy, **When** I query `pg_is_in_recovery()` on the replica, **Then** the result is true.
2. **Given** the with-replica pack’s `devcontainer.json`, **When** I inspect `pgsql.connections`, **Then** both primary and “Replica (Read)” profiles are defined.

### User Story 6 - Without-replica pack stays simple (Priority: P1)

As a developer using the **without replica** pack, no replica service is required; IDE has a single primary connection profile.

**Acceptance Scenarios**:

1. **Given** the without-replica pack is active, **When** I list Compose services, **Then** `db-replica-one` is not defined as a running service requirement.
2. **Given** that pack’s `devcontainer.json`, **When** I inspect `pgsql.connections`, **Then** only the primary profile is present.

## Edge Cases

- External network `heavy-rental-network` missing → Compose fails until `docker network create heavy-rental-network`.
- Promoting while an old `.devcontainer` exists → must replace/rename first.
- Switching packs → remove active config; restore other pack from git if already moved.
- Replica first boot needs healthy primary; `start_period` allows bootstrap time.
- Without-replica compose may still declare unused volume `postgres-replica-one-data` (as-built leftover; not a service).

## Requirements

- **FR-001**: Repository MUST provide two pack folders under `Heavy-Rental-REST-API/` containing a nested `.devcontainer`.
- **FR-002**: Operator docs MUST instruct moving the chosen `.devcontainer` **up one level** to `Heavy-Rental-REST-API/.devcontainer`.
- **FR-003**: Both packs MUST define app service `heavy-rental-rest-api` on external network `heavy-rental-network`.
- **FR-004**: Both packs MUST define primary Postgres service `db-primary` (container `postgres-primary`), database `heavy_rental`, host port **5432**.
- **FR-005**: Both packs MUST set Spring datasource env to primary (`SPRING_DATASOURCE_URL` → `jdbc:postgresql://db-primary:5432/heavy_rental`).
- **FR-006**: With-replica pack MUST define `db-replica-one` (container `postgres-replica-one`), host port **5433**, streaming replication bootstrap from primary.
- **FR-007**: With-replica pack MUST provision replication role (e.g. `replicator`) and primary WAL settings suitable for streaming.
- **FR-008**: Without-replica pack MUST NOT require a running replica service.
- **FR-009**: Devcontainer MUST use non-root `vscode` and fix workspace ownership in `postCreateCommand`.
- **FR-010**: Devcontainer MUST install Java Pack, Spring Boot Extension Pack, and Postgres VS Code extension; `pgsql.connections` MUST match the active pack (primary only vs primary+replica).
- **FR-011**: Forward ports MUST include **8080** and **5432** (replica host **5433** is Compose-mapped for with-replica pack).
- **FR-012** (Phase 4 T0): Primary container `postgres-primary` MUST remain on external network `heavy-rental-network` so peer Haystack merge-sync can resolve and read `heavy_rental`.
- **FR-013** (Phase 4 D0): Spec Kit MUST publish a versioned fleet domain [schema-contract.md](./contracts/schema-contract.md) (producer) listing tables used by Haystack fleet LTM allowlist (`asset`, `booking`, `category` by default).
- **FR-014** (Phase 4): This pack MUST NOT implement Haystack merge-sync; REST primary is **pull source only**. Sync job lives in Haystack-Fast-API.

### Key Entities

- **Pack folder**: Named directory holding a nested `.devcontainer` before promote.
- **Active `.devcontainer`**: Configuration at `Heavy-Rental-REST-API/.devcontainer` after promote.
- **Primary**: Writable Postgres for the API; fleet domain **source of truth** for Haystack mirror.
- **Replica**: Optional streaming standby (with-replica pack only).
- **D0 schema contract**: Versioned inventory of fleet tables shared with Haystack consumer docs.

## Success Criteria

- **SC-001**: README alone enables choose → move up → reopen in container.
- **SC-002**: Primary healthy and writable for both packs.
- **SC-003**: With-replica: replica healthy and in recovery.
- **SC-004**: App env points datasource at primary for both packs.
- **SC-005**: Spec Kit / OpenSpec names match as-built service, container, and port identifiers.
- **SC-006** (Phase 4 D0): `contracts/schema-contract.md` v1.0 exists and documents default fleet tables.
- **SC-007** (Phase 4 T0): Primary is documented as Haystack fleet pull source on `heavy-rental-network`.

## Assumptions

- Operators use VS Code Dev Containers (or compatible tooling).
- Dev-only passwords are acceptable locally.
- Application multi-datasource routing to replica is out of scope for the pack defaults.
