# Proposal: Phase 4 D0 schema contract and fleet source docs

## Intent

Document REST API primary as the **fleet LTM pull source** for Haystack merge-sync (Phase 4 T0) and freeze a **D0 producer schema contract** for default tables (`asset`, `booking`, `category`).

## Scope

### In scope

- Spec Kit `contracts/schema-contract.md` (producer)
- OpenSpec + README/quickstart/verification cross-links
- Clarify: no merge-sync service in REST packs

### Out of scope

- Implementing `postgres-haystack-sync` (Haystack pack)
- Changing Compose topology or replication design
- Full Spring entity Java inventory

## Related

- Haystack consumer: `Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/contracts/schema-contract.md`
- Haystack archive: `openspec/changes/archive/2026-08-12-phase4-fleet-mirror-allowlist-d0/`
