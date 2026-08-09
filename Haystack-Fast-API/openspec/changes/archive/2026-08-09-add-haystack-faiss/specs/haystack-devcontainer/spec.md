# Delta for Haystack Devcontainer

## ADDED Requirements

### Requirement: FAISS local vector store for Haystack

The Haystack application service MUST support in-process FAISSDocumentStore usage: install or document `faiss-haystack`, and expose `FAISS_INDEX_PATH` (and optional dim/index defaults) pointing at a writable path under the workspace volume. A separate FAISS Compose service is NOT required. FAISS MUST NOT replace Postgres or Neo4j.

#### Scenario: FAISS env present

- **GIVEN** the app container is running
- **WHEN** environment variables are read
- **THEN** `FAISS_INDEX_PATH` is set to a path under `/workspaces/haystack-fast-api`

#### Scenario: Package import path documented

- **GIVEN** postCreate or documented install has run
- **WHEN** a developer imports FAISSDocumentStore
- **THEN** `from haystack_integrations.document_stores.faiss import FAISSDocumentStore` succeeds (or install steps in Spec Kit 003 restore it)
