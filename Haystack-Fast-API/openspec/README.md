# OpenSpec (SDD) artifacts

Lightweight [OpenSpec](https://github.com/Fission-AI/OpenSpec) layout for Spec-Driven Development in this project.

```text
openspec/
├── specs/                         # Source of truth (current behavior)
│   └── haystack-devcontainer/
└── changes/
    └── archive/                   # Completed change packages
        └── 2026-08-08-add-haystack-postgres-merge-sync/
```

## Source of truth

**[specs/haystack-devcontainer/spec.md](./specs/haystack-devcontainer/spec.md)** — agreed **current** behavior of the Haystack Fast API devcontainer:

- Writable local Postgres (`db` / `postgres-haystack`)
- App `DATABASE_URL` → local `db`
- Merge-sync from `postgres-primary` / `heavy_rental` (FDW upsert, 24h, halt/skip)
- Unique-key merge when no PK; additive schema evolution (default)
- Opt-in parity: drop orphan columns, secondary indexes, safe type widenings, `SYNC_MODE=mirror`
- `public` schema only; FK sync reserved / not implemented

## Archived changes

| Archive | Description |
|---|---|
| [2026-08-08-add-haystack-postgres-merge-sync](./changes/archive/2026-08-08-add-haystack-postgres-merge-sync/) | Initial local Postgres + 24h merge sync change package |

Each archive keeps `proposal.md`, `design.md`, `tasks.md`, and historical **delta** specs.

Later enhancements (unique-key merge, additive evolution, opt-in flags) were folded into the **source of truth** above and Spec Kit docs without a second archive package.

**Spec Kit twin (feature package):** [specs/001-haystack-postgres-merge-sync/](../specs/001-haystack-postgres-merge-sync/)

### Running verification

Runtime checks (SC-001–SC-007 + UK/EV/opt-in):

**→ [specs/001-haystack-postgres-merge-sync/verification.md](../specs/001-haystack-postgres-merge-sync/verification.md)**

Env contract:

**→ [specs/001-haystack-postgres-merge-sync/contracts/db-sync-env.md](../specs/001-haystack-postgres-merge-sync/contracts/db-sync-env.md)**
