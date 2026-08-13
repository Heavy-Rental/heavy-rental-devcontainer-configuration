# Feature Specification: Fleet Neo4j Populate (SQL → Cypher MERGE)

**Feature Branch**: `005-haystack-neo4j-populate`

**Created**: 2026-08-13

**Status**: Implemented

**Input**: Phase 8 T3 / PR-L 8.1 — populate Neo4j fleet projection from Haystack local Postgres; isolate fleet labels from DocumentStore.

## User Scenarios & Testing

### User Story 1 - Fleet graph from local mirror (Priority: P1)

As a Haystack developer, after fleet rows exist on `postgres-haystack`, Neo4j contains matching `:Asset` / `:Booking` / `:Category` nodes without manual Cypher.

**Independent Test**: Seed rows in local Postgres; wait for populate interval; Cypher count > 0.

**Acceptance Scenarios**:

1. **Given** `postgres-haystack` has rows in allowlisted tables with an `id` column, **When** a populate cycle succeeds, **Then** corresponding fleet-labeled nodes exist in Neo4j.
2. **Given** the same rows on a second cycle, **When** MERGE runs again, **Then** node counts stay stable (idempotent).

### User Story 2 - DocumentStore isolation (Priority: P1)

As a developer using `neo4j-haystack` DocumentStore on the same Neo4j instance, fleet populate never deletes or rewrites document nodes.

**Independent Test**: Create `(:Document)`; run populate including rebuild; Document remains.

**Acceptance Scenarios**:

1. **Given** a non-fleet node (e.g. `:Document`), **When** populate runs in `merge` or `rebuild` mode, **Then** that node still exists.
2. **Given** rebuild mode, **When** fleet labels are cleared, **Then** only fleet labels are deleted (no full-graph wipe).

### User Story 3 - Soft dependency failures (Priority: P2)

As an operator, if Postgres or Neo4j is briefly down, the populate job skips the cycle and retries instead of crash-looping the stack.

**Acceptance Scenarios**:

1. **Given** Neo4j is stopped, **When** a cycle runs, **Then** logs show skip and the process continues after the interval.

## Requirements

- **FR-001**: Compose MUST include a `neo4j-populate` service that reads from `postgres-haystack` and writes to `neo4j` on `heavy-rental-network`.
- **FR-002**: Populate MUST use parameterized Cypher **`MERGE`** keyed by node `id` for fleet tables.
- **FR-003**: Default table allowlist MUST be `asset,booking,category` (D0), overridable via `FLEET_TABLE_ALLOWLIST`.
- **FR-004**: Default fleet labels MUST be `Asset`, `Booking`, `Category` (`FLEET_LABELS`).
- **FR-005**: Populate MUST NOT delete or rewrite non-fleet labels; rebuild MUST be label-scoped only.
- **FR-006**: Populate MUST NOT write DocumentStore embeddings/content or clear the entire graph.
- **FR-007**: Missing tables or missing `id` columns MUST skip that table without failing the whole cycle hard.
- **FR-008**: Default poll interval MUST be 60s (`POPULATE_INTERVAL_SECONDS`), overridable.
- **FR-009**: Each cycle MUST log metrics including `duration_ms`, mode, and merge counts.
- **FR-010**: Spec Kit MUST document env and fleet-graph isolation contracts.

## Success Criteria

- **SC-001**: `neo4j-populate` is defined in Compose with health dependencies on Postgres and Neo4j.
- **SC-002**: Seed fleet rows appear as fleet-labeled nodes after a successful cycle.
- **SC-003**: DocumentStore nodes survive populate (including rebuild).
- **SC-004**: Contracts and verification runbook exist under Spec Kit 005.
- **SC-005**: Operators can change interval, mode, and allowlist via env.

## Assumptions

- Source of truth for fleet SQL remains REST primary → merge-sync → `postgres-haystack`.
- Application `trigger_neo4j_populate` wiring is separate (app repo).
- Shared Neo4j database is acceptable when labels are isolated.
