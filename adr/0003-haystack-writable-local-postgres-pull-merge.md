# ADR-0003: Haystack uses a writable local Postgres with pull merge

- Status: accepted
- Date: 2026-08-20
- Tags: haystack, postgres, sync

## Context

Haystack developers need a fully writable relational database for experiments. A streaming replica of `postgres-primary` is read-only. Restoring a dump with `--clean` would wipe local-only rows. Bidirectional sync would threaten the OLTP SoT (ADR-0002).

## Decision

Give Haystack its own writable Postgres (`postgres-haystack`) as the app’s default `DATABASE_URL`. Refresh shared domain data with a **pull merge** job (`postgres-haystack-sync`): FDW (or equivalent) staging from `postgres-primary`, then upsert by primary key or unique key. Default policy retains local-only rows and columns; primary wins on key conflict; primary deletes are not mirrored.

The Haystack app MUST always use local Postgres, never `postgres-primary`, as its default relational datasource.

## Consequences

- Local sandbox survives primary downtime (sync skips by default; see ADR-0004).
- Mirror can lag and diverge (local-only rows, no delete mirroring).
- Extra Postgres instance and sync job in the Haystack pack.
- Source hostname is container DNS `postgres-primary`, not Compose service name `db-primary`.

## Related

- ADR-0002, ADR-0004, ADR-0009
- OpenSpec: `Haystack-Fast-API/openspec/specs/haystack-devcontainer/spec.md`
- Spec Kit: `Haystack-Fast-API/specs/001-haystack-postgres-merge-sync/`
