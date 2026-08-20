# Design: Stripe CLI in REST API packs

## Context

Both packs build `heavy-rental-rest-api` from `.devcontainer/Dockerfile` (Java 21 Debian Trixie). `devcontainer.json` already stubs `"features": {}`. Spring Boot Dashboard Run starts only the JVM; it has no `preLaunchTask` / sidecar hook.

In-force ADRs: 0002 (OLTP SoT), 0005 (dual packs + promote).

## Goals / Non-Goals

**Goals:** `stripe` on PATH in both packs; webhook forward target `http://localhost:8080/api/payments/webhook` from the same container as Dashboard-run Spring Boot.

**Non-Goals:** Stripe Java SDK, webhook controllers, Compose sidecar, baking `STRIPE_API_KEY`, extra forwarded ports, Haystack/Portal packs.

## Decisions

1. **Official Debian apt repo in Dockerfile** — not a third-party Dev Container Feature; not `stripe/stripe-cli` as a Compose service. Apt handles amd64/arm64.
2. **`postStartCommand` + helper script** — Dashboard cannot attach `stripe listen` to Run. Start listen when the container starts **if** `stripe login` config or `STRIPE_API_KEY` exists; otherwise print how to login and re-run the script.
3. **Forward to `localhost:8080`** — Dashboard runs Spring inside `heavy-rental-rest-api`, so localhost is the app. Override with `STRIPE_CLI_FORWARD_TO`.
4. **No new ADR** — CLI install is tooling, not an architecture boundary.

## Risks / Trade-offs

- [Interactive `stripe login` cannot complete in postStart] → script no-ops without credentials; operator logs in once then re-runs the script.
- [Listen before Spring is up] → Stripe retries webhook delivery; connection refused until Run.
- [Home directory not persisted] → login may be needed after rebuild unless `STRIPE_API_KEY` is set locally.

## Open Questions

None.
