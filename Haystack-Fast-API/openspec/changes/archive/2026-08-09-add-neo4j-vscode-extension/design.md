# Design: Neo4j for VS Code extension

## Approach

- Extension ID: `neo4j-extensions.neo4j-for-vscode`
- File: `.devcontainer/devcontainer.json` → `customizations.vscode.extensions`
- Connection (inside container): `bolt://neo4j:7687`, user `neo4j`, password `heavyrental`, database `neo4j`
- Browser remains `http://localhost:7474` (host / forward)

## File changes

- `.devcontainer/devcontainer.json`
- `specs/002-haystack-neo4j/*` (docs + FR)
- `openspec/specs/haystack-devcontainer/spec.md`
- `openspec/README.md`
