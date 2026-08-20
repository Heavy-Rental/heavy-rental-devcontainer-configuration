# Architecture Decision Records

Durable **why** for this configuration repository. Specs say what the packs do; these records say why the architecture looks this way and which alternatives were rejected.

Format: [MADR](https://adr.github.io/madr/)-short (Context, Decision, Consequences). Numbering is monotonic across the whole repo (`NNNN-kebab-title.md`) and never reused.

## Rules

1. **Accepted ADRs are immutable.** Do not edit Status, body, or date of an accepted file.
2. To change a decision, add a **new** ADR whose Status is `accepted, supersedes ADR-NNNN` and whose `Supersedes:` field names the old file. Leave the old file unchanged.
3. In-force set = accepted ADRs that no later ADR supersedes.
4. OpenSpec changes MUST review in-force ADRs in `design.md` and complete `openspec/changes/<id>/adr.md` (manifest only). Full decision text lives here, not in the change folder.
5. Location is always this folder — the configuration-repo root `adr/` — even when the OpenSpec change lives under a pack.

Schema: OpenSpec [`spec-driven-with-adr`](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/). Process: [`docs/spec-governance.md`](../docs/spec-governance.md).

## Index

| ID | Title | Status | Supersedes |
|----|-------|--------|------------|
| [0001](./0001-three-packs-shared-external-network.md) | Three independent Compose packs on a shared external network | accepted | — |
| [0002](./0002-rest-primary-oltp-source-of-truth.md) | REST `postgres-primary` is the OLTP source of truth | accepted | — |
| [0003](./0003-haystack-writable-local-postgres-pull-merge.md) | Haystack uses a writable local Postgres with pull merge | accepted | — |
| [0004](./0004-near-real-time-poll-not-cdc.md) | Fleet mirror is a near-real-time poll, not CDC | accepted | — |
| [0005](./0005-rest-dual-packs-promote-devcontainer.md) | REST ships dual packs; operators promote `.devcontainer` | accepted | — |
| [0006](./0006-portal-calls-spring-only.md) | Web portal calls Spring REST only | accepted | — |
| [0007](./0007-pgvector-on-haystack-not-primary.md) | pgvector lives on Haystack Postgres; FAISS is not default | accepted | — |
| [0008](./0008-neo4j-kg1-kg2-isolation.md) | One Neo4j instance; KG-1 DocumentStore isolated from KG-2 fleet | accepted | — |
| [0009](./0009-d0-fleet-schema-contract-allowlist.md) | D0 fleet schema contract and default allowlist | accepted | — |
| [0010](./0010-openspec-openspdd-adr-documentation-model.md) | OpenSpec + OpenSPDD + ADR documentation model | accepted | — |

## In-force set (2026-08-20)

All of ADR-0001 through ADR-0010. None are superseded.
