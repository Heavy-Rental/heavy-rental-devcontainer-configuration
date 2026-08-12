# Design: Phase 4 D0 + fleet source (REST)

## Role split

| Pack | Phase 4 role |
|------|----------------|
| REST API | T0 source (`postgres-primary`) + D0 producer contract |
| Haystack | T1 lag metrics + T2 allowlist + D0 consumer + sync job |

## Why docs-only on REST

Merge-sync is a **pull** from Haystack. Adding a push job on Spring would duplicate ownership and violate the dual-plane design (primary remains OLTP SoT; haystack is mirror).
