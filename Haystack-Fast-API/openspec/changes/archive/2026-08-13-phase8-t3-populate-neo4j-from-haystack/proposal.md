# Proposal: Phase 8 T3 / PR-L 8.1 — populate Neo4j from Haystack Postgres

## Intent

Close **Phase 8 T3** (config pack) for fleet graph projection:

1. SQL → Cypher **`MERGE`** from `postgres-haystack` into Neo4j.
2. Fleet labels (`:Asset`, `:Booking`, `:Category`) **isolated** from DocumentStore.
3. Compose service + Spec Kit contracts for operators.

## Scope

### In scope

- `neo4j-populate` Compose service + `Dockerfile.neo4j-populate`
- Scripts `populate_neo4j.py` / `populate-neo4j-from-haystack.sh`
- Spec Kit `005-haystack-neo4j-populate`
- OpenSpec SoT requirement for fleet populate
- Operator README / verification

### Out of scope

- Application `trigger_neo4j_populate` real backend (app repo)
- CDC / outbox (Phase 9)
- DocumentStore indexing pipelines
- Attachment / compatibility graph beyond D0 tables
- Prometheus metrics

## Approach

1. Interval poll job reads allowlisted `public` tables from local Postgres.
2. Parameterized Cypher `MERGE` by `id` into fleet labels only.
3. Rebuild mode is label-scoped (never full-graph wipe).
4. Soft-skip when Postgres or Neo4j unavailable.

## Related artifacts

- Spec Kit: `specs/005-haystack-neo4j-populate/`
- SoT: `openspec/specs/haystack-devcontainer/spec.md`
- Feasibility (app): Plane A Neo4j populate / KG-2
