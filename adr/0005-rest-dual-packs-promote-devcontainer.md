# ADR-0005: REST ships dual packs; operators promote `.devcontainer`

- Status: accepted
- Date: 2026-08-20
- Tags: rest-api, pack-layout

## Context

Some developers want a streaming Postgres replica for HA / read experiments. Others want a single primary to save RAM. VS Code Dev Containers resolves `.devcontainer` at the folder opened in the IDE (`Heavy-Rental-REST-API/`), so two complete configs cannot both sit at that path.

## Decision

Ship **two named pack folders**, each with a nested `.devcontainer`:

- `Spring Boot REST API devcontainer with PostgreSQL Read Replica`
- `Spring Boot REST API devcontainer without read replica`

Operators **promote** the chosen pack’s `.devcontainer` one level up to `Heavy-Rental-REST-API/.devcontainer` before opening the folder. Both packs share the same app container and **always** point Spring at primary (`jdbc:postgresql://db-primary:5432/heavy_rental`). Replica is optional infrastructure, not default app read routing.

Haystack and Web Portal packs already have `.devcontainer` at pack root (no promote step).

## Consequences

- Git history of the nested packs stays intact; only one active config at a time.
- Switching packs requires removing/replacing the active `.devcontainer`.
- Replica host port is **5433**; primary is **5432** in both packs.

## Related

- OpenSpec: `Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md`
- Spec Kit: `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/`
