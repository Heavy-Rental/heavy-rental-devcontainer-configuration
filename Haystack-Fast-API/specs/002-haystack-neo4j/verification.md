# Running Verification: Haystack Neo4j

## Prerequisites

```bash
docker network create heavy-rental-network   # once
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

Or rebuild the Haystack Fast API devcontainer.

## 1. Containers healthy (SC-001, SC-005)

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' \
  | grep -E 'neo4j-haystack|postgres-haystack|haystack-fast-api|NAME'
```

**Expect:** `neo4j-haystack` healthy/up; Postgres containers still present.

## 2. App env (SC-004)

```bash
docker exec haystack-fast-api printenv | grep NEO4J
```

**Expect:**

```text
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=heavyrental
NEO4J_DATABASE=neo4j
```

## 3. Bolt from app network (SC-002)

```bash
docker exec neo4j-haystack \
  cypher-shell -u neo4j -p heavyrental 'RETURN 1 AS ok;'
```

**Expect:** `ok` = 1.

## 4. Browser (SC-003)

Open `http://localhost:7474` (or forwarded port).

- Connect URL: `bolt://localhost:7687` (from host) or use Browser defaults  
- User: `neo4j` / Password: `heavyrental`

## 4b. Neo4j for VS Code extension (SC-006, US5)

**Config check:**

```bash
grep -n 'neo4j-extensions.neo4j-for-vscode' \
  Haystack-Fast-API/.devcontainer/devcontainer.json
```

**Expect:** extension ID present under `customizations.vscode.extensions`.

**Manual (after rebuild):** open Neo4j for VS Code → connect with:

| Field | Inside container |
|---|---|
| URI | `bolt://neo4j:7687` |
| User / Password | `neo4j` / `heavyrental` |
| Database | `neo4j` |

Run `RETURN 1` (or equivalent) and confirm success.

## 5. Install neo4j-haystack (US3)

Inside the app container / devcontainer terminal:

```bash
# Prefer project dependency:
uv add neo4j-haystack
# or ad-hoc:
uv pip install neo4j-haystack
```

```bash
python -c "from neo4j_haystack import Neo4jDocumentStore; print('ok')"
```

## 6. Optional DocumentStore smoke

```python
import os
from haystack.dataclasses import Document
from neo4j_haystack import Neo4jDocumentStore

store = Neo4jDocumentStore(
    url=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    database=os.environ.get("NEO4J_DATABASE", "neo4j"),
    embedding_dim=768,  # match your embedder if required by your version
)
# Version-specific API may vary; see neo4j-haystack docs for write/query.
print("Neo4jDocumentStore constructed:", store)
```

Adjust constructor kwargs to the installed `neo4j-haystack` version.

## Pass checklist

| ID | Check | Result |
|---|---|---|
| SC-001 | Neo4j up/healthy | ☐ |
| SC-002 | cypher-shell RETURN 1 | ☐ |
| SC-003 | Browser reachable | ☐ |
| SC-004 | NEO4J_* in app | ☐ |
| SC-005 | Postgres still present | ☐ |
| SC-006 | neo4j-for-vscode in devcontainer.json | ☐ |
| US3 | neo4j-haystack import | ☐ |
| US5 | Extension connect (manual) | ☐ |

## Troubleshooting

| Symptom | Check |
|---|---|
| Healthcheck failing | Wait longer; `docker logs neo4j-haystack`; password match |
| Connection refused from app | Same network? Service name `neo4j`? |
| Port in use | Change host mapping for 7474/7687 |
| Auth failed | `NEO4J_AUTH` vs `NEO4J_PASSWORD` mismatch; wipe volume if auth changed after first init |
