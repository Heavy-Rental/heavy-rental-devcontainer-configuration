# Implementation Plan: Fleet Neo4j Populate

**Feature**: `005-haystack-neo4j-populate` | **Status**: Implemented

## Summary

Add a Compose job that projects D0 fleet tables from `postgres-haystack` into Neo4j with Cypher `MERGE`, using fleet labels isolated from DocumentStore.

## Structure

```text
Haystack-Fast-API/.devcontainer/
  Dockerfile.neo4j-populate
  docker-compose.yml          # + neo4j-populate service
  scripts/
    populate_neo4j.py         # SQL → MERGE worker
    populate-neo4j-from-haystack.sh
```

## Technical context

- Python 3.12 + `psycopg` + `neo4j` driver
- Interval poll (default 60s), soft-skip on dependency failure
- Modes: `merge` (default), `rebuild` (label-scoped clear then MERGE)
- Relationships (best-effort): `IN_CATEGORY`, `FOR_ASSET` when FK columns exist

## Testing

See [verification.md](./verification.md).
