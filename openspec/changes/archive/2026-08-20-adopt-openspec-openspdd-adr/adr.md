# ADR Review Manifest

## ADR Review Completed

- Date: 2026-08-20
- Reviewer: configuration-repo maintainers
- Change: `2026-08-20-adopt-openspec-openspdd-adr`

## In-Force ADR Context Reviewed

- None: no existing repository-level ADRs were present before this change.

## Repository-Level ADRs Created

- `adr/0001-three-packs-shared-external-network.md` — independent Compose packs on `heavy-rental-network`
- `adr/0002-rest-primary-oltp-source-of-truth.md` — primary is sole product OLTP writer
- `adr/0003-haystack-writable-local-postgres-pull-merge.md` — local writable DB + pull merge
- `adr/0004-near-real-time-poll-not-cdc.md` — 60s poll, skip when primary down
- `adr/0005-rest-dual-packs-promote-devcontainer.md` — two REST packs + promote rule
- `adr/0006-portal-calls-spring-only.md` — portal HTTP to Spring only
- `adr/0007-pgvector-on-haystack-not-primary.md` — pgvector on Haystack; FAISS not default
- `adr/0008-neo4j-kg1-kg2-isolation.md` — one Neo4j; populate never drops KG-1
- `adr/0009-d0-fleet-schema-contract-allowlist.md` — D0 `asset,booking,category`
- `adr/0010-openspec-openspdd-adr-documentation-model.md` — three-layer documentation model

## Notes

These ADRs backfill as-built decisions previously recorded only in archived OpenSpec `design.md` files and `ARCHITECTURE.md`.
