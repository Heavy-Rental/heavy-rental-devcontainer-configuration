# Proposal: Phase 8.2 T4 / PR-M — Neo4j populate trigger + KG-1 protect

## Intent

Close **Phase 8.2 T4** (config pack) after T3 SQL→MERGE:

1. Trigger fleet Neo4j populate after a **successful** merge-sync cycle.
2. Expose **admin HTTP** for the same one-shot cycle.
3. **Scoped delete** for fleet (KG-2) only; **never drop KG-1** labels (default `:Document`).

## Scope

### In scope

- HTTP admin on `neo4j-populate` (`POST /v1/populate`, `GET /health`)
- Post-success hook in `sync-from-primary.sh` (best-effort curl)
- `Dockerfile.postgres-sync` with curl
- `KG1_PROTECTED_LABELS`, orphan/scoped delete hardening
- Spec Kit 005 + OpenSpec SoT updates

### Out of scope

- App S8.3 agent tool live Neo4j client
- APOC triggers, CDC
- Prometheus

## Approach

1. Threaded stdlib HTTP server in populate worker; 202 + background cycle.
2. Sync POSTs trigger URL only when merge succeeds; never fails sync.
3. Delete paths use fleet labels minus protected KG-1 set only.
