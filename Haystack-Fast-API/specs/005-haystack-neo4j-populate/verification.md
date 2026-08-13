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

## 7. Admin HTTP (T4)

```bash
curl -sS http://localhost:8089/health
curl -sS -X POST http://localhost:8089/v1/populate
curl -sS http://localhost:8089/v1/status
```

**Expect:** health `ok`; populate returns **202**; logs show a cycle.

## 8. Post-sync trigger (T4)

With both sync and populate running and a successful merge:

```bash
docker logs postgres-haystack-sync --tail 50 | grep 'TRIGGER neo4j-populate'
```

**Expect:** `status=ok` when populate is up. Stop populate and re-run a successful merge: trigger may `fail` but cycle `status=success`.

## 9. Never drop KG-1 (T4)

Same as isolation §5 with explicit name KG-1 / `Document`. Optionally:

```bash
docker exec -e FLEET_LABELS=Document neo4j-populate \
  python3 /usr/local/bin/populate_neo4j.py --once
```

**Expect:** refuse write/delete for `Document`; existing Document nodes remain.

## Checklist

| ID | Check | ☐ |
|----|-------|---|
| SC-001 | Service defined | |
| SC-002 | Seed rows → fleet nodes | |
| SC-003 | Document survives rebuild | |
| SC-004 | Spec Kit contracts present | |
| SC-005 | Env overrides documented | |
| SC-006 | Post-sync trigger best-effort | |
| SC-007 | Admin HTTP 202 + cycle | |
| SC-008 | KG-1 labels never dropped | |
