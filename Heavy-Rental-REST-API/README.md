# Heavy Rental REST API — Devcontainer packs

This folder ships **two optional Spring Boot / Java devcontainer packs**. They are **not** active until you choose one and **move its `.devcontainer` up one level** so it sits directly under `Heavy-Rental-REST-API/`.

| Pack folder | Profile |
|-------------|---------|
| [`Spring Boot REST API devcontainer with PostgreSQL Read Replica/`](./Spring%20Boot%20REST%20API%20devcontainer%20with%20PostgreSQL%20Read%20Replica/) | App + **primary** Postgres + **streaming read replica** |
| [`Spring Boot REST API devcontainer without read replica/`](./Spring%20Boot%20REST%20API%20devcontainer%20without%20read%20replica/) | App + **primary** Postgres only |

**Specs (OpenSpec / Spec Kit):** [`openspec/`](./openspec/) · [`specs/001-rest-api-devcontainer/`](./specs/001-rest-api-devcontainer/)

---

## Difference: with vs without read replica

Both packs share the same application container and primary database. The **only major product difference** is whether a second Postgres instance acts as a **read-only standby**.

| | **With PostgreSQL Read Replica** | **Without read replica** |
|---|----------------------------------|---------------------------|
| Compose services | `heavy-rental-rest-api`, `db-primary`, **`db-replica-one`** | `heavy-rental-rest-api`, `db-primary` only |
| Primary container | `postgres-primary` | `postgres-primary` |
| Replica container | **`postgres-replica-one`** (streaming standby) | none |
| Host ports | **5432** primary, **5433** replica | **5432** primary only |
| Primary config | Custom `postgresql.conf` / `pg_hba.conf` + `replicator` role | Stock `postgres:17` defaults |
| How replica starts | `pg_basebackup` from primary, `standby.signal`, slot `replica_slot` | N/A |
| App JDBC URL | Always **primary**: `jdbc:postgresql://db-primary:5432/heavy_rental` | Same (primary) |
| VS Code Postgres profiles | Primary **+** “Replica (Read)” | Primary only |
| Best for | Learning HA / read scaling / optional multi-datasource experiments | Simple local API + one writable DB |
| Resource use | Higher (2 Postgres instances) | Lower |

### Architecture sketch

```text
WITH READ REPLICA                         WITHOUT READ REPLICA
─────────────────                         ────────────────────
app ──write──► db-primary (R/W)           app ──write──► db-primary (R/W)
                    │                          (only Postgres)
                    │ streaming replication
                    ▼
              db-replica-one (read)

host localhost:5432 = primary             host localhost:5432 = primary
host localhost:5433 = replica
```

**Note:** Even in the **with replica** pack, Spring Boot’s default datasource still targets **primary**. The replica is on the Docker network and available in the IDE for **read** connections; routing app read traffic to the replica is application configuration, not enabled automatically by this pack.

**Shared in both packs**

- Java 21 + Maven base image (`mcr.microsoft.com/devcontainers/java:3-21-trixie`)
- External Docker network: **`heavy-rental-network`**
- Database name / user / password (dev): `heavy_rental` / `postgres` / `postgres`
- Forwarded app port **8080**
- Extensions: Java Pack, Spring Boot Extension Pack, Postgres client
- Non-root user `vscode`; `postCreateCommand` fixes workspace ownership

---

## Prerequisites

1. [Docker](https://docs.docker.com/get-docker/) and [VS Code](https://code.visualstudio.com/) with the **Dev Containers** extension (`ms-vscode-remote.remote-containers`).
2. Create the shared network once (if it does not exist):

```bash
docker network create heavy-rental-network
```

3. Your Spring Boot project sources should live in the workspace the container mounts as `/workspaces/heavy-rental-rest-api` (volume-backed in Compose).

---

## Choose a pack and move `.devcontainer` up one level

VS Code Dev Containers looks for **`.devcontainer`** at the **root of the folder you open** (here: `Heavy-Rental-REST-API/`). The packs keep config one level deeper on purpose so you can pick.

### 1. Go to this directory

```bash
cd /path/to/heavy-rental-devcontainer-configuration/Heavy-Rental-REST-API
```

### 2. If an active `.devcontainer` already exists, remove or rename it

```bash
# Only if you are switching packs
rm -rf .devcontainer
# or: mv .devcontainer .devcontainer.bak
```

### 3. Move the chosen pack’s `.devcontainer` up one level

**Option A — with read replica (recommended if you need standby):**

```bash
mv "Spring Boot REST API devcontainer with PostgreSQL Read Replica/.devcontainer" ./.devcontainer
```

**Option B — without read replica (simpler):**

```bash
mv "Spring Boot REST API devcontainer without read replica/.devcontainer" ./.devcontainer
```

After either command, layout should look like:

```text
Heavy-Rental-REST-API/
  .devcontainer/          ← active (docker-compose.yml, devcontainer.json, …)
  README.md
  openspec/
  specs/
  Spring Boot REST API devcontainer with PostgreSQL Read Replica/   # may be empty after move
  Spring Boot REST API devcontainer without read replica/
```

You may delete empty pack folders after promoting, or keep them as labels. To switch packs later, move the other pack’s `.devcontainer` into place (restore from git if you already moved it).

### 4. Open the folder in VS Code Dev Containers

1. Open **VS Code**.
2. **File → Open Folder…** and select **`Heavy-Rental-REST-API`** (the folder that now contains `.devcontainer`).
3. When prompted, use **Dev Containers: Reopen in Container**, or the Command Palette:
   - `Dev Containers: Reopen in Container`
4. Wait for the image build and Compose services (primary; and replica if you chose Option A).

Alternatively, from the command palette: **Dev Containers: Open Folder in Container…** and select `Heavy-Rental-REST-API`.

---

## Quick verification

```bash
# Primary (both packs)
docker exec postgres-primary pg_isready -U postgres -d heavy_rental

# Replica only (with-replica pack)
docker exec postgres-replica-one pg_isready -U postgres -d heavy_rental
docker exec postgres-replica-one \
  psql -U postgres -d heavy_rental -c "SELECT pg_is_in_recovery();"
# Expect: t (true) on a healthy standby

# App datasource (inside app container)
docker exec heavy-rental-rest-api printenv | grep SPRING_DATASOURCE
```

Full runbooks: [`specs/001-rest-api-devcontainer/verification.md`](./specs/001-rest-api-devcontainer/verification.md) · quickstart: [`specs/001-rest-api-devcontainer/quickstart.md`](./specs/001-rest-api-devcontainer/quickstart.md)

---

## Haystack fleet mirror (Phase 4 / peer stack)

This pack’s **primary** Postgres is the **source of truth** for shared fleet domain data used by Haystack Fast API.

```text
Heavy-Rental-REST-API                 Haystack-Fast-API
postgres-primary (heavy_rental)  ◄──  postgres-haystack-sync (poll ~60s)
                                      postgres-haystack (local mirror)
```

| Concern | Owner |
|---------|--------|
| OLTP primary + app | **This pack** (`postgres-primary` on `heavy-rental-network`) |
| Near-RT merge-sync, allowlist, lag metrics | **Haystack-Fast-API** |
| D0 schema inventory | [specs/001-rest-api-devcontainer/contracts/schema-contract.md](./specs/001-rest-api-devcontainer/contracts/schema-contract.md) |

Default Haystack allowlist tables: **`asset`**, **`booking`**, **`category`**. This pack does **not** run a push/sync job.

---

## Credentials (local dev only)

| Item | Value |
|------|--------|
| Database | `heavy_rental` |
| User / password | `postgres` / `postgres` |
| Replication user (with-replica pack only) | `replicator` / `replicatorpass` |

Do not use these credentials outside local development.
