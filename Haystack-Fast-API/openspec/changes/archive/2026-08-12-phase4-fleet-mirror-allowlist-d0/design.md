# Design: Phase 4 allowlist + lag metrics + D0

## Decisions

| Topic | Decision |
|-------|----------|
| Allowlist default | `asset,booking,category` (D0 v1.0) |
| Full merge escape hatch | `SYNC_TABLE_ALLOWLIST=all` or `*` |
| FDW | `IMPORT FOREIGN SCHEMA ... LIMIT TO (...)` when list mode |
| Lag metrics | Log-only `METRICS cycle` / `METRICS merge` (no Prometheus) |
| Schema contract | Consumer doc under Spec Kit contracts; producer on REST pack |

## Data flow

```text
postgres-primary (public)
        │  FDW LIMIT TO allowlist
        ▼
postgres-haystack staging (primary_snapshot)
        │  PK/unique upsert
        ▼
postgres-haystack public (allowlisted tables)
```

## Failure modes

- Missing allowlisted table on primary: skip merge for that name; other allowlisted tables continue.
- Wrong physical names: operator overrides allowlist env and revises D0 contract.
- Zero candidates: cycle succeeds with 0 tables; metrics still logged.
