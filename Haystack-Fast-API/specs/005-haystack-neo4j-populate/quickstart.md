# Quickstart: Fleet Neo4j Populate

## Prerequisites

1. `heavy-rental-network` exists.
2. Haystack stack started (`postgres-haystack`, `neo4j`, `neo4j-populate`).
3. Optional: REST API stack + merge-sync so fleet tables have data.

## Check the job

```bash
docker logs neo4j-populate --tail 50
```

Expect `METRICS populate status=ok` or soft `status=skip_pg` / `skip_neo4j` when deps are down.

## One-shot populate

```bash
docker exec neo4j-populate python3 /usr/local/bin/populate_neo4j.py --once
```

## Verify fleet nodes (Browser or cypher-shell)

```cypher
MATCH (a:Asset) RETURN count(a) AS assets;
MATCH (b:Booking) RETURN count(b) AS bookings;
MATCH (c:Category) RETURN count(c) AS categories;
```

## Isolation smoke

```cypher
CREATE (d:Document {id: 'doc-isolation-test'});
// wait for populate cycle or run --once with POPULATE_MODE=rebuild
MATCH (d:Document {id: 'doc-isolation-test'}) RETURN d;
```

Document node must still exist after rebuild.

## Env knobs

See [contracts/neo4j-populate-env.md](./contracts/neo4j-populate-env.md).

## Related

- DocumentStore / Bolt env: [../002-haystack-neo4j/quickstart.md](../002-haystack-neo4j/quickstart.md)
- SQL fleet mirror: [../001-haystack-postgres-merge-sync/quickstart.md](../001-haystack-postgres-merge-sync/quickstart.md)
