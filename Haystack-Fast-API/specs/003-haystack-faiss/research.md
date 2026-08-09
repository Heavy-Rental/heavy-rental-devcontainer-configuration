# Research: Haystack FAISS DocumentStore

## Why FAISS with Haystack

Official **faiss-haystack** integration provides `FAISSDocumentStore` for local vector similarity search—lightweight, no external database process. Good for local development and small-to-medium RAG experiments alongside Neo4j graph store and Postgres domain data.

## Alternatives considered

| Option | Notes |
|---|---|
| Separate FAISS Docker service | FAISS API is in-process Python; a sidecar does not map cleanly to DocumentStore |
| Neo4j only | Already present; stronger for graph, heavier for pure vector smoke tests |
| InMemoryDocumentStore only | No disk persistence |
| **In-process faiss-haystack + path env** | Best fit for this config repo |

**Decision**: Install `faiss-haystack` in the app container; set `FAISS_INDEX_PATH` under the workspace volume. No Compose service for FAISS.

## Package

- `pip install faiss-haystack` / `uv add faiss-haystack` / `uv pip install faiss-haystack`
- Import: `from haystack_integrations.document_stores.faiss import FAISSDocumentStore`
- Persistence: `index_path` loads `.faiss` / `.json`; `save(path)` writes them

## Persistence layout

- Default path: `/workspaces/haystack-fast-api/.faiss/index`
- Parent dir created on first use (app or verification steps)
- Durability via existing workspace volume (`haystack-fast-api-data`), not a dedicated FAISS volume

## System deps / wheels

- Prefer prebuilt wheels on Linux x86_64 miniconda base
- Fallback if install fails: ensure `libgomp1` (apt) or `conda install -c conda-forge faiss-cpu`
- GPU (`faiss-gpu`) out of scope for this devcontainer

## OpenMP

Documented mainly for macOS host tooling; Linux container usually fine. If OMP double-init appears, set `OMP_NUM_THREADS=1` as a temporary workaround.

## Relationship to Neo4j and Postgres

| Store | Role |
|---|---|
| Postgres | Relational domain (+ merge from REST primary) |
| Neo4j | Graph + vector DocumentStore (`neo4j-haystack`) |
| FAISS | Local in-process vector DocumentStore (`faiss-haystack`) |

No automatic ETL between stores in this feature. App code chooses which DocumentStore to use.
