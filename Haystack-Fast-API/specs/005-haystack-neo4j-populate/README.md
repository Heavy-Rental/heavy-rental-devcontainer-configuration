# Spec Kit: Haystack Neo4j fleet populate (Phase 8 T3 / PR-L 8.1)

**Feature**: `005-haystack-neo4j-populate`  
**Status**: **Implemented** (T3 SQL→MERGE + **T4** post-sync/admin trigger, scoped delete, never drop KG-1)  
**Date**: 2026-08-13

Projects allowlisted fleet tables from **`postgres-haystack`** into **Neo4j** via idempotent Cypher **`MERGE`** (**KG-2** labels `:Asset`, `:Booking`, `:Category`). **KG-1** / DocumentStore labels (default `:Document`) are never written or deleted.

**T4 triggers:** after successful `postgres-haystack-sync` merge (best-effort HTTP) or admin `POST /v1/populate` (host port **8089**).

| Artifact | Description |
|---|---|
| [spec.md](./spec.md) | Requirements and success criteria |
| [plan.md](./plan.md) | As-built plan |
| [research.md](./research.md) | Design decisions |
| [data-model.md](./data-model.md) | Labels, keys, relationships |
| [contracts/neo4j-populate-env.md](./contracts/neo4j-populate-env.md) | Env contract |
| [contracts/fleet-graph-contract.md](./contracts/fleet-graph-contract.md) | Graph isolation contract |
| [verification.md](./verification.md) | Runtime checks |
| [quickstart.md](./quickstart.md) | Operator entry |
| [tasks.md](./tasks.md) | Task list |

**Implementation:**

- `.devcontainer/scripts/populate_neo4j.py`
- `.devcontainer/scripts/populate-neo4j-from-haystack.sh`
- `.devcontainer/Dockerfile.neo4j-populate`
- Compose service `neo4j-populate`

**OpenSpec:** `openspec/specs/haystack-devcontainer/spec.md` + archive `2026-08-13-phase8-t3-populate-neo4j-from-haystack`  
**ADR / OpenSPDD:** [`../../../adr/0008-neo4j-kg1-kg2-isolation.md`](../../../adr/0008-neo4j-kg1-kg2-isolation.md) · [`../../../spdd/prompt/haystack-devcontainer.md`](../../../spdd/prompt/haystack-devcontainer.md)

**Out of scope (application repo):**

- Agent `trigger_neo4j_populate` wiring into recommend (S8.3; may call this HTTP)
- Attachment / compatibility graph beyond D0 tables
- CDC (Phase 9)

**Related:** [001 merge-sync](../001-haystack-postgres-merge-sync/) · [002 Neo4j DocumentStore](../002-haystack-neo4j/) · [004 pgvector](../004-haystack-pgvector/)
