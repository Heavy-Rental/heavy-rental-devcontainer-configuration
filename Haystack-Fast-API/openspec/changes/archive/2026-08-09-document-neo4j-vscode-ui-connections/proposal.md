# Proposal: Document Neo4j VS Code UI connections

## Intent

Clarify that **Neo4j for VS Code** cannot be preconfigured with connection profiles in `devcontainer.json` the way Postgres uses `pgsql.connections`. Document the recommended **Haystack Local Neo4j** UI connection and supported settings keys only.

## Scope

In scope:
- `devcontainer.json` comments + supported settings (`neo4j.features.linting`, `neo4j.trace.server`)
- Spec Kit `002` and OpenSpec SoT wording

Out of scope:
- Seeding extension globalState/SecretStorage
- Third-party multi-DB clients
