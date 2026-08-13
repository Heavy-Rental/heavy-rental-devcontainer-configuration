# Design: Populate Neo4j from Haystack (Phase 8 T3)

## Decisions

| Topic | Decision |
|-------|----------|
| Source | `postgres-haystack` (post merge-sync) |
| Write | Parameterized Cypher `MERGE` by `id` |
| Labels | `Asset`, `Booking`, `Category` |
| Isolation | Label-scoped ops only; no global delete |
| Runtime | Python worker + bash entrypoint; Compose service |
| Interval | 60s default (aligned with merge-sync poll) |
| Modes | `merge` (default), `rebuild` (fleet labels only) |
| Metrics | Log-only `METRICS populate` |

## Data flow

```text
postgres-haystack public (asset, booking, category)
        │  SELECT *
        ▼
neo4j-populate (populate_neo4j.py)
        │  MERGE (n:Label {id}) SET n += props
        ▼
neo4j-haystack
  Fleet: :Asset :Booking :Category
  DocumentStore: :Document … (untouched)
```

## Failure modes

- Missing table / no `id`: skip table; continue cycle.
- Postgres or Neo4j down: skip cycle; sleep; retry.
- Unknown columns: coerced to scalars; dynamic projection.
