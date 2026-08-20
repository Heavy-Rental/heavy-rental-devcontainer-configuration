# Data Model: Web Portal Devcontainer

This pack has **no** durable domain tables. Runtime entities are Compose/devcontainer objects.

## Services

### App

| Attribute | Value |
|-----------|--------|
| Compose service | `heavy-rental-web-portal` |
| Container | `heavy-rental-web-portal` |
| Image | `mcr.microsoft.com/devcontainers/typescript-node:4-24-trixie` (or pack-equivalent build) |
| Workspace | `/workspaces/heavy-rental-web-portal` |
| Network | `heavy-rental-network` (external) |
| Host port | **5173** |
| Remote user | `node` |

## Peer (not in this Compose file)

| Attribute | Value |
|-----------|--------|
| REST app | `heavy-rental-rest-api:8080` |
| REST primary | `postgres-primary` (owned by REST pack) |
| Haystack | Optional dual-hop via REST |

## Domain data

None in this pack. Fleet schema: REST producer contract `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/contracts/schema-contract.md`.
