# Quickstart: REST API Devcontainer

Full operator guide: [`../../README.md`](../../README.md)

```bash
docker network create heavy-rental-network   # once

cd Heavy-Rental-REST-API

# Pick ONE:
mv "Spring Boot REST API devcontainer with PostgreSQL Read Replica/.devcontainer" ./.devcontainer
# mv "Spring Boot REST API devcontainer without read replica/.devcontainer" ./.devcontainer
```

Then in VS Code: open **`Heavy-Rental-REST-API`** → **Dev Containers: Reopen in Container**.

| Pack | Containers to expect |
|------|----------------------|
| With replica | `heavy-rental-rest-api`, `postgres-primary`, `postgres-replica-one` |
| Without | `heavy-rental-rest-api`, `postgres-primary` |

Primary: `localhost:5432` · Replica (if chosen): `localhost:5433` · App: port `8080`.
