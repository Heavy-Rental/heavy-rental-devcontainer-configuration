# Implementation Plan: REST API Devcontainer Packs

**Feature**: `001-rest-api-devcontainer` | **Status**: Specified (as-built)

## Summary

Document two as-built Spring Boot devcontainer packs and the operator workflow that promotes one pack’s `.devcontainer` to `Heavy-Rental-REST-API/.devcontainer`. No application code changes.

**Phase 4 (S4 peer):** primary remains fleet **source of truth** for Haystack merge-sync (T0). D0 producer [schema-contract.md](./contracts/schema-contract.md) freezes default tables (`asset`, `booking`, `category`). Sync job is **not** implemented here (Haystack-Fast-API owns T1/T2).

## Technical Context

| Item | Value |
|------|--------|
| Base image | `mcr.microsoft.com/devcontainers/java:3-21-trixie` (+ Maven) |
| App service | `heavy-rental-rest-api` |
| Workspace | `/workspaces/heavy-rental-rest-api` |
| Network | External `heavy-rental-network` |
| Primary | `postgres:17`, container `postgres-primary`, host **5432** |
| Replica (optional pack) | `postgres:17`, container `postgres-replica-one`, host **5433**, streaming |

## Structure

```text
Heavy-Rental-REST-API/
  README.md
  openspec/...
  specs/001-rest-api-devcontainer/...
  Spring Boot REST API devcontainer with PostgreSQL Read Replica/.devcontainer/
  Spring Boot REST API devcontainer without read replica/.devcontainer/
  .devcontainer/   # AFTER operator promote only
```

## Testing

See [verification.md](./verification.md).
