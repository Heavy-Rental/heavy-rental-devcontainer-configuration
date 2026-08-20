# Proposal: Adopt OpenSpec spec-driven-with-adr, OpenSPDD, and durable ADRs

## Why

Pack behavior was specified in OpenSpec SoT + Spec Kit, but architectural *why* was archived with each change’s `design.md`, OpenSPDD implementation contracts did not exist, and the Web Portal pack had no specs. Future changes (and coding agents) re-discovered pull-vs-push, poll-vs-CDC, and KG isolation from memory.

## What Changes

- Add repo-root OpenSpec (`schema: spec-driven-with-adr`) with platform and documentation-governance capabilities
- Add durable `adr/` (ADR-0001–0010) extracted from as-built architecture
- Add OpenSPDD REASONS canvases under `spdd/`
- Add Web Portal OpenSpec + Spec Kit `001-web-portal-devcontainer`
- Document the three-layer workflow in `docs/spec-governance.md` and cross-link pack READMEs / `ARCHITECTURE.md`

## Capabilities

### New Capabilities

- `platform-devcontainers` — shared network, pack roles, trust boundaries
- `documentation-governance` — OpenSpec + OpenSPDD + ADR rules
- `web-portal-devcontainer` — pack-level (under `Heavy-Rental-Web-Portal/openspec/`)

### Modified Capabilities

- None at Haystack / REST SoT requirement level (cross-links and config.yaml only)

## Impact

Documentation and specification only. No Compose service, port, or sync-job behavior change in this change.

## Related

- ADR-0010
- `docs/spec-governance.md`
