# Tasks: oideachais-storage-indexing-v1

## 1. `sruth/oideachais/cocoindex_flows/api_indexing.py`

- [x] Create the v1 App file (api_indexing.py)
- [x] `ApiIndex` coco.App with `api_app_main` @coco.fn
- [x] `ApiEndpoint` dataclass + lancedb.TableSchema (BGE-M3 embedding on `summary`)
- [x] `_scan_file_for_endpoints` for FastAPI / Hono / TanStack Start / Convex HTTP
- [x] `_walk_repo_for_endpoints` orchestrator
- [x] `search_api_endpoints(query, framework=None, method=None, limit=20)` helper
- [x] `_find_handler_name` best-effort post-declaration handler lookup
- [x] Functional test: 325 endpoints in `sruth/oideachais/` (4.7s)

## 2. `sruth/oideachais/cocoindex_flows/filesystem_indexing.py`

- [x] Create the v1 App file (filesystem_indexing.py)
- [x] `FilesystemIndex` coco.App with `fs_app_main` @coco.fn
- [x] `FsLayoutRow` dataclass + lancedb.TableSchema
- [x] `_walk_directory` per-dir walk + file-type Counter + top-5 largest files
- [x] `_walk_repo_for_layout` orchestrator (MAX_DEPTH=4)
- [x] `search_filesystem(query, min_depth=None, limit=10)` helper
- [x] Functional test: 351 dirs in `sruth/oideachais/` (0.1s)

## 3. `sruth/oideachais/cocoindex_flows/storage_indexing.py`

- [x] Create the v1 App file (storage_indexing.py)
- [x] `StorageIndex` coco.App with `storage_app_main` @coco.fn
- [x] `StorageBackend` dataclass + lancedb.TableSchema
- [x] `_scan_source_file` for lancedb / duckdb / ducklake / postgres / garage / s3 / r2
- [x] `_scan_wrangler_manifest` for D1 / KV / R2 bindings
- [x] `_walk_repo_for_storage` orchestrator
- [x] `search_storage(query, kind=None, limit=20)` helper
- [x] Fix `_R2_URI_RE` regex SyntaxError (was a string-quote collision)
- [x] Functional test: 151 backends in `sruth/oideachais/` (6.3s)

## 4. `sruth/oideachais/cocoindex_flows/config_indexing.py`

- [x] Create the v1 App file (config_indexing.py)
- [x] `ConfigIndex` coco.App with `config_app_main` @coco.fn
- [x] `ConfigFile` dataclass + lancedb.TableSchema
- [x] `_classify` filename → ConfigKind mapper
- [x] `_summarize` per-kind parser (JSON / TOML / YAML)
- [x] `_safe_toml` (tomllib + tiny fallback for Py 3.10)
- [x] `_walk_repo_for_config` orchestrator (3-pass: exact + pattern + .github/workflows)
- [x] `search_config(query, kind=None, limit=15)` helper
- [x] Fix pyproject.toml parse failure (dependencies can be list or dict)
- [x] Functional test: 12 configs in `sruth/oideachais/` (10.6s)

## 5. `sruth/oideachais/dagster_defs/assets/infrastructure_assets.py`

- [x] Create the asset file
- [x] 4 @asset(group_name="infrastructure") declarations
- [x] `api_endpoints` — kicks `oideachais.cocoindex_flows.api_indexing:api_app`
- [x] `filesystem_layout` — kicks `oideachais.cocoindex_flows.filesystem_indexing:fs_app`
- [x] `storage_backends` — kicks `oideachais.cocoindex_flows.storage_indexing:storage_app`
- [x] `config_files` — kicks `oideachais.cocoindex_flows.config_indexing:config_app`
- [x] 4 `_get_*_stats()` helpers (lancedb connect → row count + per-kind breakdown)
- [x] `infrastructure_assets` export list

## 6. `sruth/oideachais/STATUS.md`

- [x] §3 — add 4 new v1 rows
- [x] §4 — add `infrastructure` group row

## 7. `.agents/skills/`

- [x] `.agents/skills/ccc/SKILL.md` — reference the 4 new Dagster assets
- [x] `.agents/skills/cocoindex/SKILL.md` — reference the 4 new v1 Apps

## 8. `openspec/`

- [x] Create `openspec/changes/oideachais-storage-indexing-v1/proposal.md`
- [x] Create `openspec/changes/oideachais-storage-indexing-v1/tasks.md`
- [x] Create `openspec/changes/oideachais-storage-indexing-v1/specs/oideachais-pipeline/spec.md`
  (4 ADDED Requirements)
- [x] `openspec validate oideachais-storage-indexing-v1 --strict`
- [x] `openspec archive oideachais-storage-indexing-v1 --yes`
- [x] Commit + push to `q3-2026-oideachais-consolidation`
