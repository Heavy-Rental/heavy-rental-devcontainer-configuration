# Contract: Neo4j connection environment

## App container (`haystack-fast-api`)

| Name | Required | Default | Description |
|---|---|---|---|
| `NEO4J_URI` | yes | `bolt://neo4j:7687` | Bolt URL (Compose DNS) |
| `NEO4J_USER` | yes | `neo4j` | Username |
| `NEO4J_PASSWORD` | yes | `heavyrental` | Password (dev only) |
| `NEO4J_DATABASE` | no | `neo4j` | Database name |

## Neo4j service

| Name | Default | Description |
|---|---|---|
| `NEO4J_AUTH` | `neo4j/heavyrental` | Initial auth (`user/password`) |
| Heap settings | 512m–1G | Dev-friendly memory |

## Connectivity expectations

- From **app** network: `bolt://neo4j:7687`
- From **host**: `bolt://localhost:7687`, Browser `http://localhost:7474`
- Credentials for app and Browser MUST match `NEO4J_AUTH`

## Haystack package

- Install: `uv add neo4j-haystack` or `uv pip install neo4j-haystack`
- Client SHOULD read URI/user/password from env above

## IDE client (Neo4j for VS Code)

**Important:** Unlike Postgres (`pgsql.connections`), Neo4j for VS Code does **not** accept connection profiles in `settings.json` / `devcontainer.json`. Connections are stored in the extension’s global state and SecretStorage after you create them in the UI.

| Field | Inside devcontainer | From host (port-forward) |
|---|---|---|
| Extension ID | `neo4j-extensions.neo4j-for-vscode` | same (if connected remotely) |
| Recommended name | Haystack Local Neo4j | Haystack Local Neo4j (host) |
| Scheme | `bolt` | `bolt` |
| Host | `neo4j` | `localhost` |
| Port | `7687` | `7687` |
| User | `neo4j` | `neo4j` |
| Password | `heavyrental` (dev only) | `heavyrental` (dev only) |
| Database | `neo4j` | `neo4j` |

### Supported VS Code settings only

| Key | Default in this stack | Notes |
|---|---|---|
| `neo4j.features.linting` | `true` | Declared by the extension |
| `neo4j.trace.server` | `off` | Language-server tracing |

Do **not** add a fictional `neo4j.connections` (or similar) array — the extension ignores it.

### Create connection (UI)

1. Command Palette → **Neo4j: Create new connection** (or Neo4j activity bar → **+**).
2. Enter the fields in the table above.
3. Connect and run `RETURN 1`.

Neo4j Browser remains available at `http://localhost:7474` and is not replaced by the extension.
