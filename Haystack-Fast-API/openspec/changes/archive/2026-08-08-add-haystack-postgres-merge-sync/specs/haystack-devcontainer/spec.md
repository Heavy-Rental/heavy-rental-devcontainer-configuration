# Delta for Haystack Devcontainer

## REMOVED Requirements

### Requirement: No local Postgres in baseline

(Superseded by local writable database and merge sync requirements below.)

## ADDED Requirements

### Requirement: Local writable database

The Haystack Compose stack MUST provide a local PostgreSQL 17 service that is fully writable and persists data in a dedicated Docker volume. The Haystack application service MUST use this local database as its default read/write data source.

#### Scenario: Local database accepts writes

- **GIVEN** the Haystack stack is running and the local database service is healthy
- **WHEN** a client connects with the configured local credentials to database `heavy_rental`
- **THEN** the client can insert, update, select, and delete rows
- **AND** the instance is not a read-only standby (`pg_is_in_recovery()` is false)

#### Scenario: Application uses local database

- **GIVEN** the `haystack-fast-api` service is configured via environment
- **WHEN** the application opens its default database connection
- **THEN** it connects to the local Compose database service (not `postgres-primary`)

### Requirement: Shared network reachability to REST API primary

The local database and sync components MUST join external network `heavy-rental-network` so they can reach container `postgres-primary` when the REST API stack is running.

#### Scenario: Source host resolution

- **GIVEN** both stacks are attached to `heavy-rental-network` and primary is running
- **WHEN** the sync process resolves `postgres-primary`
- **THEN** a TCP connection to port 5432 succeeds for connectivity checks

### Requirement: Merge sync from REST API primary

The system MUST provide a sync process that merge-refreshes data from `postgres-primary` database `heavy_rental` into the local database using primary-key (or unique-key) upserts. Primary MUST win on key conflicts. Local-only rows MUST be retained. Default behavior MUST NOT wipe local application tables.

#### Scenario: Source rows appear locally

- **GIVEN** primary is reachable and contains rows in mergeable tables
- **WHEN** a successful sync cycle completes
- **THEN** those rows are present locally (inserted if new, updated if same merge key)

#### Scenario: Local-only rows retained

- **GIVEN** a row exists only on the local database for a merge key not present on primary
- **WHEN** a successful sync cycle completes
- **THEN** that row still exists locally

#### Scenario: Shared key primary wins

- **GIVEN** the same merge key exists on primary and local with different non-key values
- **WHEN** a successful sync cycle completes
- **THEN** local non-key values match primary

#### Scenario: Primary deletes not mirrored

- **GIVEN** a row was removed on primary but still exists locally
- **WHEN** a successful sync cycle completes
- **THEN** the local row is not required to be deleted

### Requirement: Connectivity check before merge

Before modifying local application data, the sync process MUST detect whether `postgres-primary` is available, with configurable retries.

#### Scenario: Successful detection

- **GIVEN** primary accepts connections with configured credentials
- **WHEN** the sync process runs its connectivity check
- **THEN** the check succeeds and a merge cycle may proceed

#### Scenario: Failed detection after retries

- **GIVEN** primary is stopped or unreachable
- **WHEN** retries are exhausted
- **THEN** the process treats the source as unavailable and MUST NOT merge application tables in that cycle

### Requirement: Halt on primary unavailability

When the source is unavailable and halt mode is enabled (default), the sync process MUST leave local application data unchanged and MUST stop further scheduled merges for that process lifetime.

#### Scenario: Default halt

- **GIVEN** `HALT_ON_PRIMARY_UNAVAILABLE` is true (default) and primary cannot be detected
- **WHEN** the sync process evaluates connectivity
- **THEN** it logs a halt condition
- **AND** it does not modify local application tables
- **AND** the sync job stops scheduling further cycles

#### Scenario: Local database remains usable after halt

- **GIVEN** the sync job has halted
- **WHEN** the developer uses the Haystack app or `psql` against the local database
- **THEN** read and write operations still succeed

### Requirement: Skip cycle when halt disabled

When the source is unavailable and halt mode is disabled, the sync process MUST skip the merge, leave local data intact, wait for the configured interval, and retry.

#### Scenario: Skip and wait

- **GIVEN** `HALT_ON_PRIMARY_UNAVAILABLE` is false and primary cannot be detected
- **WHEN** the sync process evaluates connectivity
- **THEN** it logs a skip
- **AND** it sleeps for `SYNC_INTERVAL_SECONDS`
- **AND** it attempts another cycle afterward

### Requirement: Scheduled refresh every 24 hours

The sync process MUST attempt a merge cycle when it starts (after local DB readiness) and MUST wait 24 hours by default between subsequent attempts. The interval MUST be overridable via environment configuration.

#### Scenario: Initial attempt at start

- **GIVEN** the sync service starts and the local database is ready
- **WHEN** initialization completes
- **THEN** the process attempts a connectivity check and merge (or halt/skip) before the first full interval sleep

#### Scenario: Default interval

- **GIVEN** default configuration
- **WHEN** a cycle attempt finishes
- **THEN** the next attempt is scheduled after 86400 seconds

#### Scenario: Custom interval

- **GIVEN** `SYNC_INTERVAL_SECONDS` is set to a positive integer N
- **WHEN** a cycle attempt finishes
- **THEN** the next attempt is scheduled after N seconds

### Requirement: Operational logging

The sync process MUST log cycle outcomes including connectivity result, halt, skip, merge success/failure, and tables skipped (e.g. missing primary key).

#### Scenario: Operator can diagnose halt

- **GIVEN** primary is unavailable and halt mode is enabled
- **WHEN** the operator reads sync container logs
- **THEN** the logs clearly state that primary could not be detected and that the job is halting

## MODIFIED Requirements

### Requirement: Devcontainer Compose stack

The Haystack Fast API development environment MUST start via Docker Compose using `Haystack-Fast-API/.devcontainer/docker-compose.yml`, attach to the external network `heavy-rental-network`, and include the local database service and sync service defined by this change.

#### Scenario: Stack services after change

- **GIVEN** this change is implemented
- **WHEN** a developer inspects Compose services
- **THEN** `haystack-fast-api`, `db`, and `db-sync` are defined
- **AND** all join `heavy-rental-network`
