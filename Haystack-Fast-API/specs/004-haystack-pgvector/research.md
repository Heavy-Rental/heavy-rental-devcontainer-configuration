# Research: Haystack pgvector platform

**Feature**: `004-haystack-pgvector`  
**Date**: 2026-08-12

## Decision: image vs build-from-source

| Option | Pros | Cons |
|--------|------|------|
| **A. `pgvector/pgvector:pg17`** | Official-ish community image; extension preinstalled; Postgres 17 aligned with primary | Extra image pull; not same tag as `postgres:17` |
| B. Custom Dockerfile on `postgres:17` + compile pgvector | Exact base match | Build time, maintenance |
| C. Plain `postgres:17` + apt package (if available) | Minimal change | Package availability varies by OS tag |

**Decision**: **A** — matches feasibility dual-plane §11.4 T5 recommendation.

## Decision: bootstrap path

| Option | Pros | Cons |
|--------|------|------|
| initdb only | Simple for fresh volumes | Skipped on existing data dirs |
| Operator one-shot only | Explicit | Easy to miss on upgrade |
| **initdb + healthcheck `CREATE EXTENSION IF NOT EXISTS`** | Fresh + upgraded volumes | Healthcheck does light DDL (idempotent) |

**Decision**: initdb for first boot; healthcheck ensure for upgrades.

## Relation to other stores

| Store | Role in stack |
|-------|----------------|
| Postgres domain + **pgvector** | Fleet mirror tables + **target** durable project vectors (I1) |
| Neo4j (`002`) | Graph DocumentStore / future KG-2 projection |
| FAISS (`003`) | Historical only — not default |

## Embedding dim

Default **768** aligns with existing Neo4j/FAISS pack documentation in this monorepo. App I1 must use the same dim when creating vector columns; changing dim later requires table migration.

## Non-goals confirmed

DocumentStore factory, pipeline cutover, tenant filters, TTL — application repo Phase 5.2+.
