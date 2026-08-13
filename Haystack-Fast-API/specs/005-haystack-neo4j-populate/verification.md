# Running Verification: Fleet Neo4j Populate

**Feature**: `005-haystack-neo4j-populate`

## 1. Compose service present

```bash
cd Haystack-Fast-API/.devcontainer
docker compose config --services | grep neo4j-populate
```

**Expect:** `neo4j-populate` listed.

## 2. Job running

```bash
docker ps --filter name=neo4j-populate --format '{{.Status}}'
docker logs neo4j-populate --tail 30
```

**Expect:** container up; log lines include `Config:` and `METRICS populate`.

## 3. Empty / missing tables soft path

With no `asset`/`booking`/`category` tables:

**Expect:** cycle `status=ok` with `skipped_missing` or zero merges; no crash loop.

## 4. Seed → MERGE

```bash
docker exec -i postgres-haystack psql -U postgres -d heavy_rental <<'SQL'
CREATE TABLE IF NOT EXISTS public.category (
  id text PRIMARY KEY,
  name text
);
CREATE TABLE IF NOT EXISTS public.asset (
  id text PRIMARY KEY,
  name text,
  category_id text
);
CREATE TABLE IF NOT EXISTS public.booking (
  id text PRIMARY KEY,
  asset_id text,
  status text
);
INSERT INTO public.category (id, name) VALUES ('cat-1', 'scissor lift')
  ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
INSERT INTO public.asset (id, name, category_id) VALUES ('AST-1', 'Lift A', 'cat-1')
  ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;
INSERT INTO public.booking (id, asset_id, status) VALUES ('BKG-1', 'AST-1', 'confirmed')
  ON CONFLICT (id) DO UPDATE SET asset_id = EXCLUDED.asset_id, status = EXCLUDED.status;
SQL

docker exec neo4j-populate python3 /usr/local/bin/populate_neo4j.py --once

docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental \
  'MATCH (a:Asset {id: "AST-1"}) RETURN a.id, a.name'
```

**Expect:** row returned; logs show `MERGE label=Asset`.

## 5. Isolation (DocumentStore)

```bash
docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental \
  'CREATE (d:Document {id: "doc-isolation-test"}) RETURN d.id'

docker exec -e POPULATE_MODE=rebuild neo4j-populate \
  python3 /usr/local/bin/populate_neo4j.py --once

docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental \
  'MATCH (d:Document {id: "doc-isolation-test"}) RETURN d.id'
```

**Expect:** Document still present; fleet nodes re-MERGED.

## 6. Idempotency

Run `--once` twice; Cypher counts for `:Asset` unchanged for same seed.

## Checklist

| ID | Check | ☐ |
|----|-------|---|
| SC-001 | Service defined | |
| SC-002 | Seed rows → fleet nodes | |
| SC-003 | Document survives rebuild | |
| SC-004 | Spec Kit contracts present | |
| SC-005 | Env overrides documented | |
