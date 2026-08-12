# Contract: Fleet domain schema (D0) — Haystack consumer

**Feature**: `001-haystack-postgres-merge-sync`  
**Contract version**: `1.0`  
**Status**: Frozen for Phase 4 / S4 (fleet LTM mirror)  
**Role**: **Consumer** — Haystack local DB (`postgres-haystack` / `heavy_rental`) receives a **merge mirror** of allowlisted primary tables.

**Producer SoT**:  
[`../../../Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`](../../../Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md)

## Purpose

Bind Phase **4.4 D0** inventory to Haystack merge-sync **T2 allowlist** and document lag expectations (**T1**).

## Default allowlist (T2)

Env: `SYNC_TABLE_ALLOWLIST` (see [db-sync-env.md](./db-sync-env.md)).

| Default value | Meaning |
|---------------|---------|
| `asset,booking,category` | Deterministic fleet LTM set (Phase 4 exit) |
| `all` or `*` | Merge all mergeable `public` tables (sandbox / debug) |

Physical names MUST match producer contract v1.0 unless operator overrides.

## Table inventory (mirrors producer v1.0)

| Logical entity | Physical table | Typical PK | Lag-sensitive fields | Default allowlist |
|----------------|----------------|------------|----------------------|-------------------|
| Asset | `asset` | `id` | status, category refs | Yes |
| Booking | `booking` | `id` | window, asset_id, status | Yes |
| Category | `category` | `id` | name/code | Yes |

## Lag / poll SLA (T1)

| Setting | Default | Notes |
|---------|---------|--------|
| `SYNC_INTERVAL_SECONDS` | `60` | Near-RT **poll**, not CDC |
| Expected max visibility lag | ≈ interval (+ cycle duration) | Logged as `expected_max_lag_seconds` / `duration_ms` |

Sync job logs per cycle: start time, `duration_ms`, allowlist metrics, merge/skip counts.

## Data plane rules

- Source: `postgres-primary` / `heavy_rental` / `public`
- Target: `postgres-haystack` / `heavy_rental`
- Merge: PK or UNIQUE upsert; local-only rows retained (default `SYNC_MODE=merge`)
- Non-allowlisted `public` tables: **not** imported or merged when allowlist is finite

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-08-12 | D0 freeze + default allowlist `asset,booking,category` + lag log fields |
