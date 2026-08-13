# Contract: Fleet domain schema (D0) — REST API producer

**Feature**: `001-rest-api-devcontainer`  
**Contract version**: `1.0`  
**Status**: Frozen for Phase 4 / S4 (fleet LTM mirror)  
**Role**: **Producer** — Spring REST API primary (`postgres-primary` / `heavy_rental`) is the OLTP source of truth for shared fleet domain rows.

**Consumer binding**: Haystack merge-sync allowlist and read models  
→ [`../../../Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`](../../../Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md)

## Purpose

Inventory the domain tables needed for Haystack recommend / pricing / availability so:

1. Phase **4.4 D0** has a versioned freeze point.
2. Haystack `SYNC_TABLE_ALLOWLIST` defaults stay aligned with this inventory.
3. Later stages (S6 pricing, S7.1 fleet tools) implement against a known table set.

## Scope (v1.0)

| Logical entity | Physical table (`public`) | Typical PK | Lag-sensitive fields | Fleet-mirror default |
|----------------|---------------------------|------------|----------------------|----------------------|
| Asset | `asset` | `id` | `status`, category FK, pricing-related columns if present | **Yes** (allowlist) |
| Booking | `booking` | `id` | `start` / `end` (or equivalent), `asset_id`, `status` | **Yes** (allowlist) |
| Category | `category` | `id` | `name` / `code` | **Yes** (allowlist) |

Optional tables (not in default Haystack allowlist; document if Spring adds them later):

| Logical entity | Physical table | Notes |
|----------------|----------------|--------|
| Rental plan | `rental_plan` | Add to allowlist when used by pricing |
| Payment | `payment` | Usually not required for recommend LTM |

## Physical naming rule

- Names above are **exact Postgres relation names** expected in `public` on `postgres-primary`.
- If Spring/JPA uses different names (e.g. `assets`, quoted `"Asset"`), operators **MUST** override Haystack `SYNC_TABLE_ALLOWLIST` to match and update this contract in a v1.x revision.
- Primary key column names may vary; Haystack merge uses source PK or UNIQUE as merge key (see Haystack `db-sync-env.md`).

## Enums / status (indicative)

Exact Java enum constants live in the Spring application. For mirror consumers, treat status-like columns as **opaque strings** unless the Spring app documents a closed set.

| Area | Guidance |
|------|----------|
| Asset status | Lag-sensitive; mirror refresh drives availability accuracy |
| Booking status | Lag-sensitive; overlapping windows need near-RT poll (default 60s) |
| Category codes | Prefer stable codes over display names for tool filters |

## Network / instance identity (T0)

| Attribute | Value |
|-----------|--------|
| Container | `postgres-primary` |
| Compose service | `db-primary` |
| Database | `heavy_rental` |
| Network | `heavy-rental-network` (external) |
| Role for Haystack | **Read source only** — REST stack does **not** run a push/sync job |

## Non-goals (this contract)

- Full Flyway/Liquibase dump of every column
- Bidirectional sync or Spring→Haystack write-back
- Neo4j graph projection (Phase 8) — implemented on Haystack pack as `neo4j-populate` / Spec Kit `005-haystack-neo4j-populate` (not on this REST pack)
- Application entity Java source as the normative runtime SoT (OpenSpec app contracts may refine enums later)

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-12 | Initial D0 freeze: asset, booking, category for Phase 4 allowlist |
