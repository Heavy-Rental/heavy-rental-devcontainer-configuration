# Quickstart: Web Portal Devcontainer

Full operator guide: [`../../README.md`](../../README.md)

```bash
docker network create heavy-rental-network   # once

# Open Heavy-Rental-Web-Portal in VS Code → Dev Containers: Reopen in Container
# No promote / move-.devcontainer step.
```

Expect container `heavy-rental-web-portal`. Host UI port **5173**.

Peer REST (for real data): [`../../../Heavy-Rental-REST-API/README.md`](../../../Heavy-Rental-REST-API/README.md) — app **8080**, primary **5432**.
