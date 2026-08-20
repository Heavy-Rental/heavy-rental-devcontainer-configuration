# ADR-0010: OpenSpec + OpenSPDD + ADR documentation model

- Status: accepted
- Date: 2026-08-20
- Tags: documentation, sdd, spdd, adr

## Context

Pack behavior was already captured in GitHub Spec Kit workbooks and lightweight OpenSpec SoT files. Architectural rationale lived only in archived `design.md` files, so future changes re-litigated pull-vs-push, poll-vs-CDC, and KG isolation. There was no durable ADR log, no OpenSPDD REASONS Canvas (implementation contract / negative space), and no Web Portal OpenSpec. Default OpenSpec `spec-driven` drops `design.md` on archive.

## Decision

Adopt a **three-layer** in-repo model:

1. **OpenSpec** with schema **`spec-driven-with-adr`**: living behavior SoT under `openspec/specs/` (repo platform + per pack). Change order: proposal → specs → design → adr → tasks.
2. **ADR** at repo-root **`adr/`**: immutable accepted records; supersede by adding a new file. Change-local `adr.md` is a review manifest only.
3. **OpenSPDD REASONS Canvas** under **`spdd/`**: feature/pack implementation contracts (Requirements, Entities, Approach, Structure, Operations, Norms, Safeguards). Sync canvases when code drifts (`/spdd-sync` or equivalent).

Spec Kit `specs/00N-…/` remains the feature workbook (stories, contracts, verification) and MUST stay aligned with OpenSpec SoT.

Web Portal MUST have the same OpenSpec + Spec Kit layout as the other packs.

## Consequences

- Agents can read *what / how / why* without mining archives or chat history.
- More artifacts to update per change; skip the full folder only for typo/docs-only edits.
- CLI install for `openspec` / `openspdd` is optional; markdown is the contract.

## Related

- [`docs/spec-governance.md`](../docs/spec-governance.md)
- OpenSpec: `openspec/specs/documentation-governance/spec.md`
