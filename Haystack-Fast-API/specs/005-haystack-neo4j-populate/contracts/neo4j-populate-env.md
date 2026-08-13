# Contract: Neo4j populate environment

**Feature**: `005-haystack-neo4j-populate`  
**Consumer**: Operators, `neo4j-populate` Compose service, `postgres-haystack-sync` trigger  
**Versions**: T3 (SQL→MERGE) · **T4** (post-sync / admin HTTP, KG-1 protect)

## Postgres source

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `PGHOST` / `TARGET_HOST` | yes | `postgres-haystack` | Local Haystack DB host |
| `PGPORT` / `TARGET_PORT` | no | `5432` | Port |
| `PGUSER` / `TARGET_USER` | yes | `postgres` | User |
| `PGPASSWORD` / `TARGET_PASSWORD` | yes | `postgres` | Password (dev) |
| `PGDATABASE` / `TARGET_DB` | yes | `heavy_rental` | Database |

## Neo4j target

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `NEO4J_URI` | yes | `bolt://neo4j:7687` | Bolt URL |
| `NEO4J_USER` | yes | `neo4j` | User |
| `NEO4J_PASSWORD` | yes | `heavyrental` | Password (dev) |
| `NEO4J_DATABASE` | no | `neo4j` | Database name |

## Populate behavior

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `FLEET_TABLE_ALLOWLIST` | no | `asset,booking,category` | Comma list of `public` tables |
| `FLEET_LABELS` | no | `Asset,Booking,Category` | KG-2 labels allowed for write/delete |
| `KG1_PROTECTED_LABELS` | no | `Document` | **Never** write or delete these labels |
| `POPULATE_MODE` | no | `merge` | `merge` or `rebuild` (fleet-scoped clear) |
| `POPULATE_TRIGGER_MODE` | no | `both` | `event` \| `interval` \| `both` |
| `POPULATE_INTERVAL_SECONDS` | no | `60` | Interval loop when mode is `interval` or `both` |
| `POPULATE_ORPHAN_DELETE` | no | `false` | Fleet-only prune of nodes missing from SQL |
| `POPULATE_HTTP_PORT` | no | `8089` | Admin HTTP listen port |
| `POPULATE_HTTP_ENABLED` | no | `true` | Serve admin HTTP |
| `POPULATE_HTTP_TOKEN` | no | empty | If set, require `X-Populate-Token` |
| `POPULATE_ONCE` | no | `false` | One cycle then exit |

## Sync-side trigger (Phase 8.2 T4)

On **`postgres-haystack-sync`**:

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `NEO4J_POPULATE_TRIGGER_URL` | no | `http://neo4j-populate:8089/v1/populate` | Empty disables |
| `NEO4J_POPULATE_TRIGGER_TIMEOUT_SECONDS` | no | `5` | curl timeout |
| `NEO4J_POPULATE_TRIGGER_TOKEN` | no | empty | Optional `X-Populate-Token` |

Trigger is **best-effort**: failed HTTP never fails the merge cycle.

## Admin HTTP

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness |
| `GET` | `/v1/status` | Last cycle metrics |
| `POST` | `/v1/populate` | Start one cycle (`?mode=merge\|rebuild` or JSON body); returns **202** |

```bash
curl -X POST http://localhost:8089/v1/populate
curl -X POST 'http://localhost:8089/v1/populate?mode=rebuild'
python3 /usr/local/bin/populate_neo4j.py --once
```
