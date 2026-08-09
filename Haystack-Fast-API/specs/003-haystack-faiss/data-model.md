# Data Model: Haystack FAISS

## Entities

### FAISS (in-process)

| Field | Value |
|---|---|
| Compose service | none (runs in `haystack-fast-api`) |
| Package | `faiss-haystack` |
| Import | `haystack_integrations.document_stores.faiss.FAISSDocumentStore` |
| Index files | `{FAISS_INDEX_PATH}.faiss`, `{FAISS_INDEX_PATH}.json` (Haystack save/load naming) |

### App connection / config env

| Name | Default | Description |
|---|---|---|
| `FAISS_INDEX_PATH` | `/workspaces/haystack-fast-api/.faiss/index` | Path prefix for index persistence |
| `FAISS_EMBEDDING_DIM` | `768` | Suggested embedding dimension |
| `FAISS_INDEX_STRING` | `Flat` | FAISS index factory string |

### Persistence volume

Uses existing workspace volume mounted at `/workspaces/haystack-fast-api` (`haystack-fast-api-data`). No dedicated FAISS volume.

### Coexistence

Postgres and Neo4j services remain the network-attached data services; FAISS does not replace them.
