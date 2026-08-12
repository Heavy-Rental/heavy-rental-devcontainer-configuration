# Haystack Fast API — Devcontainer pack

This folder ships a **single Compose-based devcontainer** for **Haystack Fast API** local development. The active configuration lives at **`Haystack-Fast-API/.devcontainer/`** (no pack promote step—unlike the REST API dual packs).

| Service | Container | Role |
|---------|-----------|------|
| App | `haystack-fast-api` | Dev workspace for the Haystack Fast API project |
| Local Postgres | `postgres-haystack` | Writable relational DB + **pgvector** (`heavy_rental`; image `pgvector/pgvector:pg17`) |
| Fleet merge-sync | `postgres-haystack-sync` | Near-RT **pull** from REST API `postgres-primary` (~60s poll) |
| Neo4j | `neo4j-haystack` | Graph store for Haystack DocumentStore (neo4j-haystack) |

**Specs (OpenSpec / Spec Kit):** [`openspec/`](./openspec/) · [`specs/001-haystack-postgres-merge-sync/`](./specs/001-haystack-postgres-merge-sync/) · [`specs/002-haystack-neo4j/`](./specs/002-haystack-neo4j/) · [`specs/004-haystack-pgvector/`](./specs/004-haystack-pgvector/)  
**Historical only (not in default stack):** [`specs/003-haystack-faiss/`](./specs/003-haystack-faiss/)

---

## Stack overview

One stack: app + local Postgres + merge-sync job + Neo4j. The app always uses the **local** database, not the REST API primary.

| | **Haystack default stack** |
|---|----------------------------|
| Compose services | `haystack-fast-api`, `postgres-haystack`, `postgres-haystack-sync`, `neo4j` |
| App container | `haystack-fast-api` |
| Local Postgres | `postgres-haystack` — **pgvector/pgvector:pg17**, host port **5434** → container `5432` |
| pgvector | Extension **`vector`** on `heavy_rental` (Phase 5 T5 / D4 platform ready) |
| Sync job | `postgres-haystack-sync` — source `postgres-primary`, target `postgres-haystack` |
| Neo4j | `neo4j-haystack` — Browser **7474**, Bolt **7687** |
| App Postgres URL | `postgresql://postgres:postgres@postgres-haystack:5432/heavy_rental` |
| App embedding dim | `INDEXING_EMBEDDING_DIM=768` (contract for future I0/I1 PgvectorDocumentStore) |
| App Neo4j env | `NEO4J_URI=bolt://neo4j:7687`, user `neo4j`, password `heavyrental` |
| Default sync interval | **60s** poll (`SYNC_INTERVAL_SECONDS`; not CDC) |
| Default table allowlist | `asset,booking,category` (`SYNC_TABLE_ALLOWLIST`; use `all` for full public) |
| VS Code Postgres profiles | **Haystack Local (R/W)** + **REST API Primary (source)** |
| Neo4j IDE | **Neo4j for VS Code** (UI-managed connection; not `pgsql.connections`-style) |
| Best for | Haystack app work with a sandbox Postgres mirror of fleet data + pgvector platform + local Neo4j |
| Peer dependency | REST API stack optional for merge; primary must be up for successful fleet pull |

### Architecture sketch

```text
Heavy-Rental-REST-API (peer)              Haystack-Fast-API (this pack)
────────────────────────────              ────────────────────────────
postgres-primary (OLTP SoT)  ◄──pull──   postgres-haystack-sync
   heavy_rental / public                    (~60s, allowlist)
   (no pgvector required)                     │
                                              ▼
app (Spring) ──R/W──► postgres-primary   postgres-haystack (local R/W)
                                         + pgvector (extension vector)
                                              ▲
haystack-fast-api ──DATABASE_URL──────────────┘
haystack-fast-api ──INDEXING_EMBEDDING_DIM──── (768; future I1)
haystack-fast-api ──NEO4J_*──► neo4j-haystack

host localhost:5434 = postgres-haystack
host localhost:7474 = Neo4j Browser
host localhost:7687 = Neo4j Bolt
```

**Note:** Merge-sync is a **pull** into Haystack. It does **not** write back to the REST API primary. Local-only rows on `postgres-haystack` are retained under default merge mode. When primary is down, the sync job **skips** the cycle and retries (default); local Postgres stays usable.

**Included in this pack**

- App image build from `.devcontainer/Dockerfile` (workspace mount at `/workspaces/haystack-fast-api`)
- External Docker network: **`heavy-rental-network`**
- Postgres 17 + **pgvector** local DB (`pgvector/pgvector:pg17`); name / user / password (dev): `heavy_rental` / `postgres` / `postgres`
- `vector` extension bootstrap (initdb + healthcheck ensure); dim contract `INDEXING_EMBEDDING_DIM=768`
- Forwarded ports: **5434** (Postgres), **7474** / **7687** (Neo4j)
- Extensions: Postgres client (`ms-ossdata.vscode-pgsql`), Neo4j for VS Code (`neo4j-extensions.neo4j-for-vscode`)
- Non-root user `vscode`; `postCreateCommand` fixes workspace ownership and installs `uv` + `neo4j-haystack` (best-effort)
- FAISS is **not** wired in the default Compose / postCreate path
- DocumentStore factory / indexing → Pgvector writer (**I0/I1**) are **application** work, not this pack

---

## Prerequisites

1. [Docker](https://docs.docker.com/get-docker/) and [VS Code](https://code.visualstudio.com/) with the **Dev Containers** extension (`ms-vscode-remote.remote-containers`).
2. Create the shared network once (if it does not exist):

```bash
docker network create heavy-rental-network
```

3. Your Haystack Fast API project sources should live in the workspace the container mounts as `/workspaces/haystack-fast-api` (volume-backed in Compose).
4. **For fleet merge-sync:** start the **Heavy Rental REST API** pack first so container **`postgres-primary`** is healthy on the same network. Without it, sync **skips** cycles and local Postgres still works empty/with local data.

Operator guide for the peer stack: [`../Heavy-Rental-REST-API/README.md`](../Heavy-Rental-REST-API/README.md)

---

## Open in VS Code Dev Containers

VS Code Dev Containers looks for **`.devcontainer`** at the **root of the folder you open**. This pack already has configuration at `Haystack-Fast-API/.devcontainer/`—there is **no** “move pack up one level” step.

### 1. Go to this directory

```bash
cd /path/to/heavy-rental-devcontainer-configuration/Haystack-Fast-API
```

### 2. Confirm layout

```text
Haystack-Fast-API/
  .devcontainer/          ← active (docker-compose.yml, devcontainer.json, scripts/…)
  README.md
  openspec/
  specs/
```

### 3. Open the folder in VS Code Dev Containers

1. Open **VS Code**.
2. **File → Open Folder…** and select **`Haystack-Fast-API`** (the folder that contains `.devcontainer`).
3. When prompted, use **Dev Containers: Reopen in Container**, or the Command Palette:
   - `Dev Containers: Reopen in Container`
4. Wait for the image build and Compose services (`postgres-haystack`, `postgres-haystack-sync`, `neo4j`, app).

Alternatively, from the command palette: **Dev Containers: Open Folder in Container…** and select `Haystack-Fast-API`.

### Optional: Compose only (without full Dev Containers UX)

```bash
cd Haystack-Fast-API/.devcontainer
docker compose up -d
```

---

## Quick verification

```bash
# Local Postgres (writable; not a standby)
docker exec postgres-haystack pg_isready -U postgres -d heavy_rental
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "SELECT pg_is_in_recovery();"
# Expect: f (false)

# pgvector extension (Phase 5 T5 / D4)
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c \
  "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
# Expect: vector | <version>

# Merge-sync job (running loop; merge or skip when primary missing)
docker logs postgres-haystack-sync 2>&1 | tail -50
# Expect: cycle logs; METRICS cycle ... duration_ms=... ; allowlist mode on start

# Neo4j
docker exec neo4j-haystack cypher-shell -u neo4j -p heavyrental 'RETURN 1;'
# Browser: http://localhost:7474

# App env (inside app container)
docker exec haystack-fast-api printenv DATABASE_URL
# Expect: ...@postgres-haystack:5432/heavy_rental
docker exec haystack-fast-api printenv INDEXING_EMBEDDING_DIM
# Expect: 768
docker exec haystack-fast-api printenv | grep NEO4J
```

Full runbooks:

- Postgres merge: [`specs/001-haystack-postgres-merge-sync/verification.md`](./specs/001-haystack-postgres-merge-sync/verification.md) · quickstart: [`specs/001-haystack-postgres-merge-sync/quickstart.md`](./specs/001-haystack-postgres-merge-sync/quickstart.md)
- Neo4j: [`specs/002-haystack-neo4j/verification.md`](./specs/002-haystack-neo4j/verification.md) · quickstart: [`specs/002-haystack-neo4j/quickstart.md`](./specs/002-haystack-neo4j/quickstart.md)
- pgvector platform: [`specs/004-haystack-pgvector/verification.md`](./specs/004-haystack-pgvector/verification.md) · quickstart: [`specs/004-haystack-pgvector/quickstart.md`](./specs/004-haystack-pgvector/quickstart.md)

---

## REST API fleet source (Phase 4 / peer stack)

Shared fleet domain data is owned by the **REST API primary**. This pack **pulls** allowlisted tables into `postgres-haystack`.

```text
Heavy-Rental-REST-API                 Haystack-Fast-API
postgres-primary (heavy_rental)  ◄──  postgres-haystack-sync (poll ~60s)
                                      postgres-haystack (local mirror)
```

| Concern | Owner |
|---------|--------|
| OLTP primary + Spring app | **Heavy-Rental-REST-API** (`postgres-primary` on `heavy-rental-network`) |
| Near-RT merge-sync, allowlist, lag metrics | **This pack** (`postgres-haystack-sync`) |
| D0 schema inventory (consumer) | [specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md](./specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md) |
| D0 schema inventory (producer) | [../Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md](../Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md) |

Default allowlist tables: **`asset`**, **`booking`**, **`category`**. Override with `SYNC_TABLE_ALLOWLIST` in Compose (e.g. `all` for full `public` merge).

---

## Pgvector platform (Phase 5 T5 / D4)

Local Postgres is **pgvector-ready** so the Haystack **application** can later cut over indexing DocumentStore from InMemory to `PgvectorDocumentStore` (I0 factory → I1 pipeline; not implemented in this config pack).

| Item | Value |
|------|--------|
| Image | `pgvector/pgvector:pg17` |
| Extension | `vector` on `heavy_rental` |
| Dim contract | `INDEXING_EMBEDDING_DIM=768` |
| Spec Kit | [`specs/004-haystack-pgvector/`](./specs/004-haystack-pgvector/) |
| App I0/I1 | **haystack-fast-api** application repo (future) |

**Upgraded volumes:** init scripts run only on first data-dir init; the healthcheck also runs `CREATE EXTENSION IF NOT EXISTS vector`. Manual ensure:

```bash
docker exec postgres-haystack \
  psql -U postgres -d heavy_rental -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

REST API **primary** does not need pgvector (fleet OLTP SoT stays plain Postgres 17).

---

## Credentials (local dev only)

| Item | Value |
|------|--------|
| Local Postgres database | `heavy_rental` |
| Local Postgres user / password | `postgres` / `postgres` |
| Host port (local Postgres) | **5434** |
| Neo4j user / password | `neo4j` / `heavyrental` |
| Neo4j Browser | http://localhost:7474 |
| Neo4j Bolt (from host) | `bolt://localhost:7687` |
| Neo4j Bolt (from app container) | `bolt://neo4j:7687` |
| REST primary (peer source) | Container `postgres-primary`, same DB/user/password defaults |

Do not use these credentials outside local development.

---

## Neo4j for VS Code (IDE)

The devcontainer installs **`neo4j-extensions.neo4j-for-vscode`**. Connections are **UI-managed** (not a `pgsql.connections`-style array).

1. Command Palette → **Neo4j: Create new connection** (or Neo4j sidebar **+**).
2. Recommended profile **Haystack Local Neo4j**:

| Field | Inside container | From host |
|-------|------------------|-----------|
| Scheme / URI | `bolt` → `bolt://neo4j:7687` | `bolt://localhost:7687` |
| Host / Port | `neo4j` / `7687` | `localhost` / `7687` |
| User | `neo4j` | `neo4j` |
| Password | `heavyrental` | `heavyrental` |
| Database | `neo4j` | `neo4j` |

3. Connect and run `RETURN 1`.

Postgres IDE profiles are already defined in `devcontainer.json` (`Haystack Local (R/W)` and `REST API Primary (source)`).
