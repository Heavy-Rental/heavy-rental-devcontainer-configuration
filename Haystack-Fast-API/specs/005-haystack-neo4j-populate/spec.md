# Feature Specification: Fleet Neo4j Populate (SQL → Cypher MERGE)

**Feature Branch**: `005-haystack-neo4j-populate`

**Created**: 2026-08-13

**Status**: Implemented (T3 populate + T4 trigger / KG-1 protect)

**Input**: Phase 8 T3 / PR-L 8.1 — SQL → Cypher MERGE fleet projection.  
Phase 8.2 T4 / PR-M — trigger after successful sync or admin HTTP; scoped delete; never drop KG-1 labels.

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

### User Story 4 - Trigger after successful sync (Priority: P1) — T4

As an operator, when merge-sync completes successfully, fleet Neo4j populate is triggered without blocking or failing the sync job.

**Acceptance Scenarios**:

1. **Given** `NEO4J_POPULATE_TRIGGER_URL` is set and populate is healthy, **When** a merge cycle succeeds, **Then** sync logs `TRIGGER neo4j-populate status=ok`.
2. **Given** populate is down, **When** a merge cycle succeeds, **Then** sync logs trigger fail/skip and the cycle remains `status=success`.

### User Story 5 - Admin HTTP trigger (Priority: P1) — T4

As an operator, I can force a populate cycle via HTTP.

**Acceptance Scenarios**:

1. **Given** populate is running, **When** I `POST /v1/populate`, **Then** the service accepts (202) and runs a cycle.

### User Story 6 - Never drop KG-1 (Priority: P1) — T4

As a developer using project KG-1 / DocumentStore, rebuild and orphan delete never remove protected labels.

**Acceptance Scenarios**:

1. **Given** a `:Document` node and `KG1_PROTECTED_LABELS=Document`, **When** populate runs `rebuild`, **Then** the Document node remains.

## Requirements

- **FR-001**: Compose MUST include a `neo4j-populate` service that reads from `postgres-haystack` and writes to `neo4j` on `heavy-rental-network`.
- **FR-002**: Populate MUST use parameterized Cypher **`MERGE`** keyed by node `id` for fleet tables.
- **FR-003**: Default table allowlist MUST be `asset,booking,category` (D0), overridable via `FLEET_TABLE_ALLOWLIST`.
- **FR-004**: Default fleet labels MUST be `Asset`, `Booking`, `Category` (`FLEET_LABELS`).
- **FR-005**: Populate MUST NOT delete or rewrite non-fleet labels; rebuild MUST be label-scoped only.
- **FR-006**: Populate MUST NOT write DocumentStore embeddings/content or clear the entire graph.
- **FR-007**: Missing tables or missing `id` columns MUST skip that table without failing the whole cycle hard.
- **FR-008**: Default poll interval MUST be 60s (`POPULATE_INTERVAL_SECONDS`), overridable when interval mode is enabled.
- **FR-009**: Each cycle MUST log metrics including `duration_ms`, mode, and merge counts.
- **FR-010**: Spec Kit MUST document env and fleet-graph isolation contracts.
- **FR-011** (T4): After a **successful** merge-sync cycle, the sync job MUST best-effort HTTP-trigger populate when `NEO4J_POPULATE_TRIGGER_URL` is set; trigger failure MUST NOT fail sync.
- **FR-012** (T4): `neo4j-populate` MUST expose admin HTTP `POST /v1/populate` (and `GET /health`).
- **FR-013** (T4): Populate MUST honor `KG1_PROTECTED_LABELS` (default `Document`) and MUST never delete or write those labels.
- **FR-014** (T4): Scoped delete (rebuild / optional orphan prune) MUST apply only to fleet labels minus protected labels.

## Success Criteria

- **SC-001**: `neo4j-populate` is defined in Compose with health dependencies on Postgres and Neo4j.
- **SC-002**: Seed fleet rows appear as fleet-labeled nodes after a successful cycle.
- **SC-003**: DocumentStore / KG-1 nodes survive populate (including rebuild).
- **SC-004**: Contracts and verification runbook exist under Spec Kit 005.
- **SC-005**: Operators can change interval, mode, and allowlist via env.
- **SC-006** (T4): Successful sync can trigger populate without failing sync.
- **SC-007** (T4): Admin HTTP can force one-shot populate.
- **SC-008** (T4): KG-1 protected labels are never dropped.

## Assumptions

- Source of truth for fleet SQL remains REST primary → merge-sync → `postgres-haystack`.
- Application agent `trigger_neo4j_populate` wiring (S8.3) may call this pack’s HTTP surface.
- Shared Neo4j database is acceptable when KG-1 / KG-2 labels are isolated.
