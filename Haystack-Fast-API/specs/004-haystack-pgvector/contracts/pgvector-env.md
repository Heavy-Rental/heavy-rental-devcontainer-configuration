# Contract: pgvector platform environment

**Feature**: `004-haystack-pgvector`  
**Consumer**: Operators, future haystack-fast-api I0/I1 DocumentStore wiring

## Postgres service (`postgres-haystack`)

| Item | Value |
|------|--------|
| Image | `pgvector/pgvector:pg17` |
| Container name | `postgres-haystack` |
| Database | `heavy_rental` |
| User / password (dev) | `postgres` / `postgres` |
| Host port | **5434** |
| Required extension | `vector` |
| Init script | `.devcontainer/initdb/01-create-vector-extension.sql` → `/docker-entrypoint-initdb.d/` |
| Healthcheck | `CREATE EXTENSION IF NOT EXISTS vector` then `pg_isready` |

## App container (`haystack-fast-api`)

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `DATABASE_URL` | yes | `postgresql://postgres:postgres@postgres-haystack:5432/heavy_rental` | Relational + future Pgvector connection |
| `INDEXING_EMBEDDING_DIM` | no* | `768` | Dim contract for future vector columns / embedder (*set in Compose for this pack) |

### Not set by this platform step

| Name | Notes |
|------|--------|
| `INDEXING_DOCUMENT_STORE` | I0 in application repo (`memory` \| `pgvector`) |
| Pgvector table / index names | Owned by app / Haystack integration |

## Sync service

| Item | Value |
|------|--------|
| Service | `postgres-haystack-sync` |
| Image | `postgres:17` (client tools; no pgvector required) |
| Target host | `postgres-haystack` |

## Peer REST primary

| Item | Value |
|------|--------|
| Container | `postgres-primary` |
| pgvector required? | **No** |

## Operator one-shot (if extension missing)

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Dim change policy

If `INDEXING_EMBEDDING_DIM` changes after I1 tables exist, operators MUST migrate or recreate vector columns; platform only documents the env contract.
