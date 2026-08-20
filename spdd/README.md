# OpenSPDD — REASONS Canvas contracts

[OpenSPDD](https://github.com/gszhangwei/open-spdd) (Structured Prompt-Driven Development) turns implementation intent into an executable **design contract**. In this repo the canvases describe **as-built Dev Container packs**, not product application source.

OpenSpec says **what** the packs must do. ADRs say **why**. These canvases say **exactly how** to implement a change and **what not to do** (Safeguards).

Process: [`docs/spec-governance.md`](../docs/spec-governance.md).

```text
spdd/
├── analysis/     # Strategic analysis (OpenSPDD /spdd-analysis)
└── prompt/       # Living REASONS Canvas contracts (/spdd-reasons-canvas)
```

## Living canvases (as-built)

| Canvas | Scope |
|--------|--------|
| [prompt/platform-devcontainers.md](./prompt/platform-devcontainers.md) | Shared network, pack roles, trust boundaries |
| [prompt/haystack-devcontainer.md](./prompt/haystack-devcontainer.md) | Haystack Compose, merge-sync, pgvector, Neo4j populate |
| [prompt/rest-api-devcontainer.md](./prompt/rest-api-devcontainer.md) | Dual REST packs, primary, optional replica |
| [prompt/web-portal-devcontainer.md](./prompt/web-portal-devcontainer.md) | React portal pack, no local DB |

Strategic analysis: [analysis/platform-devcontainers.md](./analysis/platform-devcontainers.md).

## Workflow for a new pack change

```text
/spdd-analysis          →  spdd/analysis/…
/spdd-reasons-canvas    →  spdd/prompt/…   (or edit the living canvas)
# also: OpenSpec proposal → specs → design → adr → tasks
/spdd-generate          →  Compose / scripts / docs
/spdd-sync              →  canvas matches as-built
```

Installing the `openspdd` CLI is optional. Markdown in this folder is the contract.

New feature canvases MAY use OpenSPDD filenames `{TICKET}-{YYYYMMDDHHmm}-[{Action}]-{scope}-{description}.md`. After archive, merge durable operations/safeguards back into the living pack canvas.

## REASONS dimensions

| Letter | Meaning | This repo uses it for |
|--------|---------|------------------------|
| R | Requirements | Why the pack exists and for whom |
| E | Entities | Compose services, volumes, contracts |
| A | Approach | Patterns already chosen (see `adr/`) |
| S | Structure | Layers, dependencies, network |
| O | Operations | Ordered, verifiable implementation steps |
| N | Norms | Naming, env, logging, spec update rules |
| S | Safeguards | Negative space — what MUST NOT be done |
