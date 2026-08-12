# Verification: pgvector platform (T5 / D4)

**Feature**: `004-haystack-pgvector`

## Preconditions

- External network `heavy-rental-network` exists
- Haystack Compose stack running (`postgres-haystack` healthy)

## Checks

### SC-001 — Extension present

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

Expect: one row for `vector`.

### SC-002 — Writable local DB + app URL

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "SELECT pg_is_in_recovery();"
# Expect: f

docker exec haystack-fast-api printenv DATABASE_URL
# Expect: ...@postgres-haystack:5432/heavy_rental
```

### SC-003 — Embedding dim env

```bash
docker exec haystack-fast-api printenv INDEXING_EMBEDDING_DIM
# Expect: 768
```

### SC-004 — Merge-sync and Neo4j still healthy

```bash
docker logs postgres-haystack-sync 2>&1 | tail -30
# Expect: cycle logs (merge or skip)

docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental 'RETURN 1;'
```

### SC-005 — Image tag

```bash
docker inspect postgres-haystack --format '{{.Config.Image}}'
# Expect: pgvector/pgvector:pg17
```

## Optional: vector type smoke (platform only)

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "SELECT '[1,2,3]'::vector;"
```

Expect: success (type available). No Haystack document table required.

## Operator notes

- Init scripts under `initdb/` run only on **first** data directory init.
- Healthcheck runs `CREATE EXTENSION IF NOT EXISTS vector` for upgraded volumes.
- REST primary does not need pgvector.
