# Contract: Compose / app environment — Web Portal

## App service (`heavy-rental-web-portal`)

This pack does **not** define database or Neo4j environment variables. API base URL and auth are owned by portal **application** sources.

| Item | Value |
|------|--------|
| Remote user | `node` |
| Workspace | `/workspaces/heavy-rental-web-portal` |
| Typical dev server | Vite on **5173** |

## Host ports

| Port | Target | Pack |
|------|--------|------|
| `5173` | React / Vite dev server | this pack |
| `8080` | Peer REST API | REST pack (not published here) |

## Network

| Name | Type |
|------|------|
| `heavy-rental-network` | External bridge (must pre-exist) |

## Credentials

None defined by this pack. Peer Postgres / Neo4j credentials: REST and Haystack operator READMEs (local-dev only).
