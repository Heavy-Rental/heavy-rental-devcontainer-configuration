# ADR-0004: Fleet mirror is a near-real-time poll, not CDC

- Status: accepted
- Date: 2026-08-20
- Tags: haystack, sync, operations

## Context

Near-real-time fleet awareness is required for recommend / graph work. Logical replication / CDC would need publications on the REST primary, slot management, and operational complexity inappropriate for local Dev Containers. An original 24-hour cadence was too slow for fleet LTM.

When primary is down, halt-by-default plus `restart: unless-stopped` caused restart storms. Skip-and-retry is safer for local use.

## Decision

Use a **scheduled poll** (default `SYNC_INTERVAL_SECONDS=60`), not CDC or streaming replication, for Haystack merge-sync. Default when primary is unreachable: **skip the cycle**, leave local data intact, sleep, retry. Opt-in `HALT_ON_PRIMARY_UNAVAILABLE=true` may halt the job. Sync service uses `restart: unless-stopped`.

Expected max visibility lag is approximately the poll interval plus cycle duration (logged as `expected_max_lag_seconds` / `duration_ms`). Prometheus is not required.

## Consequences

- Operators get near-RT without primary WAL/publication changes.
- Lag is bounded by poll, not “real-time”.
- Skip-by-default means a down REST stack does not brick Haystack.

## Related

- ADR-0003
- OpenSpec archive: `Haystack-Fast-API/openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/`
- Phase 4 metrics: `Haystack-Fast-API/openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/`
