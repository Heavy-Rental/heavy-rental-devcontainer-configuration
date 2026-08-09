# Research: REST API Devcontainer Packs

## Why two packs

| Pack | Rationale |
|------|-----------|
| **Without replica** | Lower resource use; enough for CRUD API work against one Postgres |
| **With read replica** | Local streaming standby for HA/read-scale learning and optional read traffic |

**Decision:** Ship both as nested packs; operator promotes one `.devcontainer` to the project root (`Heavy-Rental-REST-API/`).

## Why promote “up one level”

Dev Containers resolve config from the opened folder’s `.devcontainer`. Nested pack folders avoid overwriting a single default and make preference explicit.

## Streaming replica approach (with-replica pack)

- Primary: `wal_level=replica`, replication slots, `replicator` role (`init-primary.sql`)
- Replica: `pg_basebackup` + `standby.signal` + `primary_conninfo` / `primary_slot_name=replica_slot` (`init-secondary.sh`)
- Host map **5433** avoids clashing with primary **5432**

## App still writes to primary

Default Spring datasource always targets `db-primary`. Replica is network-visible and IDE-profiled for reads; multi-datasource Spring config is app-level.

## As-built leftover

Without-replica `docker-compose.yml` declares volume `postgres-replica-one-data` without a replica service. Harmless; optional cleanup.

## Alternatives considered

| Option | Why not default |
|--------|------------------|
| Single pack with optional replica profile flag | Harder for operators who only unzip/copy folders; two explicit packs are clearer |
| Logical replication | Overkill for local standby demo; physical streaming matches current scripts |
