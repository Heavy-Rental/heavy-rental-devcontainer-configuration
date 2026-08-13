# Contract: Fleet graph isolation (KG-2 projection)

**Feature**: `005-haystack-neo4j-populate`  
**Version**: `1.0`  
**Status**: Frozen for Phase 8 T3 / PR-L 8.1

## Purpose

Bind SQL D0 fleet tables to Neo4j fleet labels and guarantee isolation from Haystack DocumentStore usage on the same Neo4j instance.

## Mapping

| SQL table | Neo4j label | MERGE property |
|-----------|-------------|----------------|
| `asset` | `Asset` | `id` |
| `booking` | `Booking` | `id` |
| `category` | `Category` | `id` |

## Isolation rules

1. Populate MAY create/update/delete only labels listed in `FLEET_LABELS` (default above).
2. Populate MUST NOT run global deletes (`MATCH (n) DETACH DELETE n`).
3. Rebuild mode MUST delete only fleet labels, then MERGE again.
4. Populate MUST NOT write DocumentStore node shapes (embeddings, chunk content pipelines).
5. Nodes MAY share the default database `neo4j`; isolation is by **label**, not by database name (v1).

## Provenance

Fleet nodes SHOULD carry:

- `_source = 'fleet-mirror'`
- `_populated_at` (datetime)

## Non-goals

- App-side job orchestration / `trigger_neo4j_populate`
- Attachment / compatibility subgraph beyond D0
- Bidirectional graph → SQL sync
