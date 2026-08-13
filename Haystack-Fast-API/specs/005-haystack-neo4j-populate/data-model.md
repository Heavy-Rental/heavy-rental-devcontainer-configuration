# Data Model: Fleet Neo4j Projection

## Source (SQL)

| Logical entity | Table (`public`) | Required key | Default allowlist |
|----------------|------------------|--------------|-------------------|
| Asset | `asset` | `id` | Yes |
| Booking | `booking` | `id` | Yes |
| Category | `category` | `id` | Yes |

All other columns are projected as node properties (coerced to Neo4j scalars).

## Target (Neo4j)

| Label | MERGE key | Internal props |
|-------|-----------|----------------|
| `Asset` | `id` | `_source='fleet-mirror'`, `_populated_at` |
| `Booking` | `id` | same |
| `Category` | `id` | same |

Uniqueness: `CREATE CONSTRAINT … IF NOT EXISTS FOR (n:Label) REQUIRE n.id IS UNIQUE`.

## Relationships (best-effort)

| Rel type | Pattern | When |
|----------|---------|------|
| `IN_CATEGORY` | `(:Asset)-[:IN_CATEGORY]->(:Category)` | `asset` has `category_id` / `categoryId` / `category` |
| `FOR_ASSET` | `(:Booking)-[:FOR_ASSET]->(:Asset)` | `booking` has `asset_id` / `assetId` / `asset` |

## Isolation

| Namespace | Labels | Touched by populate? |
|-----------|--------|----------------------|
| KG-2 Fleet | `Asset`, `Booking`, `Category` | Yes (MERGE / scoped delete) |
| KG-1 Project / DocumentStore | `Document` (default protected) | **Never** |
| Other | any non-fleet | **No** |

Rebuild / orphan delete operate only on fleet labels **minus** `KG1_PROTECTED_LABELS`.
