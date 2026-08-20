# Running Verification: Web Portal Devcontainer

## Prerequisites

- `docker network create heavy-rental-network` (once)
- Folder `Heavy-Rental-Web-Portal` opened in Dev Containers (or Compose from `.devcontainer`)

## 0. Layout (SC-001 / FR-007)

```bash
test -f Heavy-Rental-Web-Portal/.devcontainer/devcontainer.json
test -f Heavy-Rental-Web-Portal/.devcontainer/docker-compose.yml
```

## 1. Container (SC-002)

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' \
  | grep -E 'heavy-rental-web-portal|NAMES'
```

Expect `heavy-rental-web-portal`.

## 2. No pack-local database (SC-003)

```bash
# This Compose project should not require postgres-primary / neo4j in *this* project.
docker compose -f Heavy-Rental-Web-Portal/.devcontainer/docker-compose.yml config --services
# Expect: heavy-rental-web-portal (only)
```

## 3. Network

Container inspect should list network `heavy-rental-network`.

## 4. Specs present (SC-005)

```bash
test -f Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md
```
