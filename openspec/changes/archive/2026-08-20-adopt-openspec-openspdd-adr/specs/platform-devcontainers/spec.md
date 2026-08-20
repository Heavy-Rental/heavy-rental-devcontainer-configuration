## ADDED Requirements

### Requirement: Three independent packs on a shared external network

The repository MUST provide three pack folders — `Heavy-Rental-Web-Portal/`, `Heavy-Rental-REST-API/`, `Haystack-Fast-API/` — each with its own Compose stack. There MUST NOT be a root Compose file that starts all three. All application and data services MUST attach to the **external** Docker network `heavy-rental-network`. Packs MUST NOT create that network.

#### Scenario: Packs present

- **GIVEN** a checkout of this repository
- **WHEN** an operator lists the repository root
- **THEN** the three pack folders exist

#### Scenario: Network is external

- **GIVEN** `heavy-rental-network` does not exist
- **WHEN** an operator starts any pack Compose project
- **THEN** Compose fails until `docker network create heavy-rental-network` has been run

### Requirement: Pack runtime roles

| Pack | Role |
|------|------|
| Web Portal | Presentation (React / Vite); no local database |
| REST API | Business HTTP API and OLTP source of truth (`postgres-primary`) |
| Haystack Fast API | Mirror, graph, and vector plane (`postgres-haystack`, Neo4j, merge-sync, populate) |

#### Scenario: Portal has no local database

- **GIVEN** only the Web Portal Compose stack is started
- **WHEN** services are listed
- **THEN** no Postgres or Neo4j service is required in that pack

### Requirement: OLTP write ownership

`postgres-primary` / database `heavy_rental` MUST remain the product OLTP source of truth. The Haystack stack MUST NOT write `postgres-primary`. Haystack merge-sync MUST be a **pull** from primary into `postgres-haystack`.

#### Scenario: Haystack does not write primary

- **GIVEN** both REST and Haystack stacks are on `heavy-rental-network`
- **WHEN** merge-sync runs
- **THEN** primary is used as a read source only

### Requirement: Portal HTTP trust boundary

The Web Portal MUST use the REST API as its product HTTP backend. Recommend-style features MAY be implemented as Spring dual-hop into Haystack. The portal MUST NOT require direct Haystack, Postgres, or Neo4j credentials for product flows.

#### Scenario: Portal depends on REST, not Haystack

- **GIVEN** the portal container is running and REST is down
- **WHEN** the UI issues product API calls
- **THEN** those calls fail until REST is healthy
- **AND** the portal pack itself does not start Haystack

### Requirement: Cross-pack DNS contract

Peer integration MUST use Compose/container DNS names on `heavy-rental-network` (for example `heavy-rental-rest-api`, `postgres-primary`, `postgres-haystack`, `neo4j`, `neo4j-populate`).

#### Scenario: Haystack sync resolves primary

- **GIVEN** both REST and Haystack stacks are up and primary is healthy
- **WHEN** Haystack sync resolves `postgres-primary`
- **THEN** a connectivity check to port 5432 can succeed

### Requirement: Platform architecture document

The repository MUST publish `ARCHITECTURE.md` describing pack roles, data flows, storage planes, ports, and trust boundaries, and MUST link OpenSpec, Spec Kit, ADR, and OpenSPDD entry points.

#### Scenario: Architecture doc present

- **GIVEN** a checkout of this repository
- **WHEN** an operator opens `ARCHITECTURE.md`
- **THEN** the three packs, shared network, and documentation map are described
