# OpenSpec (SDD) — configuration repository

[OpenSpec](https://github.com/Fission-AI/OpenSpec) source of truth for **cross-pack** platform behavior and documentation governance. Pack-level OpenSpec (Haystack, REST, Web Portal) remains the capability SoT for each Compose stack.

Schema: **`spec-driven-with-adr`** ([`config.yaml`](./config.yaml)). Durable ADRs: [`../adr/`](../adr/). Process: [`../docs/spec-governance.md`](../docs/spec-governance.md). OpenSPDD canvases: [`../spdd/`](../spdd/).

```text
openspec/
├── config.yaml
├── specs/
│   ├── platform-devcontainers/      # Shared network, pack roles, trust boundaries
│   └── documentation-governance/    # OpenSpec + OpenSPDD + ADR rules
└── changes/
    └── archive/
        └── 2026-08-20-adopt-openspec-openspdd-adr/
```

## Sources of truth

| Capability | Spec |
|------------|------|
| Platform packs | [specs/platform-devcontainers/spec.md](./specs/platform-devcontainers/spec.md) |
| Documentation model | [specs/documentation-governance/spec.md](./specs/documentation-governance/spec.md) |

## Pack OpenSpec (capability SoT)

- [Haystack-Fast-API/openspec](../Haystack-Fast-API/openspec/)
- [Heavy-Rental-REST-API/openspec](../Heavy-Rental-REST-API/openspec/)
- [Heavy-Rental-Web-Portal/openspec](../Heavy-Rental-Web-Portal/openspec/)

## Archived changes

| Archive | Description |
|---------|-------------|
| [2026-08-20-adopt-openspec-openspdd-adr](./changes/archive/2026-08-20-adopt-openspec-openspdd-adr/) | Adopt spec-driven-with-adr, durable `adr/`, OpenSPDD canvases, Web Portal specs |

## Change order

`proposal → specs → design → adr → tasks` then apply, then archive into `specs/`. Do not edit accepted files under `adr/`; supersede with a new ADR.
