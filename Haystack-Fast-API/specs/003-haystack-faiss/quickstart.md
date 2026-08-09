# Quickstart: Haystack FAISS DocumentStore

## What you get

| Piece | Detail |
|---|---|
| Package | `faiss-haystack` (installed via postCreate / `uv`) |
| Env | `FAISS_INDEX_PATH`, optional dim/index string |
| Service | none (in-process in `haystack-fast-api`) |

## Install / import

```bash
export PATH="$HOME/.local/bin:$PATH"
uv add faiss-haystack
# or: uv pip install faiss-haystack

python -c "from haystack_integrations.document_stores.faiss import FAISSDocumentStore; print('ok')"
```

## Construct from env

```python
import os
from haystack_integrations.document_stores.faiss import FAISSDocumentStore

store = FAISSDocumentStore(
    index_path=os.environ.get("FAISS_INDEX_PATH"),
    embedding_dim=int(os.environ.get("FAISS_EMBEDDING_DIM", "768")),
    index_string=os.environ.get("FAISS_INDEX_STRING", "Flat"),
)
print(store)
```

## Related

- Neo4j DocumentStore: [../002-haystack-neo4j/quickstart.md](../002-haystack-neo4j/quickstart.md)
- Verification: [verification.md](./verification.md)
