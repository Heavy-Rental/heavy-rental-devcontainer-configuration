# Research: Haystack Neo4j

## Why Neo4j with Haystack

Official **neo4j-haystack** integration provides `Neo4jDocumentStore` for Haystack v2, using Neo4j vector indexes for embeddings and retrieval—aligned with RAG / document pipelines.

## Alternatives considered

| Option | Notes |
|---|---|
| In-memory / local file stores | Fine for unit tests; not shared persistent graph |
| Postgres only (pgvector) | Good for vectors; weaker native graph traversals — **platform ready** in stack as `004-haystack-pgvector` (T5/D4); durable project chunks target I1, not a Neo4j replacement for graph |
| Neo4j Aura | Cloud; extra account; not offline-friendly for this devcontainer |
| **Local Neo4j Compose** | Best fit for heavy-rental local multi-service network |

**Decision**: Local Neo4j 5 Community in Haystack Compose.

## Package

- `pip install neo4j-haystack` / `uv add neo4j-haystack`
- Import: `from neo4j_haystack import Neo4jDocumentStore`
- URL form: `bolt://neo4j:7687` inside Compose network

## Auth

Neo4j 5 requires auth. Compose `NEO4J_AUTH=neo4j/<password>` sets initial credentials non-interactively for dev.

## APOC / GDS

Not enabled by default. APOC can be added later via `NEO4J_PLUGINS` if pipelines need procedures. GDS is enterprise-oriented and out of scope for community dev defaults.

## Relationship to Postgres

Postgres continues to hold relational rental domain data (with optional merge from REST API primary). Neo4j holds Haystack documents/embeddings/graph structure. No automatic ETL between them in this feature.

## IDE clients

| Client | Role |
|---|---|
| Neo4j Browser (`:7474`) | Full web UI shipped with Neo4j container |
| **Neo4j for VS Code** (`neo4j-extensions.neo4j-for-vscode`) | Cypher/Bolt in the IDE; installed via `devcontainer.json` |

Both use the same Bolt endpoint and dev credentials. Extension does not replace Browser.

### Why no `pgsql.connections`-style Neo4j settings

Official extension settings only include linting/trace. Connections are created in the UI and stored in extension **globalState** (`connections`) and **SecretStorage** (passwords). Seeding that storage from the host is fragile and out of scope. Developers create **Haystack Local Neo4j** once via **Neo4j: Create new connection**.
