# Proposal: Phase 4 fleet mirror allowlist, lag metrics, and D0 schema contract

## Intent

Close Phase 4 / S4 remaining gaps for Haystack Postgres merge-sync:

1. **T1** — log cycle lag/duration metrics (near-RT poll already at 60s).
2. **T2** — deterministic table allowlist (`asset,booking,category` by default).
3. **D0** — versioned schema contract binding allowlist to fleet domain tables.

## Scope

### In scope

- `SYNC_TABLE_ALLOWLIST` on `postgres-haystack-sync` / `sync-from-primary.sh`
- FDW `LIMIT TO` when allowlist is finite
- Per-cycle `METRICS` log lines (`duration_ms`, `expected_max_lag_seconds`, merge counts)
- Spec Kit + OpenSpec updates; consumer `schema-contract.md`
- Peer REST API producer schema contract (separate pack)

### Out of scope

- CDC / outbox (Phase 9)
- Neo4j populate (Phase 8)
- Prometheus metrics endpoint
- Changing REST API Compose topology
- Spring application entity code

## Approach

1. Default Compose/env allowlist to D0 fleet tables; support `all`/`*` override.
2. Filter merge candidates; import only allowlisted relations into staging when finite.
3. Instrument every cycle with duration and poll lag notes.
4. Publish D0 contracts on both Haystack (consumer) and REST (producer) packs.

## Related artifacts

- Spec Kit: `specs/001-haystack-postgres-merge-sync/`
- SoT: `openspec/specs/haystack-devcontainer/spec.md`
- REST peer: `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`
