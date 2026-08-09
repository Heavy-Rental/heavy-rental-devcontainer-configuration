# Delta for Haystack Devcontainer

## ADDED Requirements

### Requirement: Neo4j VS Code extension

The Haystack Fast API `devcontainer.json` MUST list the official Neo4j for VS Code extension (`neo4j-extensions.neo4j-for-vscode`) under `customizations.vscode.extensions`. Neo4j Browser on port 7474 remains available. Spec Kit docs MUST document Bolt connection parameters for use inside the container.

#### Scenario: Extension configured for install

- **GIVEN** `Haystack-Fast-API/.devcontainer/devcontainer.json`
- **WHEN** a developer inspects `customizations.vscode.extensions`
- **THEN** `neo4j-extensions.neo4j-for-vscode` is present
