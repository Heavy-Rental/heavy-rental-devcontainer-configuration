# Web Portal Devcontainer Specification

## Purpose

Behavior of the **Heavy Rental Web Portal** development container pack under `Heavy-Rental-Web-Portal/`. This is the OpenSpec **source of truth** for agreed as-built behavior.

The pack ships a **single** Compose-based Dev Container (React / TypeScript). Configuration lives at `Heavy-Rental-Web-Portal/.devcontainer/` — operators do **not** promote a nested pack (unlike REST API).

Change history:

- `openspec/changes/archive/2026-08-20-add-web-portal-devcontainer/`

Spec Kit: `specs/001-web-portal-devcontainer/`.

In-force ADRs: 0001 (network), 0006 (portal HTTP), 0010 (docs).

## Requirements

### Requirement: Single Compose app service

The Web Portal development environment MUST start via Docker Compose using `Heavy-Rental-Web-Portal/.devcontainer/docker-compose.yml`, attach to the external network `heavy-rental-network`, and define application service `heavy-rental-web-portal` only (no pack-local Postgres or Neo4j).

#### Scenario: Stack services

- **GIVEN** this configuration is deployed
- **WHEN** a developer inspects Compose services
- **THEN** `heavy-rental-web-portal` is defined
- **AND** it joins `heavy-rental-network`
- **AND** a healthy local database service is not required

### Requirement: Workspace and runtime shape

The app service MUST use a TypeScript/Node Dev Container base image, mount the workspace at `/workspaces/heavy-rental-web-portal`, run as non-root user `node`, forward typical Vite port **5173**, and run a `postCreateCommand` that fixes workspace ownership for `node`.

#### Scenario: Remote user and port

- **GIVEN** the portal devcontainer is running
- **WHEN** runtime is inspected
- **THEN** `remoteUser` is `node` and host port **5173** is forwarded (or equivalently published for the Vite dev server)

### Requirement: No pack-local data plane

This pack MUST NOT define Postgres, Neo4j, merge-sync, or neo4j-populate services. Backend data access for product flows MUST go through the peer **Heavy-Rental-REST-API**.

#### Scenario: No local database in pack

- **GIVEN** only the Web Portal Compose stack is started
- **WHEN** services are listed
- **THEN** `postgres-primary`, `postgres-haystack`, and `neo4j` are not required in this pack

### Requirement: Product HTTP to REST only

The portal MUST treat `heavy-rental-rest-api` as the product HTTP backend. Recommend-style features MAY be reached only as a Spring dual-hop into Haystack. The pack MUST NOT require Haystack, Postgres, or Neo4j credentials in Compose.

#### Scenario: Portal starts without Haystack

- **GIVEN** `heavy-rental-network` exists and the portal stack starts
- **WHEN** Haystack is not running
- **THEN** the portal container still starts
- **AND** product API calls still depend on REST being healthy

### Requirement: No promote step

Unlike the REST API dual packs, operators MUST open `Heavy-Rental-Web-Portal/` directly; `.devcontainer` MUST already sit at that folder root.

#### Scenario: Active config at pack root

- **GIVEN** a checkout of this repository
- **WHEN** an operator lists `Heavy-Rental-Web-Portal/`
- **THEN** `.devcontainer/devcontainer.json` and Compose are present without a move-up step
