# Contract: FAISS DocumentStore environment

## App container (`haystack-fast-api`)

| Name | Required | Default | Description |
|---|---|---|---|
| `FAISS_INDEX_PATH` | yes | `/workspaces/haystack-fast-api/.faiss/index` | Path prefix for FAISS index files |
| `FAISS_EMBEDDING_DIM` | no | `768` | Suggested embedding dimension for store init |
| `FAISS_INDEX_STRING` | no | `Flat` | FAISS index factory string |

## Connectivity expectations

- No network service or host port for FAISS (in-process).
- Path MUST be writable by `vscode` under the workspace volume.
- Parent directory SHOULD be created before first `save` if missing (`mkdir -p "$(dirname "$FAISS_INDEX_PATH")"`).

## Haystack package

- Install: `uv add faiss-haystack` or `uv pip install faiss-haystack`
- Client SHOULD read path/dim from env above
- Import: `from haystack_integrations.document_stores.faiss import FAISSDocumentStore`
