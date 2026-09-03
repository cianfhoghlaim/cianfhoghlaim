# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: V1 API endpoint indexer (api_endpoints asset)

The system SHALL run a v1-native CocoIndex App for HTTP route indexing,
producing one row per route handler in the `api_endpoints` LanceDB
table. The App uses:

- Regex catalogue covering 4 frameworks: FastAPI (`@app.get`, `@router.post`),
  Hono (`app.get`, `hono.post`), TanStack Start (`createFileRoute`,
  `createServerFileRoute`), and Convex HTTP actions (`httpAction`).
- 1 `ApiEndpoint` dataclass with BGE-M3 embedding on the `summary` field
  (1024 dims).
- `asyncio.to_thread` to run the CPU-bound regex scan (does not block the
  event loop).
- 100-row upsert batches to respect the HNSW-DROP-THRESHOLD rule.
- `localfs.walk_dir`-style recursive walk with the codebase_indexing.py
  excludes (`.venv/`, `node_modules/`, `__pycache__/`, `target/`,
  `dist/`, `build/`, `.turbo/`, `.cocoindex_code/`, `stedding/`,
  `.git/`, `docs/cocoindex/`).

The Dagster asset `api_endpoints` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks the
v1 App via `cocoindex update oideachais.cocoindex_flows.api_indexing:api_app`.

#### Scenario: A developer searches the HTTP surface for an agent-memory route

- **GIVEN** the `api_endpoints` Dagster asset has materialised
- **WHEN** a developer runs `await search_api_endpoints("agent memory add")`
- **THEN** the v1 App returns the top-20 rows from the `api_endpoints`
  LanceDB table, ranked by BGE-M3 cosine similarity to the query,
  with `score = 1.0 - _distance`

#### Scenario: A developer filters by framework

- **GIVEN** the `api_endpoints` Dagster asset has materialised
- **WHEN** a developer runs `await search_api_endpoints("query", framework="hono")`
- **THEN** the v1 App returns only Hono routes (filtered by `framework = 'hono'`)

### Requirement: V1 filesystem layout indexer (filesystem_layout asset)

The system SHALL run a v1-native CocoIndex App for filesystem layout
indexing, producing one row per directory (depth 1-4) in the
`filesystem_layout` LanceDB table. The App uses:

- `os.walk` with excludes matching the codebase_indexing.py set.
- 1 `FsLayoutRow` dataclass with fields: `dir_path`, `file_count`,
  `total_bytes`, `file_types` (JSON-encoded `Counter`), `top_files`
  (JSON-encoded list of `[name, size]`), `largest_descendant`,
  `depth`, `summary`, and a BGE-M3 embedding on `summary` (1024 dims).
- `MAX_DEPTH = 4` to keep the row count bounded (~500 dirs in this
  monorepo at depth 4).
- 100-row upsert batches.

The Dagster asset `filesystem_layout` (group `infrastructure`) lives
in `sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks
the v1 App via `cocoindex update oideachais.cocoindex_flows.filesystem_indexing:fs_app`.

#### Scenario: A developer searches for a directory by description

- **GIVEN** the `filesystem_layout` Dagster asset has materialised
- **WHEN** a developer runs `await search_filesystem("dagster assets", min_depth=2)`
- **THEN** the v1 App returns the top-10 directories semantically related
  to "dagster assets", filtered to `depth >= 2`, ranked by BGE-M3 cosine similarity

#### Scenario: A developer inspects the largest file in a subtree

- **GIVEN** the `filesystem_layout` Dagster asset has materialised
- **WHEN** a developer reads the `largest_descendant` column for the
  `sruth/oideachais/dagster_defs/` row
- **THEN** the cell value is the relative path of the largest file in
  the subtree (e.g. `sruth/oideachais/dagster_defs/assets/codebase_assets.py`)

### Requirement: V1 storage backend indexer (storage_backends asset)

The system SHALL run a v1-native CocoIndex App for storage backend
indexing, producing one row per backend instance in the
`storage_backends` LanceDB table. The App uses:

- 9 storage kinds: `lancedb`, `duckdb`, `ducklake`, `postgres`,
  `garage`, `r2`, `d1`, `kv`, `iceberg`.
- Regex catalogue for source-file references (lancedb, duckdb,
  ducklake, postgres, garage, s3, r2).
- Wrangler-manifest scanner (both `wrangler.jsonc` and `wrangler.toml`)
  for D1 / KV / R2 bindings.
- 1 `StorageBackend` dataclass with BGE-M3 embedding on `summary`.
- 100-row upsert batches.

The Dagster asset `storage_backends` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks the
v1 App via `cocoindex update oideachais.cocoindex_flows.storage_indexing:storage_app`.

#### Scenario: A developer finds where the Irish curriculum data is stored

- **GIVEN** the `storage_backends` Dagster asset has materialised
- **WHEN** a developer runs `await search_storage("Irish curriculum", kind="ducklake")`
- **THEN** the v1 App returns the top-20 DuckLake rows semantically
  related to "Irish curriculum", ranked by BGE-M3 cosine similarity

#### Scenario: A developer lists all D1 bindings

- **GIVEN** the `storage_backends` Dagster asset has materialised
- **WHEN** a developer runs `await search_storage("", kind="d1", limit=100)`
- **THEN** the v1 App returns up to 100 rows where `kind = 'd1'`,
  each carrying `name` (the binding name) and `config_ref = '[[d1_databases]]'`

### Requirement: V1 config file indexer (config_files asset)

The system SHALL run a v1-native CocoIndex App for config file indexing,
producing one row per config file in the `config_files` LanceDB table.
The App uses:

- 12 config kinds: `docker-compose`, `mise`, `package`, `pyproject`,
  `turbo`, `wrangler`, `env`, `k8s`, `pulumi`, `dg`, `github`,
  `justfile`.
- Filename-based classification (first-match wins) + pattern match
  for `docker-compose*.y*ml`, `compose.y*ml`, `*.k8s.yaml`,
  `kustomization.yaml`, `.github/workflows/*.yml`.
- Per-kind parser (JSON / TOML / YAML) producing a structured
  `summary` (e.g. `mise.toml: mise tools python,uv,bun,dagger`)
  and a `package_count` (workspace size for `package.json` and
  `dg.toml`).
- Graceful fallback to a tiny TOML subset parser if `tomllib` is
  unavailable (Python 3.10).
- 1 `ConfigFile` dataclass with BGE-M3 embedding on `summary`.
- 100-row upsert batches.

The Dagster asset `config_files` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks
the v1 App via `cocoindex update oideachais.cocoindex_flows.config_indexing:config_app`.

#### Scenario: A developer finds the wrangler manifest for a worker

- **GIVEN** the `config_files` Dagster asset has materialised
- **WHEN** a developer runs `await search_config("cloudflare worker", kind="wrangler")`
- **THEN** the v1 App returns the top-15 wrangler rows semantically
  related to "cloudflare worker", ranked by BGE-M3 cosine similarity

#### Scenario: A developer lists all mise.toml files with their tool set

- **GIVEN** the `config_files` Dagster asset has materialised
- **WHEN** a developer runs `await search_config("", kind="mise", limit=50)`
- **THEN** the v1 App returns up to 50 rows where `kind = 'mise'`,
  each carrying a `summary` like `mise.toml: mise tools python,uv,bun`

## REMOVED Requirements

(None.)
