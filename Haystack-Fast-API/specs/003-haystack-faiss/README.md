# Spec Kit: Haystack FAISS DocumentStore

**Status: removed from default devcontainer** — FAISS env (`FAISS_*`) and postCreate `faiss-haystack` install are **no longer** wired in `docker-compose.yml` / `devcontainer.json`. This Spec Kit package is retained for history only. OpenSpec SoT no longer requires FAISS.

**Previous status**: Implemented (in-process **FAISSDocumentStore** via `faiss-haystack` (CPU); no separate FAISS Docker service).

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Requirements and success criteria |
| [plan.md](./plan.md) | Implementation plan |
| [research.md](./research.md) | Decisions |
| [data-model.md](./data-model.md) | Path + env entities |
| [contracts/faiss-env.md](./contracts/faiss-env.md) | Environment contract |
| [verification.md](./verification.md) | Runtime verification |
| [quickstart.md](./quickstart.md) | Short entry |
| [tasks.md](./tasks.md) | Task list |

**Former implementation (removed):** compose `FAISS_*` env + postCreate `faiss-haystack`  
**OpenSpec:** archive `add-haystack-faiss` (historical); current SoT does not require FAISS
