# Proposal: REST API devcontainer dual packs

## Intent

Document and govern two Spring Boot REST API devcontainer packs (with and without PostgreSQL streaming read replica) using OpenSpec + Spec Kit, and require operators to promote the chosen pack’s `.devcontainer` one level under `Heavy-Rental-REST-API/`.

## Scope

In scope:

- OpenSpec SoT for both profiles
- Spec Kit `001-rest-api-devcontainer`
- Operator README (difference table + move up + Dev Containers open)

Out of scope:

- Changing as-built Compose/Dockerfile of either pack
- Spring multi-datasource implementation
- Automatic install of both packs simultaneously

## Approach

Treat pack folders as distribution units; active config is always `Heavy-Rental-REST-API/.devcontainer` after a one-level promote.
