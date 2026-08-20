# Spec governance: OpenSpec, OpenSPDD, and ADR

This repository documents **as-built local-development packs** (Dev Containers + Compose), not the product application source. Humans and coding agents MUST treat the artifacts below as the shared contract before changing pack behavior.

## The three layers

| Layer | Tool | Answers | Lives in | Survives a change archive? |
|-------|------|---------|----------|----------------------------|
| **What** | [OpenSpec](https://github.com/Fission-AI/OpenSpec) (spec-driven development) | Current agreed **behavior** | `openspec/specs/` (repo + each pack) | **Yes** — merged into SoT |
| **How / not-how** | [OpenSPDD](https://github.com/gszhangwei/open-spdd) (structured prompt-driven development) | Precise **implementation contract** (REASONS Canvas) | `spdd/` | **Yes** — living canvas; sync after code drift |
| **Why** | [ADR](https://adr.github.io/) (Architecture Decision Records) | Durable **architectural choice** and alternatives rejected | `adr/` | **Yes** — outside `openspec/`; immutable once accepted |

GitHub [Spec Kit](https://github.com/github/spec-kit) packages under each pack’s `specs/00N-…/` remain the **feature workbooks** (stories, contracts, verification). They are not a fourth source of truth: they MUST stay consistent with the OpenSpec SoT for that capability.

```text
                    ┌─────────────────────────────────────────┐
                    │  adr/     WHY (architecture memory)      │
                    │  OpenSpec WHAT (behavior SoT)            │
                    │  OpenSPDD HOW (REASONS Canvas contract)  │
                    └─────────────────────────────────────────┘
                                      ▲
                                      │ design against
                     OpenSpec change: proposal → specs → design → adr → tasks
                                      │
                                      ▼
                     apply in Compose / scripts / pack docs
                                      │
                                      ▼
                     archive: merge spec delta into SoT; keep ADRs + canvases
```

Default OpenSpec archives `design.md` with the change. This repo uses the **`spec-driven-with-adr`** schema so architectural rationale is **not** trapped in `openspec/changes/archive/`. See [intent-driven `spec-driven-with-adr`](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/).

## Where artifacts live

```text
heavy-rental-devcontainer-configuration/
├── adr/                                  # Durable ADRs (repo-wide sequence)
├── docs/spec-governance.md               # This file
├── openspec/                             # Platform OpenSpec (schema + cross-pack SoT)
│   ├── config.yaml                       # schema: spec-driven-with-adr
│   ├── specs/
│   └── changes/
├── spdd/                                 # OpenSPDD analysis + REASONS canvases
│   ├── analysis/
│   └── prompt/
├── Heavy-Rental-Web-Portal/openspec/ + specs/
├── Heavy-Rental-REST-API/openspec/ + specs/
└── Haystack-Fast-API/openspec/ + specs/
```

Pack-level OpenSpec remains the **capability** SoT (Haystack stack, REST packs, Web Portal pack). Root OpenSpec is the **platform** SoT (shared network, trust boundaries, documentation model). Durable ADRs are **always** at the configuration-repo root `adr/`, even when the change folder lives under a pack.

## Change workflow (required for pack behavior)

Use this order for any change that alters Compose services, sync/populate jobs, ports, schema contracts, or operator-visible behavior:

1. **Proposal** — `openspec/changes/<id>/proposal.md` (why now, capabilities, impact).
2. **Specs** — delta under `openspec/changes/<id>/specs/<capability>/spec.md` (`ADDED` / `MODIFIED` / `REMOVED`).
3. **Design** — `design.md`. MUST list in-force ADRs from `adr/` and stay coherent with them.
4. **ADR review** — `openspec/changes/<id>/adr.md` (manifest). Create `adr/NNNN-kebab-title.md` only for a new durable decision. **Never edit** an accepted ADR; supersede it with a new file.
5. **OpenSPDD** — update or add `spdd/prompt/…` REASONS Canvas (Requirements, Entities, Approach, Structure, Operations, Norms, Safeguards). Safeguards are the negative space (what MUST NOT be done).
6. **Tasks** — `tasks.md` checkboxes; then implement.
7. **Spec Kit** — update the matching `specs/00N-…/` workbook (contracts, verification, quickstart).
8. **Archive** — merge the spec delta into `openspec/specs/<capability>/spec.md`; move the change folder to `openspec/changes/archive/YYYY-MM-DD-<id>/`.

Skip the full change folder only for typo/docs-only edits that do not change requirements. When in doubt, use the change folder.

### OpenSpec config

Every `openspec/config.yaml` in this repo MUST set:

```yaml
schema: spec-driven-with-adr
```

Artifact order: **proposal → specs → design → adr → tasks**.

## Reading order for a new contributor or agent

1. [`ARCHITECTURE.md`](../ARCHITECTURE.md) — how the three packs compose.
2. [`adr/README.md`](../adr/README.md) — in-force decisions (walk `Supersedes:`).
3. OpenSpec SoT for the pack you are changing.
4. Matching OpenSPDD canvas under [`spdd/prompt/`](../spdd/prompt/).
5. Spec Kit verification for the feature.

## Pack capability map

| Pack | OpenSpec SoT | Spec Kit | OpenSPDD canvas |
|------|--------------|----------|-----------------|
| Platform (all packs) | [`openspec/specs/platform-devcontainers/spec.md`](../openspec/specs/platform-devcontainers/spec.md) | — | [`spdd/prompt/platform-devcontainers.md`](../spdd/prompt/platform-devcontainers.md) |
| Documentation model | [`openspec/specs/documentation-governance/spec.md`](../openspec/specs/documentation-governance/spec.md) | — | (this file + canvas Safeguards) |
| Haystack Fast API | [`Haystack-Fast-API/openspec/specs/haystack-devcontainer/spec.md`](../Haystack-Fast-API/openspec/specs/haystack-devcontainer/spec.md) | `Haystack-Fast-API/specs/001`–`005` | [`spdd/prompt/haystack-devcontainer.md`](../spdd/prompt/haystack-devcontainer.md) |
| REST API | [`Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md`](../Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md) | `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer` | [`spdd/prompt/rest-api-devcontainer.md`](../spdd/prompt/rest-api-devcontainer.md) |
| Web Portal | [`Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md`](../Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md) | `Heavy-Rental-Web-Portal/specs/001-web-portal-devcontainer` | [`spdd/prompt/web-portal-devcontainer.md`](../spdd/prompt/web-portal-devcontainer.md) |

## Sync rule

When implementation and artifacts diverge, **fix the prompt/spec first, then the code** (OpenSPDD). After a shipped change, run the equivalent of `/spdd-sync` so the REASONS Canvas still matches Compose and scripts. OpenSpec SoT MUST be archived in the same change; ADRs stay immutable.

## Optional CLI

- OpenSpec: [openspec.dev](https://openspec.dev/) — validate/propose/archive against `openspec/`.
- OpenSPDD: `openspdd generate --all` then `/spdd-analysis`, `/spdd-reasons-canvas`, `/spdd-generate`, `/spdd-sync`. Installing the CLI is optional; the canvases in `spdd/` are the contract even without it.
