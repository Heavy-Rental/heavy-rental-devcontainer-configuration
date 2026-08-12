# Delta: haystack-devcontainer (Phase 4 allowlist + metrics + D0)

## ADDED Requirements

### Requirement: Deterministic fleet table allowlist (Phase 4 T2)

The sync process MUST default to merging only tables listed in `SYNC_TABLE_ALLOWLIST` (default `asset,booking,category` per D0 schema contract). Values `all` or `*` MUST enable full `public` schema merge. Non-allowlisted tables MUST be skipped (and SHOULD be excluded from FDW import via `LIMIT TO` when the list is finite).

#### Scenario: Default allowlist merges fleet tables only

- **GIVEN** default `SYNC_TABLE_ALLOWLIST=asset,booking,category`
- **WHEN** a successful sync cycle completes
- **THEN** only allowlisted, mergeable tables are required to be merged
- **AND** other public tables are not required to appear or update locally

#### Scenario: Full public override

- **GIVEN** `SYNC_TABLE_ALLOWLIST` is `all` or `*`
- **WHEN** the sync process runs
- **THEN** all mergeable public tables are eligible for merge

### Requirement: Cycle lag and duration metrics (Phase 4 T1)

Each sync cycle MUST log wall-clock duration (`duration_ms`) and a poll-based lag expectation (`expected_max_lag_seconds` approximately equal to `SYNC_INTERVAL_SECONDS`). Merge cycles SHOULD log allowlist-related counts. Prometheus exposition is not required.

#### Scenario: Metrics line after cycle

- **GIVEN** a sync cycle completes (success, skip, fail, or halt)
- **WHEN** the operator reads sync container logs
- **THEN** a metrics line includes `duration_ms` and interval / expected lag fields

### Requirement: D0 schema contract published

Spec Kit MUST publish a versioned fleet domain schema contract (`specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`) that binds default allowlist tables to the REST API producer contract.

#### Scenario: Contract present

- **GIVEN** a checkout of this repository
- **WHEN** an operator opens the Haystack merge-sync contracts folder
- **THEN** `schema-contract.md` exists at version 1.0 and documents default allowlist tables
