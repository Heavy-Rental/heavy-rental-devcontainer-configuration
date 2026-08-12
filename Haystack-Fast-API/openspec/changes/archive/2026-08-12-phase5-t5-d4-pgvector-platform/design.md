# Design: Phase 5 T5 / D4 pgvector platform

## Decisions

| Topic | Decision |
|-------|----------|
| Image | `pgvector/pgvector:pg17` |
| Sync client image | Remain `postgres:17` |
| Extension bootstrap | initdb SQL + healthcheck `CREATE EXTENSION IF NOT EXISTS vector` |
| Default dim | `INDEXING_EMBEDDING_DIM=768` |
| Document tables | Not created in config repo |
| Primary | No pgvector requirement |

## Data roles on postgres-haystack

```text
postgres-haystack (pgvector/pgvector:pg17)
  ├── public fleet mirror (merge-sync from primary)
  ├── extension vector (platform)
  └── (future) project document/vector tables — app I1
```

## Failure / upgrade modes

| Case | Handling |
|------|----------|
| Fresh volume | initdb creates extension |
| Existing volume from `postgres:17` | Healthcheck ensure; same major 17 |
| Incompatible data dir | Operator recreates volume after backup |
| Dim change after I1 | App migration; not this platform step |
