# Proposal: Add Web Portal devcontainer OpenSpec + Spec Kit

## Why

`ARCHITECTURE.md` and the portal README described the React pack, but unlike REST and Haystack there was no OpenSpec SoT, Spec Kit workbook, or ADR/OpenSPDD hook. Agents had no requirement scenarios for “no local DB” and “call Spring only”.

## What Changes

- OpenSpec capability `web-portal-devcontainer`
- Spec Kit `specs/001-web-portal-devcontainer/`
- Cross-links to ADR-0006 and `spdd/prompt/web-portal-devcontainer.md`

## Capabilities

### New Capabilities

- `web-portal-devcontainer`

### Modified Capabilities

- None (REST/Haystack SoT unchanged)

## Impact

Documentation only. Compose as-built.

## Related

- ADR-0006
- Root change `2026-08-20-adopt-openspec-openspdd-adr`
