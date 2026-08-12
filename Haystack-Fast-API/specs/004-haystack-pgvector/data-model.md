# Data Model: pgvector platform

**Feature**: `004-haystack-pgvector`

## Entities (platform)

### Local Postgres with pgvector

| Field | Value |
|-------|--------|
| Compose service | `postgres-haystack` |
| Container | `postgres-haystack` |
| Image | `pgvector/pgvector:pg17` |
| Database | `heavy_rental` |
| Host port | **5434** → 5432 |
| Volume | `postgres-haystack-data` |
| Extension | `vector` (pgvector) |

### Embedding dim contract

| Field | Value |
|-------|--------|
| Env (app) | `INDEXING_EMBEDDING_DIM` |
| Default | `768` |
| Consumer (future) | App embedder + `PgvectorDocumentStore` column dim (I1) |

### Not owned by this feature

| Entity | Owner |
|--------|--------|
| Haystack document / embedding tables | **App** (I1) when factory writes Pgvector |
| Fleet tables (`asset`, `booking`, `category`) | Merge-sync from primary (`001`) |
| Neo4j graph nodes | Neo4j service (`002`) |

## Relationships

```text
postgres-primary (REST, no pgvector required)
        │  merge-sync allowlist
        ▼
postgres-haystack (pgvector platform)
        ├── public.* fleet mirror tables
        └── (future) project document/vector tables — app I1
```
