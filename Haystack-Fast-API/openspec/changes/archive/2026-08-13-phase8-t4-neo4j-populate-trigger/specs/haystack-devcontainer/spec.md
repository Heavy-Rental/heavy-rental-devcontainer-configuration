## ADDED Requirements

### Requirement: Fleet Neo4j populate trigger (Phase 8.2 T4)

After a **successful** merge-sync cycle, the sync process MUST best-effort trigger fleet Neo4j populate when `NEO4J_POPULATE_TRIGGER_URL` is set (default `http://neo4j-populate:8089/v1/populate`). Trigger failure MUST NOT fail or roll back the merge cycle.

The `neo4j-populate` service MUST expose admin HTTP including `POST /v1/populate` and `GET /health`. Populate MUST honor `KG1_PROTECTED_LABELS` (default `Document`) and MUST never delete or write those labels. Scoped delete (rebuild / optional orphan prune) MUST apply only to fleet labels minus protected labels.

#### Scenario: Post-sync trigger on success

- **GIVEN** merge completes successfully and the trigger URL is set
- **WHEN** the sync job finishes the cycle
- **THEN** it attempts an HTTP POST to the populate service
- **AND** merge cycle status remains success even if the POST fails

#### Scenario: Admin HTTP one-shot

- **GIVEN** `neo4j-populate` is running
- **WHEN** an operator POSTs `/v1/populate`
- **THEN** a populate cycle is accepted without requiring the interval timer

#### Scenario: KG-1 labels never dropped

- **GIVEN** a node with a protected KG-1 label such as `:Document`
- **WHEN** populate runs rebuild or orphan delete
- **THEN** that node still exists
