# Tasks: 004-haystack-pgvector (T5 / D4)

- [x] 1. Switch `postgres-haystack` image to `pgvector/pgvector:pg17`
- [x] 2. Add `initdb/01-create-vector-extension.sql` and mount to initdb.d
- [x] 3. Healthcheck: idempotent `CREATE EXTENSION IF NOT EXISTS vector` + `pg_isready`
- [x] 4. App env `INDEXING_EMBEDDING_DIM=768`
- [x] 5. Spec Kit `004` (spec, plan, research, data-model, contract, quickstart, verification, tasks)
- [x] 6. OpenSpec SoT + archive `2026-08-12-phase5-t5-d4-pgvector-platform`
- [x] 7. Haystack operator README
- [x] 8. Peer REST API docs + light OpenSpec/spec notes
- [x] 9. Peer Web Portal README note
- [ ] 10. Operator runtime SC-001–SC-005 after rebuild (local verification)
