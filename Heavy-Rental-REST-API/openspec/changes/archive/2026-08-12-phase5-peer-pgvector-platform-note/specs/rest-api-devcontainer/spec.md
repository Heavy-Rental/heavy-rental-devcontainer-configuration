# Delta: rest-api-devcontainer — Phase 5 peer pgvector note

## ADDED Requirements

### Requirement: Primary does not require pgvector (Phase 5 peer)

Peer Haystack may enable **pgvector** on **its** local database (`postgres-haystack`) for a future DocumentStore cutover. This pack’s `postgres-primary` MUST remain a standard Postgres OLTP image for Spring and MUST NOT require extension `vector` or a pgvector image.

#### Scenario: Primary topology unchanged by Haystack pgvector

- **GIVEN** Haystack pack has pgvector platform ready (T5/D4)
- **WHEN** an operator inspects REST Compose primary image/settings
- **THEN** primary remains plain Postgres 17 (or pack-equivalent) without a pgvector requirement
