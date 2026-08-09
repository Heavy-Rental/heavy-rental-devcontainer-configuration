# Design: Add FAISS DocumentStore for Haystack

## Approach

- No Compose service: FAISSDocumentStore is in-process
- App env: `FAISS_INDEX_PATH`, `FAISS_EMBEDDING_DIM`, `FAISS_INDEX_STRING`
- Default path under workspace volume: `/workspaces/haystack-fast-api/.faiss/index`
- postCreate installs `faiss-haystack` with `neo4j-haystack`
- Complements Neo4j and Postgres; does not replace them

## File changes

- `.devcontainer/docker-compose.yml`
- `.devcontainer/devcontainer.json`
- `specs/003-haystack-faiss/*`
- `openspec/specs/haystack-devcontainer/spec.md`
