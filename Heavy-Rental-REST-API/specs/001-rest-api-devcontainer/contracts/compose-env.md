# Contract: Compose / app environment

## App service environment (`heavy-rental-rest-api`)

| Name | Value | Notes |
|------|--------|--------|
| `POSTGRES_USER` | `postgres` | Dev |
| `POSTGRES_PASSWORD` | `postgres` | Dev |
| `POSTGRES_DB` | `heavy_rental` | |
| `POSTGRES_HOSTNAME` | `db-primary` | |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://db-primary:5432/heavy_rental` | Always primary |
| `SPRING_DATASOURCE_USERNAME` | `postgres` | |
| `SPRING_DATASOURCE_PASSWORD` | `postgres` | |

## Host ports

| Port | Target | Pack |
|------|--------|------|
| `5432` | Primary Postgres | both |
| `5433` | Replica Postgres | with-replica only |
| `8080` | App (forwardPorts) | both |

## Replica-only env (`db-replica-one`)

| Name | Default |
|------|---------|
| `REPLICATION_USER` | `replicator` |
| `REPLICATION_PASSWORD` | `replicatorpass` |
| `PRIMARY_HOST` | `db-primary` |
| `PRIMARY_PORT` | `5432` |

## Network

| Name | Type |
|------|------|
| `heavy-rental-network` | External bridge (must pre-exist) |
