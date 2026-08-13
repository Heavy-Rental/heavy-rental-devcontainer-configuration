# Design: Neo4j populate trigger (Phase 8.2 T4)

## Decisions

| Topic | Decision |
|-------|----------|
| Transport | HTTP on `neo4j-populate:8089` |
| Sync coupling | Best-effort POST; no depends_on hard fail |
| Default mode | `POPULATE_TRIGGER_MODE=both` (event + interval) |
| KG-1 protect | `KG1_PROTECTED_LABELS=Document` denylist |
| Scoped delete | rebuild + optional orphan prune, fleet only |
| Sync image | `Dockerfile.postgres-sync` = postgres:17 + curl |

## Flow

```text
merge success → POST /v1/populate → background MERGE (KG-2)
admin curl   → same
interval     → optional safety net
```

## Failure modes

- Populate down: sync logs `TRIGGER … status=fail`, merge still success.
- Overlap fleet ∩ protected: refuse write/delete for those labels.
- Empty SQL keep_ids with orphan delete: skip mass-delete (use rebuild).
