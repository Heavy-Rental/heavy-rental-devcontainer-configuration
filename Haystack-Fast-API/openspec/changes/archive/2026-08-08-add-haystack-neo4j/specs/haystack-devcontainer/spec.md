# Delta for Haystack Devcontainer

## ADDED Requirements

### Requirement: Neo4j graph store for Haystack

The Haystack Compose stack MUST include a Neo4j 5 Community service on `heavy-rental-network` with persistent volume, Bolt and HTTP ports, and documented dev authentication. The application service MUST expose `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` for neo4j-haystack / driver clients.

#### Scenario: Neo4j service present

- **GIVEN** the Haystack stack is started
- **WHEN** services are inspected
- **THEN** a healthy `neo4j` service exists alongside `db` and `haystack-fast-api`

#### Scenario: App connection env

- **GIVEN** the app container is running
- **WHEN** environment variables are read
- **THEN** `NEO4J_URI` points at `bolt://neo4j:7687` with credentials matching Neo4j auth

## MODIFIED Requirements

### Requirement: Devcontainer Compose stack

The stack MUST include application, Postgres (`db` / `db-sync`), and Neo4j services on `heavy-rental-network`.

#### Scenario: Stack services with Neo4j

- **GIVEN** this configuration is deployed
- **WHEN** a developer inspects Compose services
- **THEN** `haystack-fast-api`, `db`, `db-sync`, and `neo4j` are defined
