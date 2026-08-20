# OpenSpec (SDD) artifacts — Heavy Rental Web Portal

Lightweight OpenSpec layout for Spec-Driven Development of the Web Portal **devcontainer pack**. Durable ADRs live at the configuration-repo root [`../../adr/`](../../adr/) (`schema: spec-driven-with-adr`).

```text
openspec/
├── config.yaml                    # schema: spec-driven-with-adr
├── specs/
│   └── web-portal-devcontainer/   # Source of truth
└── changes/
    └── archive/
        └── 2026-08-20-add-web-portal-devcontainer/
```

## Source of truth

**[specs/web-portal-devcontainer/spec.md](./specs/web-portal-devcontainer/spec.md)** — agreed **current** behavior:

- Single Compose service `heavy-rental-web-portal` on external `heavy-rental-network`
- No local Postgres or Neo4j
- Forward port **5173**; remote user `node`
- Product HTTP to peer REST API only (Haystack is optional dual-hop behind Spring)
- `.devcontainer` already at pack root (no REST-style promote step)

## Archived changes

| Archive | Description |
|---|---|
| [2026-08-20-add-web-portal-devcontainer](./changes/archive/2026-08-20-add-web-portal-devcontainer/) | Document as-built portal pack in OpenSpec + Spec Kit |

## Spec Kit

- [specs/001-web-portal-devcontainer/](../specs/001-web-portal-devcontainer/)

### Running verification

- [001 verification](../specs/001-web-portal-devcontainer/verification.md)

### Operator README

- [Heavy-Rental-Web-Portal/README.md](../README.md)

### Platform docs

- [`../../docs/spec-governance.md`](../../docs/spec-governance.md)
- [`../../adr/0006-portal-calls-spring-only.md`](../../adr/0006-portal-calls-spring-only.md)
- [`../../spdd/prompt/web-portal-devcontainer.md`](../../spdd/prompt/web-portal-devcontainer.md)
