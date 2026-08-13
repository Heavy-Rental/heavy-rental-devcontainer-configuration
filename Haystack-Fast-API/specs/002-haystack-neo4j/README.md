# Spec Kit: Haystack Neo4j

**Status**: Implemented

Neo4j 5 Community in the Haystack Fast API devcontainer for **neo4j-haystack** DocumentStore integration, plus the **Neo4j for VS Code** extension (`neo4j-extensions.neo4j-for-vscode`). IDE connections are created in the extension UI (not settings profiles like Postgres).

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Requirements and success criteria |
| [plan.md](./plan.md) | As-built plan |
| [research.md](./research.md) | Decisions |
| [data-model.md](./data-model.md) | Service + env entities |
| [contracts/neo4j-env.md](./contracts/neo4j-env.md) | Connection contract |
| [verification.md](./verification.md) | Runtime verification |
| [quickstart.md](./quickstart.md) | Short entry |
| [tasks.md](./tasks.md) | Task list |

**Implementation:** `Haystack-Fast-API/.devcontainer/docker-compose.yml`, `devcontainer.json`  
**OpenSpec:** `openspec/specs/haystack-devcontainer/spec.md` (SoT) + archive `add-haystack-neo4j`

**Related:** durable project-chunk vectors on Postgres use **pgvector** ([`../004-haystack-pgvector/`](../004-haystack-pgvector/)). Fleet SQL → Cypher **MERGE** (KG-2 projection, labels isolated from DocumentStore) lives in **[`../005-haystack-neo4j-populate/`](../005-haystack-neo4j-populate/)**. This package remains the DocumentStore / Bolt platform path.
