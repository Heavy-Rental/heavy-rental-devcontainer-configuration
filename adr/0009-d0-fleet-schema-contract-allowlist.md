# ADR-0009: D0 fleet schema contract and default allowlist

- Status: accepted
- Date: 2026-08-20
- Tags: schema, fleet, allowlist

## Context

Merging every `public` table from primary into Haystack is unsafe for a local sandbox (noise, secrets, non-fleet tables). Haystack and REST need a shared, versioned inventory so allowlists and Neo4j labels stay aligned. Spring/JPA physical names may differ from logical names.

## Decision

Publish a **D0 (Phase 4 freeze) schema contract v1.0**:

| Logical entity | Physical table (`public`) | Default mirror | Default Neo4j label |
|----------------|---------------------------|----------------|---------------------|
| Asset | `asset` | Yes | `:Asset` |
| Booking | `booking` | Yes | `:Booking` |
| Category | `category` | Yes | `:Category` |

- Producer: `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`
- Consumer: `Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`

Default `SYNC_TABLE_ALLOWLIST` and `FLEET_TABLE_ALLOWLIST` are `asset,booking,category`. Operators MAY set `SYNC_TABLE_ALLOWLIST=all` or `*` for full public merge (sandbox/debug). Expanding the **default** allowlist or renaming physical tables is a new contract version plus OpenSpec change (and a superseding ADR if the D0 freeze itself changes).

## Consequences

- Deterministic fleet LTM for Phase 4/8.
- Wrong physical names require env override **and** contract revision — env-only drift is not enough for a new default.
- `rental_plan` / `payment` and other tables stay off the default allowlist until a later freeze.

## Related

- ADR-0002, ADR-0003, ADR-0008
- OpenSpec archive: `Haystack-Fast-API/openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/`
