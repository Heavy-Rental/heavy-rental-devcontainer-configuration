# REST API Devcontainer Specification

## Purpose

Behavior of the **Heavy Rental Spring Boot REST API** development container packs under `Heavy-Rental-REST-API/`. This is the OpenSpec **source of truth** for agreed as-built behavior.

The project ships **two operator-selectable packs**:

1. **With PostgreSQL Read Replica** — app + primary + streaming standby  
2. **Without read replica** — app + primary only  

Operators MUST promote the chosen pack’s nested `.devcontainer` **one level up** so it becomes `Heavy-Rental-REST-API/.devcontainer` before opening the folder in VS Code Dev Containers.

Change history:

- `openspec/changes/archive/2026-08-09-add-rest-api-devcontainer-variants/`
- `openspec/changes/archive/2026-08-12-phase4-d0-schema-contract-fleet-source/` — Phase 4 D0 schema contract + primary as Haystack fleet pull source

Spec Kit: `specs/001-rest-api-devcontainer/`.

## Requirements

### Requirement: Dual pack distribution

The repository MUST provide two pack directories under `Heavy-Rental-REST-API/`, each containing a complete nested `.devcontainer` for the Spring Boot REST API:

- `Spring Boot REST API devcontainer with PostgreSQL Read Replica`
- `Spring Boot REST API devcontainer without read replica`

#### Scenario: Packs present

- **GIVEN** a checkout of this repository
- **WHEN** an operator lists `Heavy-Rental-REST-API/`
- **THEN** both pack folders exist with a nested `.devcontainer`

### Requirement: Promote `.devcontainer` one level up

Before using Dev Containers, the operator MUST move the chosen pack’s `.devcontainer` directory to `Heavy-Rental-REST-API/.devcontainer` (directly under the REST API project folder). Documentation MUST describe this promote step and warn that only one active `.devcontainer` is supported.

#### Scenario: Active config after promote

- **GIVEN** the operator moved one pack’s `.devcontainer` to `Heavy-Rental-REST-API/.devcontainer`
- **WHEN** VS Code opens `Heavy-Rental-REST-API`
- **THEN** Dev Containers can resolve `devcontainer.json` and `docker-compose.yml` at that path

### Requirement: Shared Compose stack baseline

Both packs MUST define:

- Application service `heavy-rental-rest-api` (Java 21 + Maven base image)
- Primary Postgres service `db-primary` / container `postgres-primary` (`postgres:17`), database `heavy_rental`
- Host mapping primary **5432**
- External network `heavy-rental-network`
- App environment `SPRING_DATASOURCE_URL=jdbc:postgresql://db-primary:5432/heavy_rental` (and matching username/password)
- Non-root `remoteUser` `vscode` and `postCreateCommand` ownership fix for the workspace
- VS Code extensions: Java Pack, Spring Boot Extension Pack, Postgres client

#### Scenario: App uses primary

- **GIVEN** either pack is active and running
- **WHEN** app environment is inspected
- **THEN** `SPRING_DATASOURCE_URL` targets `db-primary:5432/heavy_rental`

#### Scenario: Primary writable

- **GIVEN** primary is healthy
- **WHEN** a client connects with configured credentials
- **THEN** the client can read and write, and `pg_is_in_recovery()` is false

### Requirement: With-replica profile

The **with PostgreSQL Read Replica** pack MUST additionally define service `db-replica-one` / container `postgres-replica-one`, host port **5433**, streaming replication bootstrap from primary (including replication role and WAL settings on primary), and a VS Code Postgres profile for the replica.

#### Scenario: Replica is standby

- **GIVEN** the with-replica pack is active and healthy
- **WHEN** `pg_is_in_recovery()` is queried on the replica
- **THEN** the result is true

#### Scenario: Replica IDE profile

- **GIVEN** the with-replica pack’s `devcontainer.json`
- **WHEN** `pgsql.connections` is inspected
- **THEN** profiles exist for primary and replica (`db-replica-one`)

### Requirement: Without-replica profile

The **without read replica** pack MUST NOT require a running replica service. Its VS Code Postgres settings MUST include the primary connection only.

#### Scenario: No replica service required

- **GIVEN** the without-replica pack is active
- **WHEN** Compose services are listed
- **THEN** a healthy `db-replica-one` service is not required for the stack to be valid

### Requirement: Shared network

All services in the active pack MUST join external network `heavy-rental-network` so peer stacks (e.g. Haystack) can reach `postgres-primary` when present.

#### Scenario: Network attachment

- **GIVEN** `heavy-rental-network` exists
- **WHEN** the active Compose stack starts
- **THEN** app and primary (and replica if present) are attached to that network

### Requirement: Primary is Haystack fleet pull source (Phase 4 T0)

Container `postgres-primary` (database `heavy_rental`) MUST remain reachable on `heavy-rental-network` as the **read source** for peer Haystack merge-sync. This pack MUST NOT implement the Haystack merge-sync job.

#### Scenario: Peer can resolve primary

- **GIVEN** both REST API and Haystack stacks are on `heavy-rental-network` and primary is healthy
- **WHEN** Haystack sync resolves hostname `postgres-primary`
- **THEN** connectivity checks to port 5432 can succeed

### Requirement: D0 fleet schema contract (Phase 4)

Spec Kit MUST publish a versioned producer schema contract at `specs/001-rest-api-devcontainer/contracts/schema-contract.md` documenting default fleet tables (`asset`, `booking`, `category`) for Haystack allowlist alignment.

#### Scenario: Contract present

- **GIVEN** a checkout of this repository
- **WHEN** an operator opens the REST Spec Kit contracts folder
- **THEN** `schema-contract.md` exists at version 1.0
