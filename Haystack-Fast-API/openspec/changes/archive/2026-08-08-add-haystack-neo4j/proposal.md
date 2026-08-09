# Proposal: Add Neo4j for Haystack

## Intent

Provide a local Neo4j 5 instance in the Haystack Fast API devcontainer so developers can use **neo4j-haystack** (`Neo4jDocumentStore`) for documents and embeddings alongside existing Postgres domain data.

## Scope

In scope:
- Compose `neo4j` service, volume, ports, healthcheck, shared network
- App `NEO4J_*` env and depends_on healthy Neo4j
- Devcontainer port forwards + package install guidance
- Spec Kit `002-haystack-neo4j` + OpenSpec SoT updates

Out of scope:
- Postgres→Neo4j ETL
- Aura / clustering / GDS
- Full application pipeline code (lives in app workspace)

## Approach

Neo4j Community via official image; Bolt `neo4j:7687` on `heavy-rental-network`; dev auth `neo4j/heavyrental`; document `uv add neo4j-haystack`.
