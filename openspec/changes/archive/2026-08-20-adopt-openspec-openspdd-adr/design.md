# Design: Adopt OpenSpec, OpenSPDD, and ADR

## Context

Existing pack OpenSpec used a lightweight spec-driven layout without `config.yaml` and without durable ADRs. Spec Kit workbooks are thorough but do not survive as architecture memory after a design is archived.

In-force ADRs reviewed: none existed; this change creates ADR-0001–0010.

## Goals / Non-Goals

**Goals:** three-layer contract (OpenSpec what, OpenSPDD how, ADR why); Web Portal parity; root platform spec.

**Non-goals:** installing `openspec` / `openspdd` CLIs in the Dev Container images; changing merge-sync allowlist or Neo4j labels; rewriting operator setup videos.

## Decisions

1. **Root `openspec/` + keep pack `openspec/`** — OpenSpec CLI conventionally wants a root folder; pack SoT is already the capability contract. Root holds platform + process only.
2. **ADRs only at repo `adr/`** — even for pack-scoped changes, so the sequence is global.
3. **REASONS canvases as as-built reverse specs** — `/spdd-reverse` style; new work uses `/spdd-reasons-canvas` naming under `spdd/prompt/`.
4. **Backfill ADRs from current SoT**, not from uncommitted allowlist experiments.

## Risks / Trade-offs

- [Duplication across ARCHITECTURE.md / OpenSpec / SPDD / ADR] → Each layer has a distinct question (narrative / MUST scenarios / implementation contract / why). Cross-link; do not copy full requirement lists into ADRs.
- [Agents ignore new folders] → Governance doc + pack README pointers + OpenSpec config schema.

## Migration Plan

Docs-only. No rollback of runtime.

## Open Questions

None. Default allowlist remains D0 `asset,booking,category` (ADR-0009) until a later change.
