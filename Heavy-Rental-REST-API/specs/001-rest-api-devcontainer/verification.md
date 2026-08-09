# Running Verification: REST API Devcontainer

## Prerequisites

- Chosen pack promoted to `Heavy-Rental-REST-API/.devcontainer`
- `docker network create heavy-rental-network` (once)
- Stack started via Dev Containers or Compose from the active `.devcontainer`

## 0. Promote layout (SC-001)

```bash
test -f Heavy-Rental-REST-API/.devcontainer/devcontainer.json
test -f Heavy-Rental-REST-API/.devcontainer/docker-compose.yml
```

## 1. Containers (SC-002 / SC-003)

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' \
  | grep -E 'heavy-rental-rest-api|postgres-primary|postgres-replica-one|NAMES'
```

**Without replica:** app + `postgres-primary`  
**With replica:** app + `postgres-primary` + `postgres-replica-one`

## 2. Primary writable (SC-002)

```bash
docker exec postgres-primary \
  psql -U postgres -d heavy_rental -c "SELECT pg_is_in_recovery();"
# Expect: f (false) — primary is not a standby
```

## 3. Replica recovery (with-replica only) (SC-003)

```bash
docker exec postgres-replica-one \
  psql -U postgres -d heavy_rental -c "SELECT pg_is_in_recovery();"
# Expect: t (true)
```

## 4. App datasource (SC-004)

```bash
docker exec heavy-rental-rest-api printenv SPRING_DATASOURCE_URL
# Expect: jdbc:postgresql://db-primary:5432/heavy_rental
```

## 5. Pack identity

```bash
# With-replica pack includes replica service:
grep -q 'db-replica-one' Heavy-Rental-REST-API/.devcontainer/docker-compose.yml && echo with-replica || echo without-or-unknown

# With-replica IDE profile:
grep -q 'db-replica-one' Heavy-Rental-REST-API/.devcontainer/devcontainer.json && echo replica-profile-present || echo primary-only-profiles
```

## Pass checklist

| ID | Check | Result |
|----|--------|--------|
| SC-001 | Active `.devcontainer` after promote | ☐ |
| SC-002 | Primary healthy / not in recovery | ☐ |
| SC-003 | Replica in recovery (with pack) | ☐ / N/A |
| SC-004 | `SPRING_DATASOURCE_URL` → primary | ☐ |
| SC-005 | Names match data-model | ☐ |

## Troubleshooting

| Symptom | Action |
|---------|--------|
| Network not found | `docker network create heavy-rental-network` |
| Replica never healthy | Check primary logs; wipe replica volume and restart; confirm `replicator` role |
| Wrong pack active | Replace `Heavy-Rental-REST-API/.devcontainer` from the other pack (git restore if needed) |
| Port 5432/5433 busy | Stop conflicting local Postgres or remap host ports |
