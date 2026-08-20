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

### Stripe CLI

The app image includes `stripe`. Spring Boot Dashboard **Run** does not start `stripe listen`. After `stripe login` (or `STRIPE_API_KEY`), container start runs:

```bash
stripe listen --forward-to http://localhost:8080/api/payments/webhook
```

Manual: `/usr/local/bin/start-stripe-listen.sh` inside `heavy-rental-rest-api`.

### Phase 4 — Haystack fleet mirror (peer)

- Primary container **`postgres-primary`** on **`heavy-rental-network`** is the source Haystack pulls from.
- Domain tables: [contracts/schema-contract.md](./contracts/schema-contract.md) (default allowlist: `asset`, `booking`, `category`).
- Merge-sync runs in **Haystack-Fast-API** (`postgres-haystack-sync`), not in this pack.

### Phase 5 peer — Haystack pgvector

- Haystack local DB may use **pgvector** (`004-haystack-pgvector`); primary here stays plain Postgres.
- No action required on this pack for T5/D4.
