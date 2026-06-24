# Change: oideachais-storage-indexing-v1

## Why

Phase 2 of the 6-phase refactor plan. Phase 1 (`oideachais-codebase-graph-v1`, archived
2026-06-24) brought the *code* surface onto v1 CocoIndex: `codebase_chunks` +
`codebase_code_graph`. Phase 2 brings the *infrastructure* surface onto v1: API
endpoints, filesystem layout, storage backends, and config files.

The 4 v1 Apps replace 4 v0 Apps in `codeolas/cocoindex_flows/`:

- `oideachais/cocoindex_flows/api_indexing.py` (v1) — HTTP route
  surface (FastAPI + Hono + TanStack Start + Convex HTTP) into the
  `api_endpoints` LanceDB table with BGE-M3 embeddings. v0 at
  `codeolas/cocoindex_flows/api_indexing.py:scan_api_endpoints()` had
  no embedding and was regex-only.
- `oideachais/cocoindex_flows/filesystem_indexing.py` (v1) — directory
  structure (depth 1-4) with per-directory file-type histogram into the
  `filesystem_layout` LanceDB table. v0 at
  `codeolas/cocoindex_flows/filesystem_indexing.py` had no embedding
  and no file-type histogram.
- `oideachais/cocoindex_flows/storage_indexing.py` (v1) — every storage
  backend the monorepo touches (LanceDB / DuckDB / DuckLake / Postgres
  / Garage / S3 / R2 / D1 / KV / Iceberg) into the `storage_backends`
  LanceDB table. v0 at `codeolas/cocoindex_flows/storage_indexing.py`
  had no embedding and no `wrangler.jsonc` scanning.
- `oideachais/cocoindex_flows/config_indexing.py` (v1) — every config
  file in the repo (compose / mise / turbo / package / pyproject /
  wrangler / env / k8s / pulumi / dg / github workflows / justfile)
  into the `config_files` LanceDB table. v0 at
  `codeolas/cocoindex_flows/config_indexing.py` had no embedding and
  no structured summary.

The 4 v1 Apps follow the canonical pattern from
`oideachais/cocoindex_flows/codebase_indexing.py`:

- `@coco.fn` + `@coco.lifespan` for processing
- `lancedb.mount_table_target(...)` for the output
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for the embedding
- 100-row upsert batches (HNSW-DROP-THRESHOLD respected)

The 4 new Dagster assets live in
`oideachais/dagster_defs/assets/infrastructure_assets.py` (group
`infrastructure`) and follow the same shape as
`codebase_assets.py`: each kicks the v1 App's update via `cocoindex
update` and reports the LanceDB row count + per-category breakdown as
materialization metadata.

The `oideachais` lakehouse is now the **canonical surface indexer** for
the entire Cianfhoghlaim monorepo. The v0 code in `codeolas/` becomes
a fallback for the 30-day deprecation window and is not deleted (per
the user's plan: codeolas/ stays as a standalone subdir for now).

## What Changes

### 1. `oideachais/cocoindex_flows/api_indexing.py` (NEW)

v1 CocoIndex App named `ApiIndex` (group `infrastructure`). Indexes
the HTTP route surface across 4 frameworks into the `api_endpoints`
LanceDB table. 5-row batch.

### 2. `oideachais/cocoindex_flows/filesystem_indexing.py` (NEW)

v1 CocoIndex App named `FilesystemIndex` (group `infrastructure`).
Indexes every directory up to depth 4 into the `filesystem_layout`
LanceDB table. 3-row batch.

### 3. `oideachais/cocoindex_flows/storage_indexing.py` (NEW)

v1 CocoIndex App named `StorageIndex` (group `infrastructure`).
Indexes every storage backend reference (incl. wrangler manifests) into
the `storage_backends` LanceDB table. 2-row batch.

### 4. `oideachais/cocoindex_flows/config_indexing.py` (NEW)

v1 CocoIndex App named `ConfigIndex` (group `infrastructure`). Indexes
every config file (compose / mise / turbo / package / pyproject /
wrangler / env / k8s / pulumi / dg / github workflows / justfile) into
the `config_files` LanceDB table. 3-row batch.

### 5. `oideachais/dagster_defs/assets/infrastructure_assets.py` (NEW)

4 Dagster assets (`group_name="infrastructure"`):

- `api_endpoints` — kicks `oideachais.cocoindex_flows.api_indexing:api_app`
- `filesystem_layout` — kicks `oideachais.cocoindex_flows.filesystem_indexing:fs_app`
- `storage_backends` — kicks `oideachais.cocoindex_flows.storage_indexing:storage_app`
- `config_files` — kicks `oideachais.cocoindex_flows.config_indexing:config_app`

### 6. `oideachais/STATUS.md` (MODIFIED)

§3 (CocoIndex v0 vs v1) — add 4 new v1 rows.
§4 (Dagster asset catalogue) — add a new `infrastructure` group row.

### 7. `.agents/skills/cocoindex/SKILL.md` + `.agents/skills/ccc/SKILL.md` (MODIFIED)

Reference the new v1 companion pattern for the 4 infrastructure apps.

### 8. `openspec/specs/oideachais-pipeline/spec.md` (MODIFIED via 4 ADDED Requirements)

4 new ADDED Requirements:

- V1 API endpoint indexer (`api_endpoints` asset)
- V1 filesystem layout indexer (`filesystem_layout` asset)
- V1 storage backend indexer (`storage_backends` asset)
- V1 config file indexer (`config_files` asset)

## Impact

- Affected specs: `oideachais-pipeline` (4 ADDED Requirements)
- Affected code:
  - 4 new files in `oideachais/cocoindex_flows/`
  - 1 new file in `oideachais/dagster_defs/assets/`
- Affected skills: `cocoindex` (reference), `ccc` (reference),
  `oideachas-pipeline` (no change)
- v0 fallback: `codeolas/cocoindex_flows/{api,filesystem,storage,config}_indexing.py`
  retained for 30 days, not deleted
- v1 App update command: `cocoindex update oideachais.cocoindex_flows.api_indexing:api_app`
  (and 3 more for filesystem / storage / config)
- Dagster assets register via `oideachais/dagster_defs/definitions.py`
  import (`infrastructure_assets = [...]`)

## Success criteria

- All 4 v1 Apps import cleanly under `oideachais.cocoindex_flows.*`
- All 4 scan helpers produce the expected row count on a 100-file test repo
- `oideachais/dagster_defs/assets/infrastructure_assets.py` materialises
  without import errors in `dg dev`
- `openspec validate oideachais-storage-indexing-v1 --strict` passes
- The 4 Dagster assets show up in the unified `dg` UI
  alongside `codebase_chunks` and `codebase_code_graph`
