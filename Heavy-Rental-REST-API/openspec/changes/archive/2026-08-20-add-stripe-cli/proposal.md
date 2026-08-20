# Proposal: Add Stripe CLI to REST API Dev Containers

## Why

Spring Boot developers need the Stripe CLI in the REST API app container to trigger test events and forward webhooks to the local API (`/api/payments/webhook`) without installing Stripe on the host.

## What Changes

- Install official `stripe` CLI in both pack Dockerfiles (with / without replica)
- Add `start-stripe-listen.sh` and wire it as `postStartCommand`
- Document that Spring Boot Dashboard Run cannot start `stripe listen`; container start is the hook
- Spec Kit / OpenSpec / OpenSPDD updates

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `rest-api-devcontainer` — Stripe CLI on PATH; optional webhook listen on container start

## Impact

App image rebuild only. Compose services, ports, JDBC URL, and Postgres topology are unchanged. No Stripe secrets in Compose.

## Related

- ADR-0005 (dual packs; change both nested `.devcontainer` trees)
