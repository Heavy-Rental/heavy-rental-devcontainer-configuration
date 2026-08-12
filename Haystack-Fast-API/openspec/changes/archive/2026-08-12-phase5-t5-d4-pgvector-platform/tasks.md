# Tasks: Phase 5 T5 / D4 pgvector platform

- [x] 1. `postgres-haystack` image → `pgvector/pgvector:pg17`
- [x] 2. initdb `01-create-vector-extension.sql` + volume mount
- [x] 3. Healthcheck ensure extension + `pg_isready`
- [x] 4. `INDEXING_EMBEDDING_DIM=768` on app service
- [x] 5. Spec Kit `004-haystack-pgvector`
- [x] 6. OpenSpec SoT requirement + this archive
- [x] 7. Haystack README
- [x] 8. Peer REST + Web Portal docs
- [ ] 9. Operator runtime SC after rebuild
