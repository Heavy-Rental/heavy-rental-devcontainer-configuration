# ADR-0006: Web portal calls Spring REST only

- Status: accepted
- Date: 2026-08-20
- Tags: portal, api, trust-boundary

## Context

The React portal needs CRUD and, later, recommend-style features. Exposing Haystack (or databases) to the browser would duplicate auth, leak graph/vector credentials, and split the public API.

## Decision

The Web Portal pack is **presentation only**: no local Postgres, no Neo4j, no merge-sync. Product HTTP from the portal goes to **Heavy-Rental-REST-API** (`heavy-rental-rest-api:8080` on the Docker network, or `localhost:8080` from the host). Recommend / retrieval MAY be a **dual-hop** Spring → Haystack call. The portal MUST NOT be configured as a second browser-facing backend for Haystack or as a direct DB client.

API base URL and auth remain **application** configuration in the portal workspace, not Compose defaults in this pack.

## Consequences

- One public API surface for the UI.
- Portal container still starts without peers; API calls fail until Spring is healthy.
- Haystack credentials stay off the browser.

## Related

- OpenSpec: `Heavy-Rental-Web-Portal/openspec/specs/web-portal-devcontainer/spec.md`
- Architecture: `ARCHITECTURE.md` §4, §7.3
