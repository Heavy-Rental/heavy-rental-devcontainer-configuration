# ADR-0002: REST `postgres-primary` is the OLTP source of truth

- Status: accepted
- Date: 2026-08-20
- Tags: data, oltp, trust-boundary

## Context

Fleet domain rows (assets, bookings, categories, and later tables) need one writer for product CRUD. Haystack needs those rows for recommend / graph / vector work. Sharing one database between Spring and Haystack would couple OLTP schema, vector extensions, and experimental local writes.

## Decision

**`postgres-primary` (database `heavy_rental`) owned by the REST API pack is the only product OLTP source of truth.** Spring is the only intended product writer. Haystack MAY **read** primary over `heavy-rental-network` for merge-sync. Haystack MUST NOT write primary. Haystack MUST NOT treat `postgres-haystack` as product SoT.

## Consequences

- Fleet data bugs are fixed in Spring + primary, not by editing the Haystack mirror.
- Haystack local-only rows are sandbox features under default merge mode.
- REST pack does not run merge-sync, pgvector, or Neo4j populate.
- Schema contract is producer (REST) / consumer (Haystack).

## Related

- ADR-0003 (local Haystack Postgres)
- OpenSpec: `Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md`
- Contract: `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`
