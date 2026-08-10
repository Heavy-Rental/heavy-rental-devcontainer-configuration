# Running Verification: Haystack Postgres Merge Sync

**Feature**: `001-haystack-postgres-merge-sync`  
**Audience**: Developers verifying the feature after implementation or rebuild  
**Maps to**: Success criteria **SC-001–SC-007** in [spec.md](./spec.md)

This runbook is the **source of truth** for runtime verification. OpenSpec task lists point here.

---

## 0. Prerequisites

| Requirement | Notes |
|---|---|
| Docker + Compose v2 | Required |
| External network | `heavy-rental-network` |
| REST API stack | Container **`postgres-primary`** healthy (for merge tests SC-002–SC-004) |
| Haystack stack | Services `postgres-haystack`, `postgres-haystack-sync`, `haystack-fast-api` |

### Create the shared network (once)

```bash
docker network create heavy-rental-network
```

Ignore the error if the network already exists.

### Paths

From the monorepo root `heavy-rental-devcontainer-configuration/`:

| What | Path |
|---|---|
| Compose file | `Haystack-Fast-API/.devcontainer/docker-compose.yml` |
| Sync script | `Haystack-Fast-API/.devcontainer/scripts/sync-from-primary.sh` |
| This runbook | `Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/verification.md` |

Unless noted, Compose commands below assume:

```bash
cd Haystack-Fast-API/.devcontainer
```

---

## 1. Start and confirm the stack

### Option A — Dev Container (recommended)

1. Start / rebuild the **Heavy Rental REST API** devcontainer first (so `postgres-primary` is up).
2. Rebuild and reopen the **Haystack Fast API** devcontainer.

### Option B — Compose only

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

### Confirm containers

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' \
  | grep -E 'postgres-haystack|haystack-fast-api|postgres-primary|NAME' || true
```

| Expected name | Role |
|---|---|
| `postgres-haystack` | Local writable Postgres |
| `postgres-haystack-sync` | Merge scheduler |
| `haystack-fast-api` | App container |
| `postgres-primary` | REST API primary (source) |

### Force a new sync cycle (helper)

Default interval is 60 seconds (near-RT poll). To force a new cycle immediately:

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
docker logs -f postgres-haystack-sync
```

Press `Ctrl+C` to stop following logs (container keeps running unless it halted).

---

## 2. SC-001 — Local writable database

**Goal:** Local DB accepts read/write and is not a standby.

### 2.1 Recovery check

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT current_database(), pg_is_in_recovery();"
```

**Expect:**

| Column | Value |
|---|---|
| `current_database` | `heavy_rental` |
| `pg_is_in_recovery` | `f` |

### 2.2 Write and read

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "
CREATE TABLE IF NOT EXISTS sync_smoke (
  id int PRIMARY KEY,
  note text
);
INSERT INTO sync_smoke (id, note) VALUES (1, 'local-only')
  ON CONFLICT (id) DO NOTHING;
SELECT * FROM sync_smoke ORDER BY id;
"
```

**Expect:** `INSERT` succeeds; `SELECT` returns at least row `id=1`.

### 2.3 App points at local DB (optional)

```bash
docker exec haystack-fast-api printenv DATABASE_URL
```

**Expect:** `postgresql://postgres:postgres@postgres-haystack:5432/heavy_rental`

| SC | Result |
|---|---|
| SC-001 | ☐ Pass / ☐ Fail |

---

## 3. SC-002 — Merge from primary when reachable

**Goal:** With `postgres-primary` up, a successful sync cycle makes primary data available locally.

### 3.1 Confirm primary is up and has objects

```bash
docker exec postgres-primary \
  psql -U postgres -d heavy_rental -c "\dt"
```

**Expect:** Connection succeeds. Tables may be empty on a fresh primary; that is OK (merge can complete with 0 tables).

### 3.2 Inspect sync logs

```bash
docker logs postgres-haystack-sync 2>&1 | tail -n 80
```

If the job already **halted** earlier, recreate it (section 1 helper).

**Expect** (when primary is reachable):

- Log lines about source reachable / merge starting  
- `MERGE public.<table>` and/or `Merge cycle summary`  
- `=== Sync cycle end (success) ===`  
- Then `Sleeping 60s until next cycle` (unless interval was overridden)

**Do not expect** (for this check): `HALT: cannot detect connection`

### 3.3 Confirm local schema after merge

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "\dt"
```

**Expect:**

- If primary had public tables with PKs: those tables exist on local and sample rows match when present on primary.  
- If primary had no tables: success log with 0 tables is acceptable for connectivity + merge path.

| SC | Result |
|---|---|
| SC-002 | ☐ Pass / ☐ Fail |

---

## 4. SC-003 — Local-only rows retained

**Goal:** A row that exists only on local is still present after a successful merge.

### 4.1 Insert a local-only row

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "
INSERT INTO sync_smoke (id, note) VALUES (999, 'local-only-keep')
  ON CONFLICT (id) DO UPDATE SET note = EXCLUDED.note;
SELECT * FROM sync_smoke WHERE id = 999;
"
```

**Note:** `sync_smoke` is local-only (not on primary), so merge will not delete it. For a stronger test, insert a PK that exists only on local into a **table that also exists on primary** (if you have one).

### 4.2 Run another merge cycle

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
docker logs postgres-haystack-sync 2>&1 | tail -n 50
```

**Expect:** Successful cycle (primary up).

### 4.3 Confirm row remains

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT * FROM sync_smoke WHERE id = 999;"
```

**Expect:** Row `999` / `local-only-keep` still present.

| SC | Result |
|---|---|
| SC-003 | ☐ Pass / ☐ Fail |

---

## 5. SC-004 — Shared key: primary wins

**Goal:** When the same primary key exists on both sides with different non-key values, after merge local matches primary.

### 5.1 Pick a real merged table

From sync logs, find a line like `MERGE public.<table> (pk=...)`.  
Replace placeholders below:

- `<table>` — table name  
- `<pk>` — primary key column  
- `<id>` — a key that exists on primary  
- `<col>` — a non-key text/varchar column you can safely change  

### 5.2 Set primary value

```bash
docker exec postgres-primary \
  psql -U postgres -d heavy_rental -c \
  "UPDATE <table> SET <col> = 'from-primary' WHERE <pk> = <id>;"
```

### 5.3 Set different local value

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "UPDATE <table> SET <col> = 'from-local' WHERE <pk> = <id>;"
```

### 5.4 Merge and re-read local

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
# wait for success in logs, then:
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT <pk>, <col> FROM <table> WHERE <pk> = <id>;"
```

**Expect:** `<col>` is `from-primary` (primary wins).

**Skip note:** If primary has no suitable application tables yet, mark SC-004 as **Blocked** and retest when data exists.

| SC | Result |
|---|---|
| SC-004 | ☐ Pass / ☐ Fail / ☐ Blocked |

---

## 6. SC-005 — Primary unavailable (default skip; optional halt)

**Goal:** Missing primary does not wipe local data; local DB stays usable. **Default** is skip+retry; halt remains opt-in.

### 6.1 Confirm default skip mode

In `docker-compose.yml`, `postgres-haystack-sync` should have:

```yaml
HALT_ON_PRIMARY_UNAVAILABLE: "false"
restart: unless-stopped
```

### 6.2 Stop primary (or entire REST API stack)

```bash
docker stop postgres-primary
# or stop the REST API compose stack
```

### 6.3 Recreate sync so it checks connectivity now

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
docker logs postgres-haystack-sync 2>&1 | tail -n 40
```

**Expect (default skip):**

- Message containing `SKIP: primary unavailable` (or equivalent)  
- Job keeps running; sleeps `SYNC_INTERVAL_SECONDS` and retries  
- No successful merge of application tables in that cycle  

### 6.4 Optional — Explicit halt path

Temporarily set:

```yaml
HALT_ON_PRIMARY_UNAVAILABLE: "true"
```

and prefer `restart: "no"` for this test, then recreate:

**Expect:**

- `HALT: cannot detect connection`  
- Process exits (container may show `Exited` if restart is `"no"`)  

Restore defaults afterward.

### 6.5 Local DB still works; prior data intact

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "
SELECT 1 AS ok;
SELECT * FROM sync_smoke WHERE id = 999;
"
```

**Expect:** Queries succeed; local-only row still present if you ran SC-003.

### 6.6 Restore primary for later tests

```bash
docker start postgres-primary
# or bring REST API stack back up; wait until healthy
```

| SC | Result |
|---|---|
| SC-005 | ☐ Pass / ☐ Fail |

---

## 7. SC-006 — Default 60-second schedule

**Goal:** After a cycle, the job schedules the next attempt at 60 seconds (default near-RT poll).

1. Ensure primary is up.  
2. Recreate `postgres-haystack-sync` with **default** env (`SYNC_INTERVAL_SECONDS=60`).  
3. Inspect logs:

```bash
docker logs postgres-haystack-sync 2>&1 | grep -E 'Sleeping|interval='
```

**Expect:**

- Config log shows `interval=60s` (or equivalent)  
- After first cycle: `Sleeping 60s until next cycle`  

| SC | Result |
|---|---|
| SC-006 | ☐ Pass / ☐ Fail |

---

## 8. SC-007 — Second cycle under default (or shorter) interval

**Goal:** A second cycle runs ~60–90 seconds after the first with default near-RT settings.

### 8.1 Use default (or temporary shorter override)

Default is already `"60"`. Optionally set lower for faster tests:

```yaml
SYNC_INTERVAL_SECONDS: "30"
```

Or one-off without permanent edit:

```bash
cd Haystack-Fast-API/.devcontainer
SYNC_INTERVAL_SECONDS=60 docker compose run --rm --entrypoint /bin/bash postgres-haystack-sync \
  -c 'export SYNC_INTERVAL_SECONDS=60; /usr/local/bin/sync-from-primary.sh'
```

Prefer Compose env edit + recreate for a realistic service test:

```bash
cd Haystack-Fast-API/.devcontainer
# after setting SYNC_INTERVAL_SECONDS: "60" in compose:
docker compose up -d --force-recreate postgres-haystack-sync
docker logs -f postgres-haystack-sync
```

**Expect** (primary up):

1. First cycle soon after start  
2. `Sleeping 60s until next cycle`  
3. Second cycle within about 60–90 seconds  

### 8.2 Restore default

If you overrode the interval, set `SYNC_INTERVAL_SECONDS` back to `"60"` and recreate `postgres-haystack-sync`.

| SC | Result |
|---|---|
| SC-007 | ☐ Pass / ☐ Fail / ☐ Skipped |

---

## 9. Optional — Explicit halt mode (not a required SC)

With primary **stopped**, temporarily set:

```yaml
# postgres-haystack-sync environment
HALT_ON_PRIMARY_UNAVAILABLE: "true"
# prefer restart: "no" for this test to avoid restart storms
```

```bash
docker compose up -d --force-recreate postgres-haystack-sync
docker logs -f postgres-haystack-sync
```

**Expect:** `HALT: cannot detect connection...` and process exit.

Restore defaults: `HALT_ON_PRIMARY_UNAVAILABLE: "false"`, `SYNC_INTERVAL_SECONDS: "60"`, `restart: unless-stopped`.

---

## 10. Optional — Host access

If host port `5434` is mapped:

```bash
psql postgresql://postgres:postgres@localhost:5434/heavy_rental -c "SELECT 1;"
```

---

## 10b. Unique-key merge (no PK)

**Goal:** Tables with only a UNIQUE constraint are merged (`ALLOW_UNIQUE_MERGE_KEY=true`, default).

On primary:

```bash
docker exec postgres-primary \
  psql -U postgres -d heavy_rental -c "
CREATE TABLE IF NOT EXISTS uk_demo (
  code text UNIQUE NOT NULL,
  label text
);
INSERT INTO uk_demo (code, label) VALUES ('a', 'from-primary')
  ON CONFLICT (code) DO UPDATE SET label = EXCLUDED.label;
"
```

Force sync:

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
docker logs postgres-haystack-sync 2>&1 | grep -E 'uk_demo|unique'
```

**Expect:** log like `MERGE public.uk_demo (key=unique:code)`; local has row `a`.

Local-only retention:

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "INSERT INTO uk_demo (code, label) VALUES ('local-only', 'keep') ON CONFLICT DO NOTHING;"
# recreate postgres-haystack-sync again, then:
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "SELECT * FROM uk_demo WHERE code = 'local-only';"
```

**Expect:** `local-only` still present.

| Check | Result |
|---|---|
| Unique-key merge | ☐ Pass / ☐ Fail |

---

## 10c. Additive schema evolution (new column)

**Goal:** New columns on primary are added to existing local tables (`SCHEMA_EVOLUTION=true`, default).

On primary (after `uk_demo` already merged once):

```bash
docker exec postgres-primary \
  psql -U postgres -d heavy_rental -c "
ALTER TABLE uk_demo ADD COLUMN IF NOT EXISTS extra text;
UPDATE uk_demo SET extra = 'evolved' WHERE code = 'a';
"
```

Force sync and check local:

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d --force-recreate postgres-haystack-sync
docker logs postgres-haystack-sync 2>&1 | grep -E 'SCHEMA ADD COLUMN|uk_demo'
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT code, label, extra FROM uk_demo WHERE code = 'a';"
```

**Expect:** log `SCHEMA ADD COLUMN public.uk_demo.extra`; local `extra` is `evolved`.

| Check | Result |
|---|---|
| Schema evolution ADD COLUMN | ☐ Pass / ☐ Fail |

---

## 10d. Opt-in flags (defaults off)

Confirm startup log with defaults shows sandbox policy:

```bash
docker logs postgres-haystack-sync 2>&1 | head -n 20
```

**Expect:** `mode=merge`, `drop_orphan=false`, `indexes=false/false`, `type_widen=false`.

### Drop orphan columns (opt-in)

1. Ensure local has an extra column not on primary (e.g. leave a local-only col).  
2. Set `DROP_ORPHAN_COLUMNS: "true"` on `postgres-haystack-sync`, recreate.  
3. **Expect:** log `SCHEMA DROP COLUMN ...`; column gone.  
4. Restore flag to `"false"`.

### Secondary indexes (opt-in)

1. On primary create a non-unique index on a merged table.  
2. Set `SYNC_INDEXES: "true"`, recreate `postgres-haystack-sync`.  
3. **Expect:** log `INDEX CREATE ...`; index exists on local.  
4. Restore flag to `"false"`.

### Safe type widenings (opt-in)

1. Local column `integer`, primary altered to `bigint` (or test table).  
2. Set `SAFE_TYPE_WIDENINGS: "true"`, recreate.  
3. **Expect:** log `SCHEMA TYPE WIDEN ...` or skip if types already match.

### Mirror mode (aggressive)

```yaml
SYNC_MODE: mirror
```

**Expect:** startup enables drop/indexes/type_widen/fk flags; FK still WARN not implemented.

---

## 11. Pass / fail checklist

| ID | Check | Result |
|---|---|---|
| SC-001 | Local write works; not in recovery | ☐ Pass / ☐ Fail |
| SC-002 | Merge from primary when reachable | ☐ Pass / ☐ Fail |
| SC-003 | Local-only row retained after merge | ☐ Pass / ☐ Fail |
| SC-004 | Shared key: primary wins | ☐ Pass / ☐ Fail / ☐ Blocked |
| SC-005 | Primary down: skip (default) or halt (opt-in); local still R/W | ☐ Pass / ☐ Fail |
| SC-006 | Default sleep 60 logged | ☐ Pass / ☐ Fail |
| SC-007 | Second cycle ~60s | ☐ Pass / ☐ Fail / ☐ Skipped |
| UK | Unique-key merge (no PK) | ☐ Pass / ☐ Fail / ☐ Skipped |
| EV | Additive schema evolution | ☐ Pass / ☐ Fail / ☐ Skipped |
| OPT | Defaults keep drop/index/type off | ☐ Pass / ☐ Fail |
| OPT | Opt-in drop / index / widen (as needed) | ☐ Pass / ☐ Fail / ☐ Skipped |

**Feature verification pass:** SC-001, SC-002, SC-003, SC-005, SC-006 pass; SC-004 when data allows; SC-007 recommended; UK + EV when testing the extended merge behavior; defaults remain sandbox-safe.

---

## 12. Troubleshooting

| Symptom | What to check |
|---|---|
| Cannot resolve `postgres-primary` | REST API stack up? Both on `heavy-rental-network`? |
| `postgres-haystack-sync` already exited | Halt mode enabled or crash — check logs; with defaults expect skip not exit. Recreate: `docker compose up -d --force-recreate postgres-haystack-sync` |
| Auth failures | `postgres` / `postgres` on both stacks |
| Tables skipped | Source needs a **primary key** or **unique** key (if `ALLOW_UNIQUE_MERGE_KEY=true`) |
| New column missing locally | `SCHEMA_EVOLUTION=true`? Recreate `postgres-haystack-sync` after primary ALTER |
| App still on wrong host | `DATABASE_URL` → `postgres-haystack`, not `postgres-primary` |
| Empty merge | Primary `public` has no tables yet — SC-002 path still valid if logs show success |
| Port 5434 in use | Change host mapping in Compose or free the port |

---

## 13. After verification

1. Tick remaining items in:
   - [tasks.md](./tasks.md) — T007, T026, T028  
   - [OpenSpec archived tasks §6](../../openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/tasks.md)  
2. OpenSpec change is **archived** (2026-08-08). Source of truth: [openspec/specs/haystack-devcontainer/spec.md](../../openspec/specs/haystack-devcontainer/spec.md).

---

## Related artifacts

| Artifact | Path |
|---|---|
| Feature spec (SC-*) | [spec.md](./spec.md) |
| Env contract | [contracts/postgres-haystack-sync-env.md](./contracts/postgres-haystack-sync-env.md) |
| Implementation plan | [plan.md](./plan.md) |
| Short entry point | [quickstart.md](./quickstart.md) |
| OpenSpec SoT | `openspec/specs/haystack-devcontainer/spec.md` |
| OpenSpec archive | `openspec/changes/archive/2026-08-08-add-haystack-postgres-merge-sync/` |
| Compose | `Haystack-Fast-API/.devcontainer/docker-compose.yml` |
