# Implementation Plan: Haystack FAISS DocumentStore

**Feature**: `003-haystack-faiss` | **Status**: Implemented

## Summary

Add in-process FAISSDocumentStore support to the Haystack Compose/devcontainer: install `faiss-haystack`, expose `FAISS_*` env, document persistence under the workspace volume. Complements existing Neo4j service; no FAISS Docker service.

## Technical Context

- Package: `faiss-haystack` (CPU) via `uv` (postCreate or project deps)
- Env: `FAISS_INDEX_PATH`, optional `FAISS_EMBEDDING_DIM`, `FAISS_INDEX_STRING`
- Persistence: workspace path under existing `haystack-fast-api-data` volume (Option A)
- Complements Neo4j (`neo4j-haystack`) and Postgres (`postgres-haystack` / `postgres-haystack-sync`)

## Structure

```text
Haystack-Fast-API/.devcontainer/
  docker-compose.yml    # + FAISS_* env on haystack-fast-api
  devcontainer.json     # + faiss-haystack in postCreate install

specs/003-haystack-faiss/
  verification.md, contracts/faiss-env.md, ...
```

## Testing

See [verification.md](./verification.md).
