# Tasks: oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets

## 1. Pre-flight verification

- [ ] Run `grep -rn "from sruth.oideachais.dagster_assets\|from oideachais.dagster_assets" sruth/ infrastructure/ apps/ web/ tests/ --include="*.py"` and confirm EXACTLY 2 matches: `dagster_defs/definitions.py:169,177`
- [ ] Run `grep -rn "from sruth.oideachais.storage\.[a-z_]" sruth/ infrastructure/ apps/ web/ tests/ --include="*.py"` and confirm ONLY 3 test files (conftest.py + tests/dlt_sources/test_integration.py + tests/storage/test_lancedb_cloud.py)
- [ ] Run `git log --all --oneline -- sruth/oideachais/dagster_assets/ sruth/oideachais/storage/` to confirm both dirs originate from `137ad7b9a` or earlier sprawl commits

## 2. Part A — Migrate dagster_assets active modules to dagster_defs/assets/

- [ ] `git mv sruth/oideachais/dagster_assets/model_conversion.py sruth/oideachais/dagster_defs/assets/model_conversion.py`
- [ ] Verify `parents[4]` in the moved file is now correct (path math: 4 levels up from `dagster_defs/assets/` = REPO_ROOT)
- [ ] `git mv sruth/oideachais/dagster_assets/asset_generation.py sruth/oideachais/dagster_defs/assets/asset_generation.py`
- [ ] Verify the moved file's lazy BAML import still resolves

## 3. Part B — Update dagster_defs/definitions.py imports

- [ ] Edit `sruth/oideachais/dagster_defs/definitions.py:165-181`: replace the try/except scaffolding with:
  ```python
  from .assets.model_conversion import model_conversion_assets
  from .assets.asset_generation import asset_generation_assets
  ```
- [ ] Add both `model_conversion_assets` and `asset_generation_assets` to the unified `defs` object (as separate lists in the Assets section)
- [ ] Drop the `dagster_assets_model_conversion_skipped` warning logic

## 4. Part C — Migrate storage/ files to core/storage/{clients,config}/

- [ ] `git mv sruth/oideachais/storage/config.py sruth/oideachais/core/storage/config.py`
- [ ] `git mv sruth/oideachais/storage/connections.py sruth/oideachais/core/storage/connections.py`
- [ ] `git mv sruth/oideachais/storage/ducklake.py sruth/oideachais/core/storage/ducklake.py`
- [ ] `git mv sruth/oideachais/storage/init_schemas.py sruth/oideachais/core/storage/init_schemas.py`
- [ ] `git mv sruth/oideachais/storage/lance_iceberg.py sruth/oideachais/core/storage/lance_iceberg.py`
- [ ] `git mv sruth/oideachais/storage/curriculum_vectors.py sruth/oideachais/core/storage/curriculum_vectors.py`
- [ ] `mkdir -p sruth/oideachais/core/storage/clients/`
- [ ] `git mv sruth/oideachais/storage/ducklake_client.py sruth/oideachais/core/storage/clients/ducklake.py`
- [ ] `git mv sruth/oideachais/storage/ducklake_filesystem.py sruth/oideachais/core/storage/clients/ducklake_filesystem.py`
- [ ] `git mv sruth/oideachais/storage/lancedb_cloud.py sruth/oideachais/core/storage/clients/lancedb_cloud.py`

## 5. Part D — Update internal imports in migrated files

After the moves, internal cross-references may break. Scan for any
`from .config import`, `from .connections import`, etc. inside the
migrated files and update them. Specifically:

- [ ] `grep -rn "from oideachais.storage\.\|from sruth.oideachais.storage\." sruth/oideachais/core/storage/ --include="*.py"` — fix any internal imports
- [ ] `grep -rn "from oideachais.storage\.\|from sruth.oideachais.storage\." sruth/oideachais/dagster_defs/assets/ --include="*.py"` — fix any internal imports

## 6. Part E — Update core/storage/__init__.py re-exports

- [ ] Edit `sruth/oideachais/core/storage/__init__.py` to add re-exports for the 25 new symbols: `CogneeConfig, DuckLakeConfig, FalkorDBConfig, GarageConfig, LakehouseConfig, LanceDBConfig, MemgraphConfig, PlanetScaleConfig, StorageConfig, StorageBackend, StorageManager, DuckLakeClient, DuckLakeSnapshot, DuckLakeOCRStorage, LanceIcebergBackend, LanceIcebergClient, LanceTableInfo, LanceDBCloudClient, LanceDBCloudConfig, CurriculumVectorSearch, get_config, reset_config, get_storage_backend, get_storage_manager, get_ducklake_backend`

## 7. Part F — Update 3 test files

- [ ] Edit `sruth/oideachais/tests/conftest.py:258`: `from oideachais.storage.lancedb_cloud import CircuitBreaker` → `from oideachais.core.storage.clients.lancedb_cloud import CircuitBreaker`
- [ ] Edit `sruth/oideachais/tests/dlt_sources/test_integration.py:282,317`: replace `oideachais.storage.lancedb_cloud` with `oideachais.core.storage.clients.lancedb_cloud`
- [ ] Edit `sruth/oideachais/tests/storage/test_lancedb_cloud.py:227,333,345,371,380,388,396`: replace `oideachais.storage.lancedb_cloud` with `oideachais.core.storage.clients.lancedb_cloud`

## 8. Part G — Update openspec spec references

- [ ] Edit `openspec/specs/oideachais-pipeline/spec.md:166`: `sruth/oideachais/storage/ducklake_client.py` → `sruth/oideachais/core/storage/clients/ducklake.py`
- [ ] Edit `openspec/specs/oideachais-pipeline/spec.md:869`: same path update
- [ ] Edit `openspec/specs/oideachais-pipeline/spec.md:870`: `sruth/oideachais/storage/lancedb_cloud.py` → `sruth/oideachais/core/storage/clients/lancedb_cloud.py`
- [ ] Edit `openspec/specs/oideachais-pipeline/spec.md:912`: `sruth/oideachais/storage/` → `sruth/oideachais/core/storage/`
- [ ] Edit `openspec/changes/refactor-quadrants-to-sruth/proposal.md:182`: same path update

## 9. Part H — Update STATUS.md + baml_src/README.md references

- [ ] Edit `sruth/oideachais/STATUS.md:30`: any reference to `dagster_assets/asset_generation` → `dagster_defs/assets/asset_generation`
- [ ] Edit `sruth/oideachais/baml_src/README.md:131`: same path update

## 10. Part I — Delete legacy directories

- [ ] `git rm sruth/oideachais/dagster_assets/grammar_validation.py sruth/oideachais/dagster_assets/pdf_benchmark.py sruth/oideachais/dagster_assets/syntactic_parsing.py sruth/oideachais/dagster_assets/__init__.py sruth/oideachais/dagster_assets/README.md`
- [ ] `rmdir sruth/oideachais/dagster_assets/`
- [ ] `git rm sruth/oideachais/storage/__init__.py sruth/oideachais/storage/README.md`
- [ ] `rmdir sruth/oideachais/storage/`

## 11. Validation gates

- [ ] `openspec validate oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets --strict` → PASS
- [ ] `python -c "import sruth.oideachais"` → OK
- [ ] `python -c "from sruth.oideachais.dagster_defs.assets.model_conversion import model_conversion_assets; print(len(model_conversion_assets))"` → prints a number ≥ 8
- [ ] `python -c "from sruth.oideachais.dagster_defs.assets.asset_generation import asset_generation_assets; print(len(asset_generation_assets))"` → prints a number ≥ 4
- [ ] `python -c "from sruth.oideachais.core.storage import CogneeConfig, DuckLakeConfig, StorageManager, DuckLakeClient"` → OK
- [ ] `python -c "from sruth.oideachais.core.storage.clients.lancedb_cloud import LanceDBCloudClient, CircuitBreaker, EmbeddingBatch, LanceDBCloudConfig"` → OK
- [ ] `python -c "from sruth.oideachais.core.storage.curriculum_vectors import CurriculumVectorSearch"` → OK
- [ ] `python -c "from sruth.oideachais.dagster_defs.sensors import all_sensors; assert len(all_sensors) >= 5"` → OK
- [ ] `grep -rn "from sruth.oideachais.dagster_assets\|from oideachais.dagster_assets\|from sruth.oideachais.storage\.[a-z_]\|from oideachais.storage\.[a-z_]" sruth/ infrastructure/ apps/ web/ tests/ --include="*.py"` → 0 matches
- [ ] `mise run lint:skills` → 123/123 PASS

## 12. Doc updates

- [ ] `sruth/oideachais/REFACTORING.md` — add "Round 11 Phase 2B — Legacy Migration (2026-06-25)" entry
- [ ] `sruth/oideachais/AGENTS.md` — update route "Add a new Dagster asset" row to remove the legacy `dagster_assets/` hint (currently lists 40+ modules in `dagster_defs/assets/`); add `core/storage/{clients,config}/` to the storage row

## 13. Archive + commit + push

- [ ] `openspec archive oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets --yes`
- [ ] `git add -A` (then verify `git diff --cached --stat` shows only intended changes; if other in-flight work creeps in, `git reset HEAD` and re-stage only my files)
- [ ] `git commit -m "refactor(oideachais): round 11 phase 2b — migrate storage/ + dagster_assets/ to canonical"`
- [ ] `git pull --rebase && git push`
- [ ] `git status` → branch up to date (other in-flight modifications from other work are expected)
