## ADDED Requirements

### Requirement: Fleet Neo4j populate from local Postgres (Phase 8 T3)

The Haystack Compose stack MUST provide a `neo4j-populate` process that projects allowlisted fleet tables from `postgres-haystack` (`heavy_rental` / `public`) into Neo4j using parameterized Cypher **`MERGE`** keyed by `id`. Default allowlist MUST be `asset,booking,category`. Default fleet labels MUST be `Asset`, `Booking`, `Category`.

Populate MUST isolate fleet labels from DocumentStore: it MUST NOT delete or rewrite non-fleet labels, MUST NOT clear the entire graph, and rebuild mode MUST be label-scoped only. Missing tables or missing `id` columns MUST be skipped without hard-failing the long-running job. The process MUST soft-skip when Postgres or Neo4j is unavailable and retry after `POPULATE_INTERVAL_SECONDS` (default 60).

Application DocumentStore factory wiring and app-side `trigger_neo4j_populate` orchestration are **not** required by this platform requirement.

#### Scenario: Fleet nodes merged from local SQL

- **GIVEN** `postgres-haystack` has rows in allowlisted tables with an `id` column and Neo4j is healthy
- **WHEN** a successful populate cycle completes
- **THEN** corresponding nodes exist under fleet labels in Neo4j

#### Scenario: DocumentStore nodes survive populate

- **GIVEN** a non-fleet node such as `:Document` exists in Neo4j
- **WHEN** populate runs in `merge` or `rebuild` mode
- **THEN** that non-fleet node still exists

#### Scenario: Service present on shared network

- **GIVEN** the Haystack stack is started
- **WHEN** Compose services are inspected
- **THEN** `neo4j-populate` is defined and joins `heavy-rental-network`

## MODIFIED Requirements

### Requirement: Devcontainer Compose stack

The Haystack Fast API development environment MUST start via Docker Compose using `Haystack-Fast-API/.devcontainer/docker-compose.yml`, attach to the external network `heavy-rental-network`, and include the application service, local Postgres (`postgres-haystack` / `postgres-haystack-sync`), Neo4j, and fleet Neo4j populate (`neo4j-populate`) services.

#### Scenario: Stack services

- **GIVEN** this configuration is deployed
- **WHEN** a developer inspects Compose services
- **THEN** `haystack-fast-api`, `postgres-haystack`, `postgres-haystack-sync`, `neo4j`, and `neo4j-populate` are defined
- **AND** all join `heavy-rental-network`
