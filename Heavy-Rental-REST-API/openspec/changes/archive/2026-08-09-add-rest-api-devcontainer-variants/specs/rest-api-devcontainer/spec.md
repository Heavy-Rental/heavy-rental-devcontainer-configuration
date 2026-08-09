# Delta for REST API Devcontainer

## ADDED Requirements

### Requirement: Dual pack distribution

Two pack folders MUST ship under `Heavy-Rental-REST-API/` (with and without PostgreSQL read replica).

### Requirement: Promote `.devcontainer` one level up

Operators MUST move the chosen pack’s `.devcontainer` to `Heavy-Rental-REST-API/.devcontainer` before opening Dev Containers.

### Requirement: Shared Compose stack baseline

App + primary Postgres + external network + Spring datasource to primary.

### Requirement: With-replica profile

Streaming standby `db-replica-one` on host 5433; IDE replica profile.

### Requirement: Without-replica profile

Primary only; no required replica service.
