# Heavy Rental Web Portal — Devcontainer pack

This folder ships a **single Compose-based devcontainer** for the **Heavy Rental Web Portal** (React / TypeScript). The active configuration lives at **`Heavy-Rental-Web-Portal/.devcontainer/`** (no pack promote step—unlike the REST API dual packs).

| Service | Container | Role |
|---------|-----------|------|
| App | `heavy-rental-web-portal` | Dev workspace for the React web portal |

There is **no** local Postgres or Neo4j in this pack. Backend APIs and databases live in peer stacks (REST API, optionally Haystack) on the shared Docker network.

**Specs (OpenSpec / Spec Kit):** [`openspec/`](./openspec/) · [`specs/001-web-portal-devcontainer/`](./specs/001-web-portal-devcontainer/)  
**ADR / OpenSPDD:** [`../adr/0006-portal-calls-spring-only.md`](../adr/0006-portal-calls-spring-only.md) · [`../spdd/prompt/web-portal-devcontainer.md`](../spdd/prompt/web-portal-devcontainer.md) · [`../docs/spec-governance.md`](../docs/spec-governance.md)

Monorepo setup guide: [`../README.md`](../README.md) → *Setup Guide for the React (Heavy Rental Web Portal) Project*.

---

## Stack overview

One service: the portal app container on **`heavy-rental-network`**. The app workspace is mounted at `/workspaces/heavy-rental-web-portal`.

| | **Web Portal default stack** |
|---|------------------------------|
| Compose services | `heavy-rental-web-portal` only |
| App container | `heavy-rental-web-portal` |
| Base image | `mcr.microsoft.com/devcontainers/typescript-node:4-24-trixie` |
| Workspace | `/workspaces/heavy-rental-web-portal` |
| Host / forward port | **5173** (typical Vite/React dev server) |
| Local database | **None** (use peer REST API for data) |
| Network | External **`heavy-rental-network`** |
| Remote user | `node` |
| postCreate | Ownership fix for the workspace (`chown` for `node`) |
| Best for | UI development, component work, calling peer REST APIs over the shared network |
| Peer dependency | **Heavy-Rental-REST-API** for backend HTTP; Haystack is not required for the portal container itself |

### Architecture sketch

```text
Browser (host)
    │  localhost:5173 (forwarded)
    ▼
heavy-rental-web-portal (React / Vite workspace)
    │  HTTP on heavy-rental-network
    ▼
Heavy-Rental-REST-API (peer pack)
    heavy-rental-rest-api :8080
    postgres-primary (OLTP)
         │
         │  optional dual-hop / recommend
         ▼
    Haystack-Fast-API (peer pack)
         (internal recommend APIs)
```

**Note:** This pack does **not** start the REST API or Haystack stacks. Create the shared network once, open each project’s folder in Dev Containers as needed, and point the portal app at the REST base URL your project expects (app configuration, not defined in this Compose file).

**Included in this pack**

- TypeScript/Node 24-family base image (`typescript-node:4-24-trixie`)
- External Docker network: **`heavy-rental-network`**
- Forwarded app port **5173**
- Non-root user **`node`**; `postCreateCommand` fixes workspace ownership
- React-oriented VS Code extensions (snippets, ESLint, Prettier, Jest, browser devtools, etc.)

---

## Prerequisites

1. [Docker](https://docs.docker.com/get-docker/) and [VS Code](https://code.visualstudio.com/) with the **Dev Containers** extension (`ms-vscode-remote.remote-containers`).
2. Create the shared network once (if it does not exist):

```bash
docker network create heavy-rental-network
```

3. Your React portal project sources should live in the workspace the container mounts as `/workspaces/heavy-rental-web-portal` (volume-backed in Compose).
4. **For API integration:** start the **Heavy Rental REST API** pack so container **`heavy-rental-rest-api`** (and primary DB) are healthy on the same network. Without it, the portal container still starts; backend calls will fail until the API is up.

Peer guides:

- REST API: [`../Heavy-Rental-REST-API/README.md`](../Heavy-Rental-REST-API/README.md)
- Haystack (optional recommend plane): [`../Haystack-Fast-API/README.md`](../Haystack-Fast-API/README.md)

---

## Open in VS Code Dev Containers

VS Code Dev Containers looks for **`.devcontainer`** at the **root of the folder you open**. This pack already has configuration at `Heavy-Rental-Web-Portal/.devcontainer/`—there is **no** “move pack up one level” step.

### 1. Go to this directory

```bash
cd /path/to/heavy-rental-devcontainer-configuration/Heavy-Rental-Web-Portal
```

### 2. Confirm layout

```text
Heavy-Rental-Web-Portal/
  .devcontainer/          ← active (docker-compose.yml, devcontainer.json, Dockerfile)
  README.md
```

### 3. Open the folder in VS Code Dev Containers

1. Open **VS Code**.
2. **File → Open Folder…** and select **`Heavy-Rental-Web-Portal`** (the folder that contains `.devcontainer`).
3. When prompted, use **Dev Containers: Reopen in Container**, or the Command Palette:
   - `Dev Containers: Reopen in Container`
4. Wait for the image build and Compose service (`heavy-rental-web-portal`).

Alternatively, from the command palette: **Dev Containers: Open Folder in Container…** and select `Heavy-Rental-Web-Portal`.

### Optional: Compose only (without full Dev Containers UX)

```bash
cd Heavy-Rental-Web-Portal/.devcontainer
docker compose up -d
```

---

## Quick verification

```bash
# App container running
docker ps --format 'table {{.Names}}\t{{.Status}}' \
  | grep -E 'heavy-rental-web-portal|NAMES'

# On shared network
docker inspect heavy-rental-web-portal \
  --format '{{json .NetworkSettings.Networks}}' | grep -q heavy-rental-network \
  && echo network-ok

# Inside app container (after Dev Containers open)
docker exec heavy-rental-web-portal node --version
docker exec heavy-rental-web-portal bash -lc 'ls -la /workspaces/heavy-rental-web-portal | head'
```

### Run the portal (inside the container / integrated terminal)

Commands depend on your app (`package.json`). Typical Vite flow:

```bash
cd /workspaces/heavy-rental-web-portal
# npm install   # or pnpm / yarn, as your project uses
# npm run dev   # expect dev server on port 5173 (forwarded to host)
```

Then open **http://localhost:5173** on the host (port is listed in `forwardPorts`).

If the REST API is also running on the shared network, the portal can reach it by Docker DNS (e.g. hostname `heavy-rental-rest-api` on port **8080**—confirm against your app’s API base URL config).

---

## Peer stacks (REST API / Haystack)

| Concern | Owner |
|---------|--------|
| React UI workspace + port 5173 | **This pack** |
| Spring REST API + primary Postgres | [`../Heavy-Rental-REST-API/`](../Heavy-Rental-REST-API/) |
| Haystack recommend / index (behind Spring) | [`../Haystack-Fast-API/`](../Haystack-Fast-API/) |
| Haystack pgvector platform (Phase 5 T5/D4) | **Haystack-Fast-API** (`postgres-haystack` + extension `vector`; app I0/I1 later) |
| Shared network | **`heavy-rental-network`** (all packs) |

```text
Heavy-Rental-Web-Portal     Heavy-Rental-REST-API        Haystack-Fast-API
heavy-rental-web-portal ──► heavy-rental-rest-api  ──►  (optional dual-hop Call 1/2)
                            postgres-primary              postgres-haystack
                            (OLTP SoT)                    + pgvector platform
```

This pack does **not** run a database or merge-sync job. Portal UX still talks to **Spring** only; durable multi-user project vectors (future) live on Haystack’s pgvector-ready Postgres after application I1 — not in this Compose file.

**Specs (OpenSpec / Spec Kit):** [`openspec/`](./openspec/) · [`specs/001-web-portal-devcontainer/`](./specs/001-web-portal-devcontainer/). Peer platform docs: [`../Haystack-Fast-API/specs/004-haystack-pgvector/`](../Haystack-Fast-API/specs/004-haystack-pgvector/).

---

## Dev tools & extensions

Installed via `devcontainer.json` for React/TypeScript work (non-exhaustive):

| Extension | Purpose |
|-----------|---------|
| ES7+ React/Redux/React-Native snippets | React snippets |
| Simple React Snippets | React snippets |
| ESLint / Prettier / Stylelint | Lint & format |
| React Refactor / Auto Rename Tag | Edit productivity |
| Path / npm IntelliSense | Imports |
| Error Lens | Inline diagnostics |
| Jest | Tests |
| Firefox / Edge DevTools | Browser debugging |
| Import Cost | Bundle size hints |
| Mock Server | Local mock APIs |

---

## Credentials (local dev only)

This pack does **not** define database or Neo4j credentials.

| Item | Value |
|------|--------|
| Container user | `node` |
| Dev server port (forward) | **5173** |
| Peer REST API (typical) | host **8080** when REST pack is running |
| Peer Postgres / Neo4j | See REST API and Haystack pack READMEs |

API authentication and environment variables are owned by the **portal application** sources, not by this Compose file.

---

## Related

| Resource | Path |
|----------|------|
| Monorepo React setup guide | [`../README.md`](../README.md) (*Setup Guide for the React (Heavy Rental Web Portal) Project*) |
| End-to-end setup video (monorepo) | See parent README / `videos/End to End Project Setup Video for Heavy Rental Web Portal.mp4` |
| REST API operator README | [`../Heavy-Rental-REST-API/README.md`](../Heavy-Rental-REST-API/README.md) |
| Haystack operator README | [`../Haystack-Fast-API/README.md`](../Haystack-Fast-API/README.md) |
