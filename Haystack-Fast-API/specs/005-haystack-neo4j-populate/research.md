# Research: Fleet Neo4j Populate

## Context

Phase 4 mirrors fleet SQL into `postgres-haystack`. Neo4j already serves DocumentStore (`002`). Feasibility / app openspec call for **Plane A** async populate: SQL → Cypher MERGE (KG-2 fleet projection) without blocking recommend.

## Options considered

| Approach | Pros | Cons |
|----------|------|------|
| Full graph wipe then reload | Simple | Destroys DocumentStore data |
| Separate Neo4j database `fleet` | Strong isolation | Extra ops complexity for dev |
| **Label-scoped MERGE (chosen)** | Shares Bolt/Browser; isolates by label | Requires discipline in Cypher |

## Decisions

1. **Source = postgres-haystack** (post merge-sync), not primary.
2. **MERGE by `id`** for idempotent upserts.
3. **Fleet labels** `:Asset`, `:Booking`, `:Category` only.
4. **Rebuild** deletes only those labels.
5. **Python worker** for parameterized Cypher + JSON-safe coercion (bash+cypher-shell alone is brittle for dynamic columns).
6. **Interval poll** aligned with sync SLA (60s); not CDC.

## Related app work (not this pack)

- S7.2 `trigger_neo4j_populate` noop → real job trigger
- Recommend tools reading fleet graph
