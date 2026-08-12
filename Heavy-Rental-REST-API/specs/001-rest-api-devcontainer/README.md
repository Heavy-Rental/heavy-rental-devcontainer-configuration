# Spec Kit: REST API Devcontainer

**Feature**: `001-rest-api-devcontainer`  
**Status**: Specified (as-built from pack folders)

Spring Boot Java REST API devcontainer packs under `Heavy-Rental-REST-API/`, with two operator-selectable profiles:

1. **With PostgreSQL read replica** — primary + streaming standby  
2. **Without read replica** — primary only  

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Requirements and success criteria |
| [plan.md](./plan.md) | As-built structure |
| [research.md](./research.md) | Decisions and differences |
| [data-model.md](./data-model.md) | Services, volumes, ports |
| [contracts/compose-env.md](./contracts/compose-env.md) | Env and port contract |
| [contracts/pack-layout.md](./contracts/pack-layout.md) | Folder layout and promote rule |
| [contracts/schema-contract.md](./contracts/schema-contract.md) | **D0** fleet domain schema (producer) for Haystack mirror |
| [quickstart.md](./quickstart.md) | Short promote + open steps |
| [verification.md](./verification.md) | Runtime checks |
| [tasks.md](./tasks.md) | Task list |

**Phase 4:** Primary is the fleet LTM **pull source** for Haystack-Fast-API merge-sync. See schema contract and operator README.

**Packs (as-built):**

- `Spring Boot REST API devcontainer with PostgreSQL Read Replica/.devcontainer/`
- `Spring Boot REST API devcontainer without read replica/.devcontainer/`

**Operator entry:** [`../../README.md`](../../README.md)  
**OpenSpec SoT:** [`../../openspec/specs/rest-api-devcontainer/spec.md`](../../openspec/specs/rest-api-devcontainer/spec.md)
