# Quickstart: Haystack Neo4j

Full runbook: **[verification.md](./verification.md)**

```bash
docker network create heavy-rental-network  # once
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

| Service | Container | Ports |
|---|---|---|
| `neo4j` | `neo4j-haystack` | 7474 HTTP, 7687 Bolt |
| `db` | `postgres-haystack` | 5434 (unchanged) |

```bash
docker exec haystack-fast-api printenv | grep NEO4J
docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental 'RETURN 1;'
```

Install package in the app workspace:

```bash
uv add neo4j-haystack
```

Browser: http://localhost:7474 — user `neo4j` / password `heavyrental`.

### Neo4j for VS Code

The devcontainer installs **`neo4j-extensions.neo4j-for-vscode`**. After rebuild, open the Neo4j extension and connect:

| Field | Inside container | From host |
|---|---|---|
| URI | `bolt://neo4j:7687` | `bolt://localhost:7687` |
| User | `neo4j` | `neo4j` |
| Password | `heavyrental` | `heavyrental` |
| Database | `neo4j` | `neo4j` |
