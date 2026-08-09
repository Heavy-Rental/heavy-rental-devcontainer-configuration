# Design: REST API devcontainer dual packs

## Approach

- **As-built packs** remain the implementation under named folders.
- **Specs** describe shared baseline + with-replica / without-replica profiles.
- **Promote rule:** `mv "<pack>/.devcontainer" ./.devcontainer` from `Heavy-Rental-REST-API/`.
- **Difference:** only the with-replica pack runs `db-replica-one` (host 5433, streaming); app always writes to primary.

## Files

- `Heavy-Rental-REST-API/README.md`
- `Heavy-Rental-REST-API/specs/001-rest-api-devcontainer/*`
- `Heavy-Rental-REST-API/openspec/specs/rest-api-devcontainer/spec.md`
