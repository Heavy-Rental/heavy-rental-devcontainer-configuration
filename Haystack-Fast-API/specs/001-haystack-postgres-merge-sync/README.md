# Spec Kit: Haystack Postgres Merge Sync

**Status**: Implemented

GitHub [Spec Kit](https://github.com/github/spec-kit)–style feature package for writable Haystack Postgres with near-real-time **merge** sync (default 60s poll) from REST API `postgres-primary`.

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Feature specification (stories, FRs, success criteria) — **as-built** |
| [plan.md](./plan.md) | Implementation plan / as-built summary |
| [research.md](./research.md) | Options and decisions (including post-v1 flags) |
| [data-model.md](./data-model.md) | Entities and full env configuration |
| [tasks.md](./tasks.md) | Phased tasks (code done; operator verification open) |
| [verification.md](./verification.md) | **Running Verification** (SC-001–SC-007 + UK/EV/opt-in) |
| [quickstart.md](./quickstart.md) | Short entry → verification |
| [contracts/db-sync-env.md](./contracts/db-sync-env.md) | Sync job env/behavior contract + policy matrix |

## Implementation locations

| Path | Role |
|---|---|
| `Haystack-Fast-API/.devcontainer/docker-compose.yml` | `postgres-haystack`, `postgres-haystack-sync`, app env |
| `Haystack-Fast-API/.devcontainer/scripts/sync-from-primary.sh` | Merge loop |
| `Haystack-Fast-API/.devcontainer/devcontainer.json` | Ports, pgsql profiles |

## OpenSpec

| Path | Role |
|---|---|
| [openspec/specs/haystack-devcontainer/spec.md](../../openspec/specs/haystack-devcontainer/spec.md) | Source of truth |
| [openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/](../../openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/) | Original change archive |

Later enhancements (unique-key merge, additive evolution, opt-in parity flags) are reflected in the OpenSpec SoT and this Spec Kit package; they were not split into a second archive package.
