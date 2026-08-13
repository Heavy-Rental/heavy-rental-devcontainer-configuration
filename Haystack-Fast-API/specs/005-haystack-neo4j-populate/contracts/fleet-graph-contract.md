# Contract: Fleet graph isolation (KG-2) vs project KG-1

**Feature**: `005-haystack-neo4j-populate`  
**Version**: `1.1` (T4)  
**Status**: Frozen for Phase 8 T3 + T4 / PR-L + PR-M

## Purpose

Bind SQL D0 fleet tables to Neo4j **KG-2** fleet labels and guarantee isolation from **KG-1** project knowledge / DocumentStore labels on the same Neo4j instance.

## Planes

| Plane | Name | Typical labels | Owner |
|-------|------|----------------|-------|
| **KG-1** | Project specification knowledge | `Document` (neo4j-haystack / ingest) | Application indexing |
| **KG-2** | Fleet / equipment stockpile | `Asset`, `Booking`, `Category` | `neo4j-populate` (this pack) |

## Mapping (KG-2)

| SQL table | Neo4j label | MERGE property |
|-----------|-------------|----------------|
| `asset` | `Asset` | `id` |
| `booking` | `Booking` | `id` |
| `category` | `Category` | `id` |

## Isolation rules

1. Populate MAY create/update/delete only labels listed in `FLEET_LABELS` **minus** `KG1_PROTECTED_LABELS`.
2. Populate MUST NOT run global deletes (`MATCH (n) DETACH DELETE n`).
3. Rebuild mode MUST delete only **scoped fleet** labels (never KG-1).
4. Optional orphan delete MUST only remove fleet nodes whose `id` is absent from SQL.
5. Populate MUST NOT write DocumentStore embeddings/content.
6. Default `KG1_PROTECTED_LABELS=Document` — **never drop KG-1 labels**.
7. If `FLEET_LABELS` overlaps protected labels, those labels are refused for write/delete.

## Provenance (KG-2 nodes)

- `_source = 'fleet-mirror'`
- `_populated_at` (datetime)

## Triggers (T4)

- After successful `postgres-haystack-sync` merge → best-effort `POST` to populate admin HTTP.
- Admin / operators / future app `trigger_neo4j_populate` → same HTTP surface.
- Interval poll remains an optional safety net (`POPULATE_TRIGGER_MODE=both`).

## Non-goals

- App-side agent tool wiring (S8.3)
- Attachment / compatibility subgraph beyond D0
- Bidirectional graph → SQL sync
- APOC in-database triggers
