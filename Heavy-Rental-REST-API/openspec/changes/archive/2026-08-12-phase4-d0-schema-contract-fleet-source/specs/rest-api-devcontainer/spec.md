# Delta: rest-api-devcontainer (Phase 4 D0 + fleet source)

## ADDED Requirements

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
