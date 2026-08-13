# OpenSpec (SDD) artifacts

Lightweight [OpenSpec](https://github.com/Fission-AI/OpenSpec) layout for Spec-Driven Development in this project.

```text
openspec/
├── specs/                         # Source of truth (current behavior)
│   └── haystack-devcontainer/
└── changes/
    └── archive/
        ├── 2026-08-08-add-haystack-postgres-merge-sync/
        ├── 2026-08-08-add-haystack-neo4j/
        ├── 2026-08-09-add-haystack-faiss/
        ├── 2026-08-09-add-neo4j-vscode-extension/
        ├── 2026-08-09-document-neo4j-vscode-ui-connections/
        ├── 2026-08-12-phase4-fleet-mirror-allowlist-d0/
        ├── 2026-08-12-phase5-t5-d4-pgvector-platform/
        ├── 2026-08-13-phase8-t3-populate-neo4j-from-haystack/
        └── 2026-08-13-phase8-t4-neo4j-populate-trigger/
```

## Source of truth

**[specs/haystack-devcontainer/spec.md](./specs/haystack-devcontainer/spec.md)** — agreed **current** behavior:

- Writable local Postgres (`postgres-haystack`) + near-RT merge-sync (`postgres-haystack-sync`, default 60s poll) from `postgres-primary`
- Phase 4: `SYNC_TABLE_ALLOWLIST` (default `asset,booking,category`), cycle lag `METRICS`, D0 schema contract
- Unique-key merge, additive schema evolution, opt-in parity flags / `SYNC_MODE`
- **Phase 5 T5 / D4:** `postgres-haystack` image `pgvector/pgvector:pg17`, extension `vector`, app env `INDEXING_EMBEDDING_DIM=768` (platform ready; I0/I1 app cutover later)
- **Neo4j 5** (`neo4j` / `neo4j-haystack`) for Haystack DocumentStore (`neo4j-haystack` package)
- **Phase 8 T3 / PR-L 8.1 + T4 / PR-M:** `neo4j-populate` fleet SQL → Cypher MERGE (KG-2); post-sync + admin HTTP trigger; never drop KG-1 (`:Document`)
- **Neo4j for VS Code** extension (`neo4j-extensions.neo4j-for-vscode`) installed in the devcontainer; connections are UI-managed (not `pgsql.connections`-style settings)
- App env: `DATABASE_URL` (Postgres) + `INDEXING_EMBEDDING_DIM` + `NEO4J_*` (Bolt)
- **FAISS** is **not** in the default stack (historical Spec Kit `003` / archive only)

## Archived changes

| Archive | Description |
|---|---|
| [2026-08-08-add-haystack-postgres-merge-sync](./changes/archive/2026-08-08-add-haystack-postgres-merge-sync/) | Local Postgres + merge sync |
| [2026-08-08-add-haystack-neo4j](./changes/archive/2026-08-08-add-haystack-neo4j/) | Neo4j for Haystack |
| [2026-08-09-add-haystack-faiss](./changes/archive/2026-08-09-add-haystack-faiss/) | FAISS DocumentStore (historical; later removed from default stack) |
| [2026-08-09-add-neo4j-vscode-extension](./changes/archive/2026-08-09-add-neo4j-vscode-extension/) | Neo4j for VS Code extension |
| [2026-08-09-document-neo4j-vscode-ui-connections](./changes/archive/2026-08-09-document-neo4j-vscode-ui-connections/) | Neo4j IDE connections are UI-managed (not settings profiles) |
| [2026-08-12-phase4-fleet-mirror-allowlist-d0](./changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/) | Phase 4 T1 lag metrics, T2 allowlist, D0 schema contract |
| [2026-08-12-phase5-t5-d4-pgvector-platform](./changes/archive/2026-08-12-phase5-t5-d4-pgvector-platform/) | Phase 5 T5 / D4 pgvector platform ready |
| [2026-08-13-phase8-t3-populate-neo4j-from-haystack](./changes/archive/2026-08-13-phase8-t3-populate-neo4j-from-haystack/) | Phase 8 T3 / PR-L 8.1 fleet Neo4j populate (SQL→MERGE) |
| [2026-08-13-phase8-t4-neo4j-populate-trigger](./changes/archive/2026-08-13-phase8-t4-neo4j-populate-trigger/) | Phase 8.2 T4 / PR-M post-sync + admin HTTP trigger, KG-1 protect |

**Spec Kit (active):**

- [specs/001-haystack-postgres-merge-sync/](../specs/001-haystack-postgres-merge-sync/)
- [specs/002-haystack-neo4j/](../specs/002-haystack-neo4j/)
- [specs/004-haystack-pgvector/](../specs/004-haystack-pgvector/)
- [specs/005-haystack-neo4j-populate/](../specs/005-haystack-neo4j-populate/)

**Spec Kit (historical — not wired in default devcontainer):**

- [specs/003-haystack-faiss/](../specs/003-haystack-faiss/)

### Running verification

- Postgres merge: [001 verification](../specs/001-haystack-postgres-merge-sync/verification.md)
- Neo4j: [002 verification](../specs/002-haystack-neo4j/verification.md)
- pgvector platform: [004 verification](../specs/004-haystack-pgvector/verification.md)
- Fleet Neo4j populate: [005 verification](../specs/005-haystack-neo4j-populate/verification.md)
