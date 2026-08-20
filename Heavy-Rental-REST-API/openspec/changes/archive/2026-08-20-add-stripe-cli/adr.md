# ADR Review Manifest

## ADR Review Completed

- Date: 2026-08-20
- Reviewer: configuration-repo maintainers
- Change: `2026-08-20-add-stripe-cli`

## In-Force ADR Context Reviewed

- `adr/0002-rest-primary-oltp-source-of-truth.md` — unchanged; CLI does not write primary
- `adr/0005-rest-dual-packs-promote-devcontainer.md` — both nested packs must receive the same CLI install

## Repository-Level ADRs Created

- None: no major durable architectural decisions were introduced by this change.

## Notes

Stripe CLI is local tooling. Secrets stay out of Compose. Spring Boot Dashboard cannot start `stripe listen`; `postStartCommand` is the pack hook.
