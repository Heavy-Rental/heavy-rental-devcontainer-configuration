# Design: Add Neo4j for Haystack

## Approach

- Service `neo4j` / container `neo4j-haystack`, image `neo4j:5`
- Volume `neo4j-haystack-data`
- Ports 7474 (Browser), 7687 (Bolt)
- `NEO4J_AUTH=neo4j/heavyrental`, heap 512m–1G
- Healthcheck: `cypher-shell ... RETURN 1`
- App env: `NEO4J_URI=bolt://neo4j:7687` (+ user/password/database)
- Complements Postgres; does not replace it

## File changes

- `.devcontainer/docker-compose.yml`
- `.devcontainer/devcontainer.json`
- `specs/002-haystack-neo4j/*`
- `openspec/specs/haystack-devcontainer/spec.md`
