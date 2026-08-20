# ADR-0008: One Neo4j instance; KG-1 DocumentStore isolated from KG-2 fleet

- Status: accepted
- Date: 2026-08-20
- Tags: haystack, neo4j, graph

## Context

Haystack uses Neo4j for project DocumentStore (KG-1, default label `:Document`) and also needs a fleet graph (KG-2: assets, bookings, categories). Two Neo4j instances would double RAM and operator burden in a Dev Container. Populate that ran global `DETACH DELETE` would destroy project knowledge.

## Decision

Run **one** Neo4j 5 Community service (`neo4j` / `neo4j-haystack`) in the Haystack pack. Project fleet rows from **`postgres-haystack`** (not primary) via `neo4j-populate` using Cypher **`MERGE` keyed by `id`**.

Isolation:

- Populate MAY write/delete only `FLEET_LABELS` minus `KG1_PROTECTED_LABELS` (default `Document`).
- Rebuild and orphan prune are **label-scoped**. Never `MATCH (n) DETACH DELETE n`.
- Triggers: best-effort POST after successful SQL merge, admin HTTP `:8089`, optional interval. Trigger failure MUST NOT fail the SQL merge.

Neo4j complements Postgres; it does not replace the relational store.

## Consequences

- One Bolt/Browser pair (`7687` / `7474`) for both graph planes.
- Fleet graph can lag SQL by poll + populate latency.
- Default D0 labels are `:Asset`, `:Booking`, `:Category` (ADR-0009). Expanding labels requires a spec + contract change.

## Related

- Spec Kit: `Haystack-Fast-API/specs/002-haystack-neo4j/`, `005-haystack-neo4j-populate/`
- Contract: `Haystack-Fast-API/specs/005-haystack-neo4j-populate/contracts/fleet-graph-contract.md`
