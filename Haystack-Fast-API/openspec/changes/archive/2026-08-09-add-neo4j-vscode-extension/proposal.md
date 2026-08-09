# Proposal: Neo4j for VS Code extension

## Intent

Preinstall the official **Neo4j for VS Code** extension in the Haystack Fast API devcontainer so developers can run Cypher / connect over Bolt from the IDE, complementary to Neo4j Browser on port 7474.

## Scope

In scope:
- `devcontainer.json` extension ID `neo4j-extensions.neo4j-for-vscode`
- Spec Kit `002` docs (connection guidance, verification)
- OpenSpec SoT requirement for the extension

Out of scope:
- Changing Neo4j Compose service, ports, or auth
- Preconfiguring extension-specific settings JSON (document connection steps instead)
- Replacing Neo4j Browser

## Approach

Same pattern as `ms-ossdata.vscode-pgsql`: list the extension under `customizations.vscode.extensions`; document Bolt URI `bolt://neo4j:7687` and dev credentials in Spec Kit.
