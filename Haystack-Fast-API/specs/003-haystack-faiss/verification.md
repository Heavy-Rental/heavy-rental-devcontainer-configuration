# Running Verification: Haystack FAISS DocumentStore

Prerequisites: Haystack Compose stack started (`heavy-rental-network` exists). App container `haystack-fast-api` running.

## 1. Coexistence (stack still has Postgres + Neo4j)

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' \
  | grep -E 'neo4j-haystack|postgres-haystack|haystack-fast-api|NAME'
```

**Expect:** App + Postgres (+ Neo4j) present; no FAISS container required.

## 2. Env present

```bash
docker exec haystack-fast-api printenv FAISS_INDEX_PATH FAISS_EMBEDDING_DIM FAISS_INDEX_STRING
```

**Expect (defaults):**

```text
FAISS_INDEX_PATH=/workspaces/haystack-fast-api/.faiss/index
FAISS_EMBEDDING_DIM=768
FAISS_INDEX_STRING=Flat
```

## 3. Path writable

```bash
docker exec haystack-fast-api bash -lc \
  'mkdir -p "$(dirname "$FAISS_INDEX_PATH")" && test -w "$(dirname "$FAISS_INDEX_PATH")" && echo writable'
```

## 4. Install faiss-haystack (if not already from postCreate)

```bash
docker exec -u vscode haystack-fast-api bash -lc \
  'export PATH="$HOME/.local/bin:$PATH"; uv pip install faiss-haystack || pip install --user faiss-haystack'
```

## 5. Import smoke (US1 / SC-001)

```bash
docker exec -u vscode haystack-fast-api bash -lc \
  'python -c "from haystack_integrations.document_stores.faiss import FAISSDocumentStore; print(\"ok\")"'
```

## 6. Optional DocumentStore save/load smoke (US3)

```bash
docker exec -u vscode haystack-fast-api bash -lc 'python <<'"'"'PY'"'"'
import os
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

path = os.environ["FAISS_INDEX_PATH"]
os.makedirs(os.path.dirname(path), exist_ok=True)
dim = int(os.environ.get("FAISS_EMBEDDING_DIM", "768"))
store = FAISSDocumentStore(
    index_path=path,
    embedding_dim=dim,
    index_string=os.environ.get("FAISS_INDEX_STRING", "Flat"),
)
store.write_documents(
    [Document(content="faiss-smoke", embedding=[0.1] * dim)],
    policy=DuplicatePolicy.OVERWRITE,
)
store.save(path)
reloaded = FAISSDocumentStore(index_path=path)
print("count", reloaded.count_documents())
PY'
```

Adjust constructor kwargs to the installed `faiss-haystack` version if the API differs slightly.

## Success checklist

| Criterion | Check | Done |
|---|---|---|
| SC-001 | Import FAISSDocumentStore | ☐ |
| SC-002 | FAISS_INDEX_PATH set and writable | ☐ |
| SC-003 | Optional save/load | ☐ |
| SC-004 | Postgres/Neo4j undisturbed | ☐ |
| US1 | Package ready | ☐ |
| US2 | Env path | ☐ |

## Troubleshooting

| Symptom | Action |
|---|---|
| Import fails | Re-run `uv pip install faiss-haystack`; check Python used by `python` |
| Wheel build errors | Try `apt-get install -y libgomp1` in Dockerfile or `conda install -c conda-forge faiss-cpu` |
| Path not writable | `chown` workspace; ensure volume mount |
| OMP errors | Rare in Linux container; try `OMP_NUM_THREADS=1` |
