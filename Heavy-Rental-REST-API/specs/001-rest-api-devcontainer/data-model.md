# Data Model: REST API Devcontainer

## Packs

| Pack folder | Profile key |
|-------------|-------------|
| `Spring Boot REST API devcontainer with PostgreSQL Read Replica` | `with-replica` |
| `Spring Boot REST API devcontainer without read replica` | `without-replica` |

## Services

### App (`both`)

| Attribute | Value |
|-----------|--------|
| Compose service | `heavy-rental-rest-api` |
| Container | `heavy-rental-rest-api` |
| Image build | `.devcontainer/Dockerfile` (Java 21 + Maven + Stripe CLI) |
| Stripe CLI | `stripe` on PATH; helper `/usr/local/bin/start-stripe-listen.sh` |
| Workspace volume | `heavy-rental-rest-api-data` → `/workspaces/heavy-rental-rest-api` |
| Network | `heavy-rental-network` (external) |
| Depends on | `db-primary` healthy |

### Primary Postgres (`both`)

| Attribute | Value |
|-----------|--------|
| Compose service | `db-primary` |
| Container | `postgres-primary` |
| Image | `postgres:17` |
| Volume | `postgres-primary-data` |
| Host port | `5432:5432` |
| DB / user / password | `heavy_rental` / `postgres` / `postgres` |
| Network alias | `db` |

### Replica Postgres (`with-replica` only)

| Attribute | Value |
|-----------|--------|
| Compose service | `db-replica-one` |
| Container | `postgres-replica-one` |
| Image | `postgres:17` |
| Volume | `postgres-replica-one-data` |
| Host port | `5433:5432` |
| Bootstrap | `postgres/replica/init-secondary.sh` |
| Role | Streaming standby (read) |

## IDE connection profiles

| Profile | Pack | Host (in container network) |
|---------|------|-----------------------------|
| `heavy-rental-rest-api-db-connection` | both | `db-primary:5432` |
| `Replica (Read)` | with-replica only | `db-replica-one:5432` |

## Fleet domain schema (Phase 4 D0)

Shared inventory for Haystack merge-sync allowlist (producer view):

**→ [contracts/schema-contract.md](./contracts/schema-contract.md)**

Default physical tables: `asset`, `booking`, `category` on primary `heavy_rental` / `public`.

Haystack **pulls** from `postgres-primary` on `heavy-rental-network`; this pack does not run a sync job.
