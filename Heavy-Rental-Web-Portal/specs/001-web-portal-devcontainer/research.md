# Research: Web Portal Devcontainer

## Why no local database

The portal is a presentation tier. OLTP lives on REST `postgres-primary` (ADR-0002). A portal-local DB would create a second SoT and skip Spring rules.

## Why not call Haystack from the browser

Recommend features stay dual-hop behind Spring so the UI has one public API and Haystack credentials stay off the browser (ADR-0006).

## Why no promote step

Unlike REST dual packs, there is only one portal profile. `.devcontainer` already sits at `Heavy-Rental-Web-Portal/`.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Include Postgres in portal Compose | Duplicates OLTP; bypasses Spring |
| Vite proxy defaults in this pack | App-owned config; sources are volume-mounted |
| Call Haystack from the SPA | Splits public API; leaks AI-plane credentials |

## Decision

Document as-built single-service pack; keep API URL in application sources.
