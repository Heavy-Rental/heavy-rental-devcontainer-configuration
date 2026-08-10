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
        └── 2026-08-09-document-neo4j-vscode-ui-connections/
```

## Source of truth

**[specs/haystack-devcontainer/spec.md](./specs/haystack-devcontainer/spec.md)** — agreed **current** behavior:

- Writable local Postgres (`postgres-haystack`) + near-RT merge-sync (`postgres-haystack-sync`, default 60s poll) from `postgres-primary`
- Unique-key merge, additive schema evolution, opt-in parity flags / `SYNC_MODE`
- **Neo4j 5** (`neo4j` / `neo4j-haystack`) for Haystack DocumentStore (`neo4j-haystack` package)
- **Neo4j for VS Code** extension (`neo4j-extensions.neo4j-for-vscode`) installed in the devcontainer; connections are UI-managed (not `pgsql.connections`-style settings)
- App env: `DATABASE_URL` (Postgres) + `NEO4J_*` (Bolt)
- **FAISS** is **not** in the default stack (historical Spec Kit `003` / archive only)

## Archived changes

| Archive | Description |
|---|---|
| [2026-08-08-add-haystack-postgres-merge-sync](./changes/archive/2026-08-08-add-haystack-postgres-merge-sync/) | Local Postgres + merge sync |
| [2026-08-08-add-haystack-neo4j](./changes/archive/2026-08-08-add-haystack-neo4j/) | Neo4j for Haystack |
| [2026-08-09-add-haystack-faiss](./changes/archive/2026-08-09-add-haystack-faiss/) | FAISS DocumentStore (historical; later removed from default stack) |
| [2026-08-09-add-neo4j-vscode-extension](./changes/archive/2026-08-09-add-neo4j-vscode-extension/) | Neo4j for VS Code extension |
| [2026-08-09-document-neo4j-vscode-ui-connections](./changes/archive/2026-08-09-document-neo4j-vscode-ui-connections/) | Neo4j IDE connections are UI-managed (not settings profiles) |

**Spec Kit (active):**

- [specs/001-haystack-postgres-merge-sync/](../specs/001-haystack-postgres-merge-sync/)
- [specs/002-haystack-neo4j/](../specs/002-haystack-neo4j/)

**Spec Kit (historical — not wired in default devcontainer):**

- [specs/003-haystack-faiss/](../specs/003-haystack-faiss/)

### Running verification

- Postgres merge: [001 verification](../specs/001-haystack-postgres-merge-sync/verification.md)
- Neo4j: [002 verification](../specs/002-haystack-neo4j/verification.md)
