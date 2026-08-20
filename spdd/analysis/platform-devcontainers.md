# SPDD analysis: Heavy Rental platform devcontainers

Reverse-engineered from as-built packs (equivalent to `/spdd-analysis` + `/spdd-reverse`).

## Domain keywords

`heavy-rental-network`, pack, Dev Container, Compose, `postgres-primary`, `postgres-haystack`, merge-sync, allowlist, D0 schema contract, pgvector, Neo4j, KG-1, KG-2, `neo4j-populate`, dual-hop, promote `.devcontainer`.

## Domain concepts

| Concept | Meaning |
|---------|---------|
| Pack | A folder with `.devcontainer` + Compose for one workspace |
| OLTP SoT | `postgres-primary` / `heavy_rental` written by Spring |
| Fleet mirror | Allowlisted pull upsert into `postgres-haystack` |
| KG-1 | DocumentStore labels on Neo4j (protected) |
| KG-2 | Fleet graph labels populated from SQL |
| Dual-hop | Portal → Spring → Haystack (Haystack not browser-facing) |

## Risks

| Risk | Mitigation (in-force) |
|------|------------------------|
| Haystack writes primary | ADR-0002; sync is pull-only |
| Global Neo4j wipe | ADR-0008; scoped MERGE / delete |
| Vector extension on OLTP | ADR-0007; pgvector only on Haystack |
| CDC operational cost | ADR-0004; 60s poll |
| Agent re-litigates architecture | ADR-0010; read `adr/` before design |

## Design direction

Keep three independent packs. Document with OpenSpec (what) + OpenSPDD (how) + ADR (why). Do not collapse into one Compose. Do not expand D0 default allowlist without a new contract version.

## Related canvases

`spdd/prompt/platform-devcontainers.md` and the three pack canvases.
