# Implementation Plan: Haystack Neo4j

**Feature**: `002-haystack-neo4j` | **Status**: Implemented

## Summary

Add Neo4j 5 Community to Haystack Compose for `neo4j-haystack` DocumentStore integration; wire app env; document package install and verification. Preinstall **Neo4j for VS Code** (`neo4j-extensions.neo4j-for-vscode`) in the devcontainer.

## Technical Context

- Docker Compose service `neo4j` (`neo4j:5`), volume `neo4j-haystack-data`
- Network: `heavy-rental-network`
- Ports: 7474 (HTTP), 7687 (Bolt)
- Python: `neo4j-haystack` via `uv` (postCreate or project deps)
- IDE: `neo4j-extensions.neo4j-for-vscode` in `devcontainer.json` extensions; connections UI-managed (not `pgsql.connections`-style); optional settings `neo4j.features.linting` / `neo4j.trace.server`
- Complements existing Postgres (`db` / `db-sync`)

## Structure

```text
Haystack-Fast-API/.devcontainer/
  docker-compose.yml    # + neo4j service, app NEO4J_* env
  devcontainer.json     # + ports 7474, 7687; uv install neo4j-haystack; Neo4j VS Code extension
  scripts/              # unchanged (postgres sync)

specs/002-haystack-neo4j/
  verification.md, contracts/neo4j-env.md, ...
```

## Testing

See [verification.md](./verification.md).
