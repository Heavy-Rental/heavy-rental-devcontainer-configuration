# Delta for Haystack Devcontainer

## MODIFIED Requirements

### Requirement: Neo4j VS Code extension

Connections MUST be created via the extension UI. The stack MUST NOT claim a `pgsql.connections`-style Neo4j settings array. Supported settings only: `neo4j.features.linting`, `neo4j.trace.server` (optional). Docs MUST list recommended Haystack Local Neo4j fields.

#### Scenario: Connection is UI-managed, not settings profiles

- **GIVEN** the official Neo4j for VS Code extension
- **WHEN** a developer looks for a settings-based connection profile array
- **THEN** they use **Neo4j: Create new connection** with documented Haystack values instead
