# ADR-0001: Three independent Compose packs on a shared external network

- Status: accepted
- Date: 2026-08-20
- Tags: platform, networking, compose

## Context

The Heavy Rental local platform has three workspaces (React portal, Spring REST API, Haystack Fast API). Developers need to start them independently, keep application sources in separate volumes, and still resolve peer containers by DNS. A single monorepo Compose file would couple lifecycle, images, and IDE reopen-in-container flows.

## Decision

Ship **three independent Dev Container / Compose packs**. Do **not** provide a root Compose that starts all services. Operators create one external Docker network once:

```bash
docker network create heavy-rental-network
```

Every pack attaches its services to that network as `external: true`. Packs MUST NOT create the network.

## Consequences

- Stacks start in any order; peers appear when their Compose project is up.
- DNS names (`postgres-primary`, `heavy-rental-rest-api`, `postgres-haystack`, …) are the integration contract.
- Missing network is an operator error, not a pack bug.
- There is no single `docker compose up` for the whole platform.

## Related

- OpenSpec: `openspec/specs/platform-devcontainers/spec.md`
- Architecture: `ARCHITECTURE.md` §3
