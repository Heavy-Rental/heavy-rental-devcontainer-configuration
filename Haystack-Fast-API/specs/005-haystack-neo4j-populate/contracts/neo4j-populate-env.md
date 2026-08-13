# Contract: Neo4j populate environment

**Feature**: `005-haystack-neo4j-populate`  
**Consumer**: Operators, `neo4j-populate` Compose service

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
| `FLEET_LABELS` | no | `Asset,Booking,Category` | Labels allowed for write/delete |
| `POPULATE_MODE` | no | `merge` | `merge` or `rebuild` |
| `POPULATE_INTERVAL_SECONDS` | no | `60` | Sleep between cycles |
| `POPULATE_ONCE` | no | `false` | If true, one cycle then exit |

`SYNC_TABLE_ALLOWLIST` is accepted as a fallback for `FLEET_TABLE_ALLOWLIST` when the latter is unset.

## CLI

```bash
# One-shot (container or image entrypoint)
POPULATE_ONCE=true /usr/local/bin/populate-neo4j-from-haystack.sh
# or
python3 /usr/local/bin/populate_neo4j.py --once
```
