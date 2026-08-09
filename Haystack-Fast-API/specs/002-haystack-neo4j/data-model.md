# Data Model: Haystack Neo4j

## Entities

### Neo4j service

| Attribute | Value |
|---|---|
| Compose service | `neo4j` |
| Container | `neo4j-haystack` |
| Image | `neo4j:5` |
| Volume | `neo4j-haystack-data` → `/data` |
| HTTP | host `7474` → container `7474` |
| Bolt | host `7687` → container `7687` |
| Network | `heavy-rental-network` |

### Connection configuration (app env)

| Key | Default (dev) |
|---|---|
| `NEO4J_URI` | `bolt://neo4j:7687` |
| `NEO4J_USER` | `neo4j` |
| `NEO4J_PASSWORD` | `heavyrental` |
| `NEO4J_DATABASE` | `neo4j` |

### Auth (Neo4j container)

| Key | Value |
|---|---|
| `NEO4J_AUTH` | `neo4j/heavyrental` |

### IDE tooling

| Attribute | Value |
|---|---|
| Extension ID | `neo4j-extensions.neo4j-for-vscode` |
| Configured in | `.devcontainer/devcontainer.json` → `customizations.vscode.extensions` |
| Bolt (in container) | `bolt://neo4j:7687` |
| Bolt (from host) | `bolt://localhost:7687` |
| Auth | same as `NEO4J_AUTH` / app `NEO4J_*` |

### Complementary store

Postgres (`db` / `postgres-haystack`) remains the relational domain store; not replaced by Neo4j.
