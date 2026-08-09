# Design: Neo4j VS Code UI connections

## Approach

- Extension stores connections in globalState + SecretStorage (not workspace settings).
- Devcontainer sets only declared settings: linting/trace.
- Docs prescribe UI flow: **Neo4j: Create new connection** with host `neo4j`, port `7687`, auth `neo4j`/`heavyrental`.

## Files

- `.devcontainer/devcontainer.json`
- `specs/002-haystack-neo4j/*`
- `openspec/specs/haystack-devcontainer/spec.md`
- `openspec/README.md`
