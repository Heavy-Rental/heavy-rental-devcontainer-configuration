# Proposal: Add FAISS DocumentStore for Haystack

## Intent

Provide in-process **FAISSDocumentStore** support in the Haystack Fast API devcontainer so developers can use **faiss-haystack** for lightweight local vector search alongside existing Neo4j (`neo4j-haystack`) and Postgres domain data.

## Scope

In scope:
- App `FAISS_INDEX_PATH` (+ optional dim/index string) env under workspace volume
- Devcontainer package install guidance / postCreate for `faiss-haystack`
- Spec Kit `003-haystack-faiss` + OpenSpec SoT updates

Out of scope:
- Separate FAISS Docker/Compose service
- GPU FAISS
- Application RAG pipeline code (lives in app workspace)
- Replacing Neo4j or Postgres

## Approach

CPU `faiss-haystack` in the app container; index files under `/workspaces/haystack-fast-api/.faiss/` on the existing workspace volume; document import and save/load smoke tests.
