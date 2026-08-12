# OpenSpec (SDD) artifacts — Heavy Rental REST API

Lightweight OpenSpec layout for Spec-Driven Development of the REST API **devcontainer packs**.

```text
openspec/
├── specs/
│   └── rest-api-devcontainer/     # Source of truth
└── changes/
    └── archive/
        ├── 2026-08-09-add-rest-api-devcontainer-variants/
        └── 2026-08-12-phase4-d0-schema-contract-fleet-source/
```

## Source of truth

**[specs/rest-api-devcontainer/spec.md](./specs/rest-api-devcontainer/spec.md)** — agreed **current** behavior:

- Two operator-selectable packs (with / without PostgreSQL streaming read replica)
- Promote chosen pack’s `.devcontainer` **one level up** to `Heavy-Rental-REST-API/.devcontainer`
- Shared: Java app service, primary Postgres, `heavy-rental-network`, Spring datasource → primary
- With-replica: `db-replica-one` on host **5433**, streaming standby
- Without-replica: primary only
- Phase 4: primary is Haystack fleet **pull source**; D0 producer schema contract (`asset`, `booking`, `category`)

## Archived changes

| Archive | Description |
|---|---|
| [2026-08-09-add-rest-api-devcontainer-variants](./changes/archive/2026-08-09-add-rest-api-devcontainer-variants/) | Document dual packs + promote workflow |
| [2026-08-12-phase4-d0-schema-contract-fleet-source](./changes/archive/2026-08-12-phase4-d0-schema-contract-fleet-source/) | Phase 4 D0 schema contract + fleet source docs |

## Spec Kit

- [specs/001-rest-api-devcontainer/](../specs/001-rest-api-devcontainer/)

### Running verification

- [001 verification](../specs/001-rest-api-devcontainer/verification.md)

### Operator README

- [Heavy-Rental-REST-API/README.md](../README.md)
