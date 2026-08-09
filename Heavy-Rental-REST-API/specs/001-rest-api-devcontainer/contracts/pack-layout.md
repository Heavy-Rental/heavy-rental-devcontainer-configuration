# Contract: Pack layout and promote rule

## Distribution layout (repository)

```text
Heavy-Rental-REST-API/
  README.md
  Spring Boot REST API devcontainer with PostgreSQL Read Replica/
    .devcontainer/          # pack contents (not active until promoted)
  Spring Boot REST API devcontainer without read replica/
    .devcontainer/          # pack contents (not active until promoted)
```

## Active layout (after operator promote)

```text
Heavy-Rental-REST-API/
  .devcontainer/            # MUST be the chosen pack’s .devcontainer
    devcontainer.json
    docker-compose.yml
    Dockerfile
    postgres/…              # with-replica pack only
  README.md
```

## Promote rule

1. Working directory MUST be `Heavy-Rental-REST-API/`.
2. Operator MUST ensure no conflicting active `.devcontainer` (remove or rename).
3. Operator MUST move **exactly one** pack’s `.devcontainer` directory to `Heavy-Rental-REST-API/.devcontainer` (one level up from the pack folder).
4. Operator MUST open **`Heavy-Rental-REST-API`** (the directory containing the active `.devcontainer`) in VS Code Dev Containers.

## Commands (normative examples)

```bash
cd Heavy-Rental-REST-API
# with replica:
mv "Spring Boot REST API devcontainer with PostgreSQL Read Replica/.devcontainer" ./.devcontainer
# OR without:
# mv "Spring Boot REST API devcontainer without read replica/.devcontainer" ./.devcontainer
```

## Non-goals

- Running Dev Containers against the nested pack folder without promoting is unsupported for this project’s documented workflow.
- Installing both packs as simultaneous active configs is not supported (single `.devcontainer` only).
