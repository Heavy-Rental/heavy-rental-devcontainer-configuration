# Quickstart: pgvector platform

**Feature**: `004-haystack-pgvector`

## Prerequisites

1. Docker network: `docker network create heavy-rental-network` (if missing)
2. Open `Haystack-Fast-API` in Dev Containers (or `docker compose up` under `.devcontainer/`)
3. Optional: REST API stack for fleet merge-sync

## After stack is up

```bash
# Extension present
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

# Dim contract on app
docker exec haystack-fast-api printenv INDEXING_EMBEDDING_DIM
# Expect: 768
```

## Upgraded volume (was plain postgres:17)

Healthcheck creates the extension automatically. If needed:

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

If the image major/data directory is incompatible, backup and recreate volume `postgres-haystack-data`.

## Full verification

See [verification.md](./verification.md).

## Next (not this pack)

Application repo: I0 DocumentStore factory → I1 Pgvector writer + isolation.
