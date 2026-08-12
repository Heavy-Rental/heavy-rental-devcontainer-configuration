# Spec Kit: Haystack Postgres Merge Sync

**Status**: Implemented (includes Phase 4 T1 lag metrics, T2 allowlist, D0 schema contract)

GitHub [Spec Kit](https://github.com/github/spec-kit)–style feature package for writable Haystack Postgres with near-real-time **merge** sync (default 60s poll) from REST API `postgres-primary`.

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Feature specification (stories, FRs, success criteria) — **as-built** |
| [plan.md](./plan.md) | Implementation plan / as-built summary |
| [research.md](./research.md) | Options and decisions (including post-v1 flags) |
| [data-model.md](./data-model.md) | Entities and full env configuration |
| [tasks.md](./tasks.md) | Phased tasks (code done; operator verification open) |
| [verification.md](./verification.md) | **Running Verification** (SC-001–SC-012 + UK/EV/opt-in) |
| [quickstart.md](./quickstart.md) | Short entry → verification |
| [contracts/db-sync-env.md](./contracts/db-sync-env.md) | Sync job env/behavior contract + policy matrix |
| [contracts/schema-contract.md](./contracts/schema-contract.md) | **D0** fleet domain schema (consumer) + allowlist bind |

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
| [openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/](../../openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/) | Phase 4 allowlist + lag metrics + D0 |

Later enhancements (unique-key merge, additive evolution, opt-in parity flags, Phase 4 allowlist/D0) are reflected in the OpenSpec SoT and this Spec Kit package.

**Related (Phase 5 T5 / D4):** local DB image is now **`pgvector/pgvector:pg17`** with extension `vector` — see [`../004-haystack-pgvector/`](../004-haystack-pgvector/). Merge-sync behavior is unchanged; sync client image remains `postgres:17`.
