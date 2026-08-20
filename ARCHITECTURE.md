# Heavy Rental Platform Architecture

This document explains how the three local-development packs in this repository work together:

| Pack folder | Runtime role | Primary tech |
|-------------|--------------|--------------|
| [`Heavy-Rental-Web-Portal/`](./Heavy-Rental-Web-Portal/) | Browser UI | React / TypeScript / Vite |
| [`Heavy-Rental-REST-API/`](./Heavy-Rental-REST-API/) | Business HTTP API + OLTP source of truth | Spring Boot / Java 21 / PostgreSQL 17 |
| [`Haystack-Fast-API/`](./Haystack-Fast-API/) | Recommend / retrieval / graph + vector plane | FastAPI / Haystack / Postgres+pgvector / Neo4j |

These folders ship **devcontainer + Compose** configurations (and specs). Application source code for each service typically lives in its own workspace volume once the container is open.

Specifications use **OpenSpec** (behavior), **OpenSPDD** REASONS canvases (implementation contract), and **ADR** (why). Start with [`docs/spec-governance.md`](./docs/spec-governance.md) and [`adr/README.md`](./adr/README.md).

---

## Table of contents

1. [System purpose](#1-system-purpose)
2. [High-level architecture](#2-high-level-architecture)
3. [Shared infrastructure](#3-shared-infrastructure)
4. [Heavy-Rental-Web-Portal](#4-heavy-rental-web-portal)
5. [Heavy-Rental-REST-API](#5-heavy-rental-rest-api)
6. [Haystack-Fast-API](#6-haystack-fast-api)
7. [Cross-service data flows](#7-cross-service-data-flows)
8. [Domain model (fleet D0)](#8-domain-model-fleet-d0)
9. [Storage planes](#9-storage-planes)
10. [Network, ports, and DNS](#10-network-ports-and-dns)
11. [Trust boundaries and write ownership](#11-trust-boundaries-and-write-ownership)
12. [Failure modes and resilience](#12-failure-modes-and-resilience)
13. [Local development topology](#13-local-development-topology)
14. [Credentials (local dev only)](#14-credentials-local-dev-only)
15. [Phase roadmap (as reflected in packs)](#15-phase-roadmap-as-reflected-in-packs)
16. [Spec governance (OpenSpec, OpenSPDD, ADR)](#16-spec-governance-openspec-openspdd-adr)
17. [Where to read more](#17-where-to-read-more)

---

## 1. System purpose

The Heavy Rental platform supports equipment rental operations (assets, bookings, categories) with:

- A **web portal** for operators and users.
- A **Spring Boot REST API** as the transactional system of record (OLTP).
- A **Haystack Fast API** stack for near-real-time fleet mirroring, graph projection, and (future) vector-backed recommend / indexing.

Architecturally, the design separates:

| Concern | Owner |
|---------|--------|
| User-facing UX | Web Portal |
| Authoritative CRUD / business rules | REST API + `postgres-primary` |
| Fleet mirror, graph KG, vector platform | Haystack stack |
| Shared Docker connectivity | External network `heavy-rental-network` |

The portal does **not** talk to Haystack or databases directly for product flows. It talks to Spring. Spring may dual-hop into Haystack for recommend-style capabilities. Haystack **pulls** fleet rows from the REST primary; it does **not** write back to the primary.

---

## 2. High-level architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Host machine (browser / IDE)                    │
│  localhost:5173  ·  localhost:8080  ·  localhost:5432/5433/5434  ·  Neo4j UI │
└───────────────┬───────────────────────────┬───────────────────┬──────────────┘
                │                           │                   │
                ▼                           ▼                   ▼
┌───────────────────────────┐  ┌────────────────────────────┐  ┌──────────────────────────────┐
│ Heavy-Rental-Web-Portal   │  │ Heavy-Rental-REST-API      │  │ Haystack-Fast-API            │
│                           │  │                            │  │                              │
│ heavy-rental-web-portal   │  │ heavy-rental-rest-api      │  │ haystack-fast-api            │
│ (React / Vite)            │  │ (Spring Boot :8080)        │  │ (Haystack / FastAPI)         │
│                           │  │         │                  │  │         │                    │
│ No local DB               │  │         ▼                  │  │         ▼                    │
│                           │  │ postgres-primary (OLTP SoT)│  │ postgres-haystack            │
│                           │  │ heavy_rental / public      │  │ + pgvector (vector)          │
│                           │  │ [optional replica]         │  │         ▲                    │
│                           │  │                            │  │         │ merge-sync pull     │
│                           │  │                            │  │ postgres-haystack-sync       │
│                           │  │                            │  │         │ post-sync HTTP      │
│                           │  │                            │  │         ▼                    │
│                           │  │                            │  │ neo4j-populate → neo4j       │
└─────────────┬─────────────┘  └─────────────┬──────────────┘  └──────────────┬───────────────┘
              │ HTTP                         │ R/W JDBC                       │
              │                              │                                │
              └──────────────► heavy-rental-rest-api ◄── optional dual-hop ───┘
                                              │
                                              │ read source only
                                              ▼
                                    postgres-primary  ◄──pull──  postgres-haystack-sync

                         ════════ heavy-rental-network (external Docker network) ════════
```

### Layered view

| Layer | Components | Responsibility |
|-------|------------|----------------|
| **Presentation** | `heavy-rental-web-portal` | SPA UI, forms, dashboards |
| **API / orchestration** | `heavy-rental-rest-api` | AuthZ/authN (app-level), CRUD, business rules; optional calls into Haystack |
| **Recommend / AI plane** | `haystack-fast-api` + Neo4j + pgvector platform | Retrieval, graph fleet view, future DocumentStore / embeddings |
| **OLTP store** | `postgres-primary` (+ optional replica) | Authoritative fleet domain rows |
| **Mirror / graph stores** | `postgres-haystack`, `neo4j-haystack` | Local sandbox for Haystack; never the product SoT |

---

## 3. Shared infrastructure

### 3.1 External Docker network

All three packs attach services to the **external** network:

```bash
docker network create heavy-rental-network
```

Effects:

- Containers resolve each other by **Compose/container DNS names** (for example `heavy-rental-rest-api`, `postgres-primary`, `postgres-haystack`).
- Stacks can start independently; peers appear when their Compose stack is up.
- No pack creates the network; operators create it once.

### 3.2 Independent Compose stacks

Each pack owns its own `docker-compose.yml` under `.devcontainer/`. There is **no** single monorepo Compose that starts all three. Typical full local topology means three Dev Containers (or three Compose projects) on the same network.

### 3.3 Devcontainer model

| Pack | Active config path | Special step |
|------|--------------------|--------------|
| Web Portal | `Heavy-Rental-Web-Portal/.devcontainer/` | None |
| Haystack | `Haystack-Fast-API/.devcontainer/` | None |
| REST API | `Heavy-Rental-REST-API/.devcontainer/` | **Promote** one of two nested packs up one level first |

---

## 4. Heavy-Rental-Web-Portal

### 4.1 Role

The portal is the **presentation tier**: a React / TypeScript workspace for UI development. It has:

- No local Postgres
- No Neo4j
- No merge-sync or fleet jobs

Backend data access is expected to go through the **REST API** peer.

### 4.2 Runtime shape

| Item | Value |
|------|--------|
| Container | `heavy-rental-web-portal` |
| Base image | `mcr.microsoft.com/devcontainers/typescript-node:4-24-trixie` |
| Workspace mount | `/workspaces/heavy-rental-web-portal` |
| Host / forward port | **5173** (typical Vite dev server) |
| Remote user | `node` |
| Network | `heavy-rental-network` |

### 4.3 Integration points

```text
Browser
  → http://localhost:5173  (forwarded from portal container)
  → React app issues HTTP to REST API base URL
       e.g. http://heavy-rental-rest-api:8080  (from inside Docker network)
       or   http://localhost:8080              (from host browser via proxy/CORS as configured)
```

**Important:** Compose for this pack does **not** define the API base URL. That is application configuration (`env`, Vite config, etc.) in the portal project sources.

### 4.4 Peer dependencies

| Need | Peer |
|------|------|
| Backend CRUD / business APIs | **Heavy-Rental-REST-API** (required for real data) |
| Recommend / AI features | Indirect via REST dual-hop to **Haystack-Fast-API** (optional) |

The portal container still starts without peers; API calls fail until Spring is healthy.

### 4.5 What this pack does *not* own

- Durable multi-user project vectors (future: Haystack pgvector after app I0/I1)
- Fleet table schema (REST producer contract)
- Neo4j graph population

---

## 5. Heavy-Rental-REST-API

### 5.1 Role

Spring Boot is the **system of record** for fleet domain data and the **only HTTP backend** the portal is designed to call for product flows.

It owns:

- Application container `heavy-rental-rest-api`
- Writable primary Postgres `postgres-primary` (database `heavy_rental`)
- Optional streaming read replica `postgres-replica-one`
- Producer side of the **D0 fleet schema contract** (`asset`, `booking`, `category`)

It does **not** own:

- Haystack merge-sync
- pgvector
- Neo4j populate

### 5.2 Dual pack distribution

Operators choose one profile and **move** its nested `.devcontainer` to `Heavy-Rental-REST-API/.devcontainer`:

| Pack | Services |
|------|----------|
| **With PostgreSQL Read Replica** | App + primary + streaming standby |
| **Without read replica** | App + primary only |

Both packs share the same app JDBC target: **always primary**.

```text
WITH REPLICA                              WITHOUT REPLICA
────────────                              ───────────────
app ──write──► db-primary (R/W)           app ──write──► db-primary (R/W)
                    │
                    │ streaming replication
                    ▼
              db-replica-one (read)
```

The replica is available on the network and in the IDE for **read** experiments. Routing application reads to the replica is **application configuration**, not enabled by the pack itself.

### 5.3 Runtime shape

| Item | Value |
|------|--------|
| App container | `heavy-rental-rest-api` |
| Base image | Java 21 + Maven (`mcr.microsoft.com/devcontainers/java:3-21-trixie`) |
| Workspace | `/workspaces/heavy-rental-rest-api` |
| App port | **8080** |
| Primary | `postgres-primary` / service `db-primary`, host **5432** |
| Replica (optional) | `postgres-replica-one`, host **5433** |
| DB name / user / password (dev) | `heavy_rental` / `postgres` / `postgres` |
| Datasource | `jdbc:postgresql://db-primary:5432/heavy_rental` |
| Network | `heavy-rental-network` |

### 5.4 Relationship to Haystack

```text
Heavy-Rental-REST-API                 Haystack-Fast-API
postgres-primary (heavy_rental)  ◄──  postgres-haystack-sync (poll ~60s)
  plain Postgres 17 SoT               postgres-haystack mirror + pgvector
```

Rules:

1. **Primary is readable** by Haystack over `heavy-rental-network`.
2. REST pack does **not** push changes to Haystack.
3. Primary stays **plain Postgres 17** — no `vector` extension requirement.
4. Default fleet tables for mirror allowlist: `asset`, `booking`, `category`.

### 5.5 Optional dual-hop to Haystack

Product design keeps the portal on Spring. For recommend / retrieval features, Spring may call Haystack internally (“dual-hop” / Call 1–2 style):

```text
Portal ──HTTP──► Spring REST ──HTTP──► Haystack Fast API
                     │                      │
                     └── R/W postgres-primary   └── R/W postgres-haystack / Neo4j
```

This keeps:

- A single public API surface for the UI
- Haystack as an **internal** capability plane, not a second browser-facing backend

Exact Spring→Haystack routes are application concerns; the packs guarantee network reachability when both stacks are up.

---

## 6. Haystack-Fast-API

### 6.1 Role

Haystack is the **intelligence and mirror plane**:

1. Local writable Postgres sandbox for the Haystack app
2. Near-real-time **pull** of fleet tables from REST primary
3. **pgvector** platform readiness for future DocumentStore cutover
4. Neo4j for graph DocumentStore (KG-1) and fleet projection (KG-2)
5. Jobs that project SQL fleet rows into Neo4j via Cypher `MERGE`

The Haystack app **always** uses local `postgres-haystack`, never `postgres-primary`, as its default relational datasource.

### 6.2 Compose services

| Service / container | Role |
|---------------------|------|
| `haystack-fast-api` | Dev workspace + app process environment |
| `postgres-haystack` | Local R/W Postgres 17 + **pgvector** (`pgvector/pgvector:pg17`) |
| `postgres-haystack-sync` | Merge-sync job: pull from `postgres-primary` |
| `neo4j` → `neo4j-haystack` | Neo4j 5 Community (Browser + Bolt) |
| `neo4j-populate` | SQL → Neo4j fleet projection + admin HTTP |

### 6.3 Runtime shape

| Item | Value |
|------|--------|
| App Postgres | `postgresql://postgres:postgres@postgres-haystack:5432/heavy_rental` |
| Local Postgres host port | **5434** → container `5432` |
| Embedding dim contract | `INDEXING_EMBEDDING_DIM=768` |
| Neo4j Browser / Bolt | **7474** / **7687** |
| Neo4j auth (dev) | `neo4j` / `heavyrental` |
| Populate admin HTTP | **8089** (`POST /v1/populate`, `GET /health`) |
| Default sync interval | **60s** poll (`SYNC_INTERVAL_SECONDS`; not CDC) |
| Default table allowlist | `asset,booking,category` |
| Network | `heavy-rental-network` |

### 6.4 Merge-sync (fleet mirror)

**Direction:** primary → Haystack only (pull).  
**Style:** scheduled poll + upsert, **not** logical replication / CDC.

```text
START
  → wait for postgres-haystack ready
  → connectivity check to postgres-primary
       ├─ unavailable + default → SKIP cycle → sleep 60s → retry
       ├─ unavailable + HALT_ON_PRIMARY_UNAVAILABLE → halt job
       └─ available → MERGE:
            FDW/staging → schema evolution (additive) → upsert by PK/UNIQUE
            → log METRICS (duration_ms, expected_max_lag_seconds, …)
            → best-effort POST neo4j-populate /v1/populate
            → sleep → loop
```

Default merge policy (sandbox-safe):

| Behavior | Default |
|----------|---------|
| Primary wins on key conflict | Yes |
| Retain local-only rows | Yes |
| Mirror primary deletes | No |
| Drop local-only columns | No (`DROP_ORPHAN_COLUMNS=false`) |
| Schema | Additive CREATE TABLE / ADD COLUMN |
| Schema scope | `public` only |
| Allowlist | `asset,booking,category` (or `all` / `*`) |

Opt-in `SYNC_MODE=mirror` and related flags can tighten parity (drops, indexes, safe type widenings). Foreign-key sync is reserved / not implemented.

### 6.5 Neo4j populate (fleet graph KG-2)

After SQL is mirrored locally, `neo4j-populate` projects allowlisted tables into Neo4j:

| SQL table | Neo4j label | MERGE key |
|-----------|-------------|-----------|
| `asset` | `:Asset` | `id` |
| `booking` | `:Booking` | `id` |
| `category` | `:Category` | `id` |

Best-effort relationships:

| Relationship | Pattern | When |
|--------------|---------|------|
| `IN_CATEGORY` | `(:Asset)-[:IN_CATEGORY]->(:Category)` | asset has category FK-like field |
| `FOR_ASSET` | `(:Booking)-[:FOR_ASSET]->(:Asset)` | booking has asset FK-like field |

**Isolation (critical):**

| Plane | Labels | Touched by populate? |
|-------|--------|----------------------|
| **KG-2 Fleet** | `Asset`, `Booking`, `Category` | Yes (MERGE / scoped delete) |
| **KG-1 DocumentStore** | `Document` (default protected) | **Never** |

Rebuild / orphan prune never run global graph wipes and never drop KG-1 labels.

Triggers:

1. **Post-sync** — after successful merge, sync best-effort `POST` to `http://neo4j-populate:8089/v1/populate`
2. **Admin HTTP** — operator/app one-shot populate
3. **Interval safety net** — default ~60s poll

Trigger failure does **not** fail or roll back the SQL merge cycle.

### 6.6 Pgvector platform (Phase 5)

Local Postgres is **vector-ready**:

- Image: `pgvector/pgvector:pg17`
- Extension: `vector` on `heavy_rental`
- Contract env: `INDEXING_EMBEDDING_DIM=768`

Application work still separate (not required for the platform pack):

- **I0** — DocumentStore factory wiring
- **I1** — indexing pipeline writer / durable multi-user project vectors

REST primary must **not** install pgvector for this design.

### 6.7 Historical note: FAISS

Spec Kit `003-haystack-faiss` is **historical only**. FAISS is not wired in the default Compose / postCreate path; pgvector is the intended durable vector platform.

---

## 7. Cross-service data flows

### 7.1 Operator CRUD (happy path)

```text
User → Web Portal → REST API → postgres-primary
                      │
                      └── response JSON → Portal UI
```

Within ~60s (default), Haystack merge-sync copies allowlisted tables into `postgres-haystack`, then may trigger Neo4j populate for KG-2 nodes.

### 7.2 Fleet mirror pipeline (end-to-end)

```text
[1] Spring writes row to postgres-primary.public.asset
[2] postgres-haystack-sync (≤ ~SYNC_INTERVAL_SECONDS)
      → upserts into postgres-haystack.public.asset
[3] On successful merge → POST neo4j-populate /v1/populate
[4] neo4j-populate MERGE (:Asset {id: ...}) with properties + optional rels
[5] haystack-fast-api can query SQL mirror and/or Neo4j for recommend tools
```

### 7.3 Recommend dual-hop (conceptual)

```text
Portal ──(1)──► REST ──(2)──► Haystack
                  │              │
                  │              ├── read postgres-haystack (fleet LTM + future vectors)
                  │              └── read neo4j-haystack (KG-1 docs + KG-2 fleet)
                  └── REST composes response for portal
```

Portal never needs Haystack credentials or Neo4j connectivity.

### 7.4 What never flows backward

| Forbidden / non-goal | Why |
|----------------------|-----|
| Haystack → write `postgres-primary` | Primary remains sole OLTP SoT |
| Populate → drop `:Document` | Protects KG-1 project knowledge |
| Portal → direct DB | Encapsulation; auth and rules stay in Spring |
| REST primary requires pgvector | Keep OLTP image plain and operationally simple |

---

## 8. Domain model (fleet D0)

**Contract version:** 1.0 (Phase 4 freeze)  
**Producer:** REST API primary  
**Consumer:** Haystack merge-sync allowlist + Neo4j populate

| Logical entity | Physical table (`public`) | Typical PK | Lag-sensitive fields | Default mirror |
|----------------|---------------------------|------------|----------------------|----------------|
| Asset | `asset` | `id` | status, category FK, pricing-related cols | Yes |
| Booking | `booking` | `id` | start/end, asset_id, status | Yes |
| Category | `category` | `id` | name / code | Yes |

Optional / not default allowlist:

| Entity | Table | Notes |
|--------|-------|--------|
| Rental plan | `rental_plan` | Add when pricing needs it |
| Payment | `payment` | Usually not needed for recommend LTM |

If Spring/JPA uses different physical names, operators must override `SYNC_TABLE_ALLOWLIST` / populate allowlists and revise the schema contract.

Producer contract:  
[`Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`](./Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md)

Consumer contract:  
[`Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`](./Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md)

---

## 9. Storage planes

```text
┌──────────────────── Postgres planes ────────────────────┐
│                                                          │
│  postgres-primary          postgres-replica-one (opt)    │
│  ────────────────          ──────────────────────        │
│  OLTP SoT                  Streaming standby             │
│  Spring R/W                Read experiments              │
│  No pgvector               No pgvector                   │
│                                                          │
│  postgres-haystack                                       │
│  ─────────────────                                       │
│  Haystack R/W sandbox                                    │
│  Fleet mirror (allowlist)                                │
│  + extension vector (platform)                           │
│  Local-only rows retained under merge mode               │
└──────────────────────────────────────────────────────────┘

┌──────────────────── Neo4j planes (one instance) ─────────┐
│  neo4j-haystack                                          │
│                                                          │
│  KG-1  :Document …     ← app DocumentStore / ingest      │
│        (protected; never dropped by populate)            │
│                                                          │
│  KG-2  :Asset :Booking :Category                         │
│        ← neo4j-populate from postgres-haystack           │
│        provenance: _source='fleet-mirror'                │
└──────────────────────────────────────────────────────────┘
```

### Why separate SQL instances?

| Goal | Design choice |
|------|----------------|
| Isolate Haystack experiments from production-like OLTP | Local `postgres-haystack` |
| Avoid vector/extension risk on Spring primary | pgvector only on Haystack DB |
| Survive primary downtime for local AI work | Skip sync; keep local DB usable |
| Near-RT fleet awareness without CDC ops cost | 60s poll merge |

---

## 10. Network, ports, and DNS

### 10.1 Host-published ports (typical)

| Port | Service | Pack |
|------|---------|------|
| **5173** | React Vite dev server | Web Portal |
| **8080** | Spring REST API | REST API |
| **5432** | Postgres primary | REST API |
| **5433** | Postgres replica | REST API (with-replica only) |
| **5434** | Postgres Haystack local | Haystack |
| **7474** | Neo4j Browser HTTP | Haystack |
| **7687** | Neo4j Bolt | Haystack |
| **8089** | neo4j-populate admin HTTP | Haystack |

### 10.2 Useful Docker DNS names

| Hostname | Reachable from | Purpose |
|----------|----------------|---------|
| `heavy-rental-web-portal` | peers on network | Portal container |
| `heavy-rental-rest-api` | portal / haystack | Spring HTTP |
| `postgres-primary` / `db-primary` | haystack sync, REST app | OLTP |
| `postgres-replica-one` / `db-replica-one` | REST stack | Standby reads |
| `postgres-haystack` | haystack app, sync, populate | Local mirror DB |
| `neo4j` | haystack app, populate | Bolt `7687` |
| `neo4j-populate` | sync trigger | Admin HTTP `8089` |

### 10.3 From host vs from container

| Client location | REST API | Haystack Postgres | Neo4j Bolt |
|-----------------|----------|-------------------|------------|
| Host browser / tools | `localhost:8080` | `localhost:5434` | `localhost:7687` |
| Another container on network | `heavy-rental-rest-api:8080` | `postgres-haystack:5432` | `neo4j:7687` |

---

## 11. Trust boundaries and write ownership

```text
                    WRITE AUTHORITY
┌──────────────────────────────────────────────────────────┐
│  postgres-primary  ←  Spring REST only (product SoT)     │
│  postgres-haystack ←  Haystack app + merge-sync upserts  │
│  neo4j-haystack    ←  Haystack app (KG-1) + populate (KG-2)│
└──────────────────────────────────────────────────────────┘

                    READ PATHS
┌──────────────────────────────────────────────────────────┐
│  Portal     → REST HTTP only                             │
│  Spring     → primary JDBC (+ optional Haystack HTTP)    │
│  Haystack   → local Postgres + Neo4j                     │
│  Sync job   → read primary, write local Postgres         │
│  Populate   → read local Postgres, write Neo4j KG-2      │
└──────────────────────────────────────────────────────────┘
```

Implications for developers:

1. Fix fleet data bugs in **Spring + primary**, not by editing the Haystack mirror as if it were SoT.
2. Local-only rows on `postgres-haystack` are intentional sandbox features under merge mode.
3. Graph fleet nodes can lag SQL by roughly the poll interval (plus populate latency).
4. Do not point the portal at Haystack for authoritative booking mutations.

---

## 12. Failure modes and resilience

| Scenario | Expected behavior |
|----------|-------------------|
| REST stack down | Portal API calls fail; Haystack local DB still works; sync **skips** cycles (default) |
| Haystack stack down | Portal + REST CRUD still work; recommend dual-hop fails |
| Portal stack down | APIs and DBs unaffected |
| Primary unreachable during sync | Skip (default) or halt if `HALT_ON_PRIMARY_UNAVAILABLE=true`; no local wipe |
| Neo4j populate trigger fails | Merge still succeeds; populate retries on interval / next success |
| Missing allowlisted table / `id` column | Populate skips that table; job continues |
| Replica lag / down (with-replica pack) | Primary + app unaffected; replica IDE reads may fail |

Default sync uses `restart: unless-stopped` so the long-running loop survives engine restarts without halt+restart storms.

---

## 13. Local development topology

### 13.1 Recommended bring-up order

1. Create network: `docker network create heavy-rental-network`
2. Start **Heavy-Rental-REST-API** (promote pack, open Dev Container) — primary healthy
3. Start **Haystack-Fast-API** — sync can pull; populate can run
4. Start **Heavy-Rental-Web-Portal** — point app at REST base URL

Minimum for UI + CRUD only: steps 1, 2, 4.  
Minimum for mirror/graph work: steps 1–3.

### 13.2 Workspace layout (this configuration repo)

```text
heavy-rental-devcontainer-configuration/
├── ARCHITECTURE.md                 ← this document
├── README.md                       ← setup guides / videos
├── docs/spec-governance.md         ← OpenSpec + OpenSPDD + ADR workflow
├── adr/                            ← durable architecture decisions
├── openspec/                       ← platform OpenSpec (spec-driven-with-adr)
├── spdd/                           ← OpenSPDD REASONS canvases
├── Heavy-Rental-Web-Portal/
│   ├── .devcontainer/
│   ├── openspec/ · specs/
│   └── README.md
├── Heavy-Rental-REST-API/
│   ├── Spring Boot REST API devcontainer with PostgreSQL Read Replica/
│   ├── Spring Boot REST API devcontainer without read replica/
│   ├── openspec/ · specs/
│   └── README.md
└── Haystack-Fast-API/
    ├── .devcontainer/              # compose, sync scripts, neo4j populate
    ├── openspec/ · specs/
    └── README.md
```

### 13.3 Spec / OpenSpec / OpenSPDD / ADR ownership

| Area | Spec Kit | OpenSpec SoT | OpenSPDD canvas | ADRs |
|------|----------|--------------|-----------------|------|
| Platform (all packs) | — | `openspec/specs/platform-devcontainers/` | `spdd/prompt/platform-devcontainers.md` | 0001–0010 |
| Documentation model | — | `openspec/specs/documentation-governance/` | `docs/spec-governance.md` | 0010 |
| REST packs | `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/` | `rest-api-devcontainer` | `spdd/prompt/rest-api-devcontainer.md` | 0002, 0005, 0007, 0009 |
| Haystack merge-sync | `Haystack-Fast-API/specs/001-…` | `haystack-devcontainer` | `spdd/prompt/haystack-devcontainer.md` | 0003, 0004, 0009 |
| Haystack Neo4j service | `002-haystack-neo4j` | same | same | 0008 |
| Haystack pgvector | `004-haystack-pgvector` | same | same | 0007 |
| Neo4j fleet populate | `005-haystack-neo4j-populate` | same | same | 0008, 0009 |
| Web Portal | `Heavy-Rental-Web-Portal/specs/001-web-portal-devcontainer/` | `web-portal-devcontainer` | `spdd/prompt/web-portal-devcontainer.md` | 0006 |

OpenSpec schema is **`spec-driven-with-adr`**. Durable ADRs always live at repo-root [`adr/`](./adr/), not inside archived change folders. Change order: proposal → specs → design → adr → tasks. See [`docs/spec-governance.md`](./docs/spec-governance.md).

---

## 14. Credentials (local dev only)

| Resource | User | Password | Notes |
|----------|------|----------|-------|
| Postgres primary / replica / haystack | `postgres` | `postgres` | DB `heavy_rental` |
| Replication role (with-replica) | `replicator` | `replicatorpass` | Standby bootstrap only |
| Neo4j | `neo4j` | `heavyrental` | Browser + Bolt |

**Do not use these credentials outside local development.**

---

## 15. Phase roadmap (as reflected in packs)

| Phase / theme | What landed in configuration packs |
|---------------|-------------------------------------|
| Shared network + multi-pack Dev Containers | All three packs on `heavy-rental-network` |
| REST dual packs (with/without replica) | Operator-selectable primary ± standby |
| Phase 4 fleet mirror | Allowlist, D0 schema contract, lag metrics, pull sync |
| Phase 5 pgvector platform | `postgres-haystack` image + `vector` extension + dim env |
| Phase 8 Neo4j populate | SQL→Cypher MERGE, KG-1 isolation, post-sync + admin HTTP |
| Future app work (not pack-complete) | Haystack DocumentStore I0/I1; richer Spring dual-hop recommend; portal API config |

FAISS was explored and **removed** from the default stack in favor of pgvector.

---

## 16. Spec governance (OpenSpec, OpenSPDD, ADR)

Three in-repo layers keep pack behavior and architecture memory in git:

| Layer | Tool | Question | Location |
|-------|------|----------|----------|
| **What** | OpenSpec (`spec-driven-with-adr`) | Current agreed behavior | `openspec/specs/` (repo + each pack) |
| **How / not-how** | OpenSPDD REASONS Canvas | Implementation contract and safeguards | `spdd/prompt/` |
| **Why** | ADR (MADR-short) | Durable architectural choice | `adr/` |

GitHub Spec Kit packages under `specs/00N-…/` are feature workbooks (stories, contracts, verification) and MUST stay aligned with the matching OpenSpec SoT.

Default OpenSpec archives `design.md` with the change. This repo keeps **ADRs outside the change** so rationale is visible to the next proposal. Accepted ADRs are immutable; a new decision adds a new file that **supersedes** the old one.

### In-force ADRs (summary)

| ADR | Decision |
|-----|----------|
| [0001](./adr/0001-three-packs-shared-external-network.md) | Three independent Compose packs; external `heavy-rental-network` |
| [0002](./adr/0002-rest-primary-oltp-source-of-truth.md) | REST `postgres-primary` is the only product OLTP writer |
| [0003](./adr/0003-haystack-writable-local-postgres-pull-merge.md) | Haystack writable local Postgres + pull merge |
| [0004](./adr/0004-near-real-time-poll-not-cdc.md) | Near-RT poll (60s), not CDC; skip when primary down |
| [0005](./adr/0005-rest-dual-packs-promote-devcontainer.md) | Dual REST packs; promote `.devcontainer` |
| [0006](./adr/0006-portal-calls-spring-only.md) | Portal calls Spring only |
| [0007](./adr/0007-pgvector-on-haystack-not-primary.md) | pgvector on Haystack; FAISS not default |
| [0008](./adr/0008-neo4j-kg1-kg2-isolation.md) | One Neo4j; populate never drops KG-1 |
| [0009](./adr/0009-d0-fleet-schema-contract-allowlist.md) | D0 default allowlist `asset,booking,category` |
| [0010](./adr/0010-openspec-openspdd-adr-documentation-model.md) | This documentation model |

Full process: [`docs/spec-governance.md`](./docs/spec-governance.md).

---

## 17. Where to read more

### Operator READMEs

- [Heavy-Rental-Web-Portal/README.md](./Heavy-Rental-Web-Portal/README.md)
- [Heavy-Rental-REST-API/README.md](./Heavy-Rental-REST-API/README.md)
- [Haystack-Fast-API/README.md](./Haystack-Fast-API/README.md)
- [Root setup guides & videos](./README.md)

### Spec Kit entry points

- REST: [specs/001-rest-api-devcontainer](./Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/)
- Web Portal: [specs/001-web-portal-devcontainer](./Heavy-Rental-Web-Portal/specs/001-web-portal-devcontainer/)
- Merge-sync: [specs/001-haystack-postgres-merge-sync](./Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/)
- Neo4j service: [specs/002-haystack-neo4j](./Haystack-Fast-API/specs/002-haystack-neo4j/)
- Pgvector: [specs/004-haystack-pgvector](./Haystack-Fast-API/specs/004-haystack-pgvector/)
- Neo4j populate: [specs/005-haystack-neo4j-populate](./Haystack-Fast-API/specs/005-haystack-neo4j-populate/)

### OpenSpec sources of truth

- [openspec/specs/platform-devcontainers/spec.md](./openspec/specs/platform-devcontainers/spec.md)
- [openspec/specs/documentation-governance/spec.md](./openspec/specs/documentation-governance/spec.md)
- [Haystack-Fast-API/openspec/specs/haystack-devcontainer/spec.md](./Haystack-Fast-API/openspec/specs/haystack-devcontainer/spec.md)
- [Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md](./Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md)
- [Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md](./Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md)

### ADR and OpenSPDD

- [adr/README.md](./adr/README.md)
- [spdd/README.md](./spdd/README.md)
- [docs/spec-governance.md](./docs/spec-governance.md)

---

## Summary

| Question | Answer |
|----------|--------|
| Who owns the UI? | **Heavy-Rental-Web-Portal** (React) |
| Who owns authoritative fleet data? | **Heavy-Rental-REST-API** + `postgres-primary` |
| Who mirrors fleet data for AI/recommend? | **Haystack-Fast-API** merge-sync → `postgres-haystack` |
| Who builds the fleet graph? | **neo4j-populate** (KG-2), isolated from DocumentStore (KG-1) |
| Who does the portal call? | **Spring REST only** (Haystack is behind Spring if used) |
| How do stacks see each other? | External Docker network **`heavy-rental-network`** |
| Is sync real-time CDC? | No — near-RT **poll** (default 60s) |
| Does Haystack write the primary? | **No** — pull-only mirror |

This architecture keeps a clear OLTP boundary, gives Haystack a safe sandbox with graph and vector platforms, and lets the three packs develop independently while composing into one local platform on a shared network.
