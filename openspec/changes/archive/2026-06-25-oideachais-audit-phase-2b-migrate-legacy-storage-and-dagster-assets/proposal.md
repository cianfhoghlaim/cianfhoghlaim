# Change: oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets

## Why

Phase 2A removed 4 pure-duplicate surfaces (~5,500 LOC). This change
migrates the remaining unique files (2 active `dagster_assets/` modules +
9 unique `storage/` files = ~7,700 LOC) to their canonical homes, then
`git rm`'s the legacy directories.

These two surfaces are NOT byte-identical duplicates — they carry
substantial unique code that must be preserved across the migration:

1. **`dagster_assets/`** has 2 active asset modules
   (`model_conversion.py`, `asset_generation.py`) that are imported via
   `dagster_defs/definitions.py:165-181` (guarded try/except). They need
   migration to `dagster_defs/assets/` so the `parents[N]` REPO_ROOT
   calculation becomes correct (it was `parents[4]` at the legacy 3-level
   path; the new 4-level path makes `parents[4]` actually point at
   REPO_ROOT). Plus 3 dead modules (`grammar_validation`,
   `pdf_benchmark`, `syntactic_parsing`) need deletion (~1,300 LOC).

2. **`storage/`** has 9 unique files (config, connections, ducklake,
   ducklake_client, ducklake_filesystem, init_schemas, lance_iceberg,
   lancedb_cloud, curriculum_vectors) that carry substantial backend
   client code (DuckLake, Lance Iceberg, LanceDB Cloud, OCR storage,
   curriculum vector search). The `core/storage/` canonical home was
   created but the migration was never completed.

External usage: ONLY 3 test files import from legacy `storage/*` (conftest
+ test_integration + test_lancedb_cloud). NO production code uses it.
NO openspec canonical paths reference it (the 2 refs in
`oideachais-pipeline/spec.md:166,869-870,912` and the `refactor-quadrants-to-sruth/proposal.md:182`
ref are stale and need updates).

## What Changes

### Part A — Migrate `dagster_assets/` active modules to `dagster_defs/assets/`

| Source | Destination | LOC | Notes |
|:--|:--|--:|:--|
| `dagster_assets/model_conversion.py` | `dagster_defs/assets/model_conversion.py` | 374 | `parents[4]` → `parents[4]` (path math becomes correct at new 4-level location) |
| `dagster_assets/asset_generation.py` | `dagster_defs/assets/asset_generation.py` | 281 | No path math (lazy imports only); import `boto3` etc. preserved |
| `dagster_assets/grammar_validation.py` | (delete — 0 importers) | 415 | Dead since 2026-06 refactor |
| `dagster_assets/pdf_benchmark.py` | (delete — 0 importers) | 483 | Dead since 2026-06 refactor |
| `dagster_assets/syntactic_parsing.py` | (delete — 0 importers) | 535 | Dead since 2026-06 refactor |
| `dagster_assets/__init__.py` | (delete with directory) | 91 | Only existed to re-export the 5 submodules; no external importer |
| `dagster_assets/README.md` | (delete with directory) | 11 | Stale nav |

After migration, update `dagster_defs/definitions.py:165-181`:
- Drop the try/except scaffolding (the migration makes the imports safe)
- Import as `from .assets.model_conversion import model_conversion_assets`
- Import as `from .assets.asset_generation import asset_generation_assets`
- Add both to the unified `defs` object

After migration, update STATUS.md:30 + baml_src/README.md:131 to
reference the new canonical paths.

### Part B — Migrate `storage/` unique files to `core/storage/{clients,config}/`

| Source | Destination | LOC | Notes |
|:--|:--|--:|:--|
| `storage/config.py` | `core/storage/config.py` | 359 | 9 dataclasses + `get_config`/`reset_config` (multi-backend config) |
| `storage/connections.py` | `core/storage/connections.py` | 691 | 4 backends + `StorageBackend`/`StorageManager` |
| `storage/ducklake.py` | `core/storage/ducklake.py` | 780 | `CELTIC_MANUSCRIPT_SCHEMAS` + `DuckLakeClient` + `DuckLakeSnapshot` |
| `storage/ducklake_client.py` | `core/storage/clients/ducklake.py` | 882 | Postgres catalog + Garage S3 connector |
| `storage/ducklake_filesystem.py` | `core/storage/clients/ducklake_filesystem.py` | 623 | OCR storage |
| `storage/init_schemas.py` | `core/storage/init_schemas.py` | 418 | Schema bootstrap |
| `storage/lance_iceberg.py` | `core/storage/lance_iceberg.py` | 603 | Lance + Iceberg backend |
| `storage/lancedb_cloud.py` | `core/storage/clients/lancedb_cloud.py` | 664 | `LanceDBCloudClient` ($100 credits) |
| `storage/curriculum_vectors.py` | `core/storage/curriculum_vectors.py` | 427 | Curriculum-specific vector search |
| `storage/__init__.py` | (delete — replaced by `core/storage/__init__.py` which already re-exports `SerialDatabaseExecutor`, `DuckDBClient`, `LanceDBClient`) | 110 | Old __init__.py re-exports from `..core.storage` (canonical-piggybacks) |
| `storage/README.md` | (delete) | 11 | Stale nav |

The new `core/storage/__init__.py` (existing, 29 lines) needs updating to
add re-exports for the migrated symbols: `CogneeConfig`, `DuckLakeConfig`,
`FalkorDBConfig`, `GarageConfig`, `LakehouseConfig`, `LanceDBConfig`,
`MemgraphConfig`, `PlanetScaleConfig`, `StorageConfig`, `StorageBackend`,
`StorageManager`, `DuckLakeClient`, `DuckLakeSnapshot`,
`DuckLakeOCRStorage`, `LanceIcebergBackend`, `LanceIcebergClient`,
`LanceTableInfo`, `LanceDBCloudClient`, `LanceDBCloudConfig`,
`CurriculumVectorSearch`, `get_config`, `reset_config`,
`get_storage_backend`, `get_storage_manager`, `get_ducklake_backend`.

### Part C — Update 3 test files

Update imports from `oideachais.storage.X` to `oideachais.core.storage.X`:

| File | Old | New |
|:--|:--|:--|
| `tests/conftest.py:258` | `from oideachais.storage.lancedb_cloud import CircuitBreaker` | `from oideachais.core.storage.clients.lancedb_cloud import CircuitBreaker` |
| `tests/dlt_sources/test_integration.py:282,317` | `from oideachais.storage.lancedb_cloud import (...)` | `from oideachais.core.storage.clients.lancedb_cloud import (...)` |
| `tests/storage/test_lancedb_cloud.py:227,333,345,371,380,388,396` | `from oideachais.storage.lancedb_cloud import (...)` | `from oideachais.core.storage.clients.lancedb_cloud import (...)` |

After migration, `sruth/oideachais/tests/storage/` may either stay as
the test home for lancedb_cloud tests OR be moved to
`tests/core/storage/`. This change keeps it at `tests/storage/` to
minimize churn — a follow-up doc-only change can rename it.

### Part D — Update openspec spec references

Update `openspec/specs/oideachais-pipeline/spec.md`:
- Line 166: `sruth/oideachais/storage/ducklake_client.py` → `sruth/oideachais/core/storage/clients/ducklake.py`
- Lines 869-870: same path updates for `ducklake_client.py` and `lancedb_cloud.py`
- Line 912: `sruth/oideachais/storage/` → `sruth/oideachais/core/storage/`

Update `openspec/changes/refactor-quadrants-to-sruth/proposal.md:182`:
- Replace `sruth/oideachais/storage/` with `sruth/oideachais/core/storage/`

### Part E — Delete legacy directories

```bash
git rm -r sruth/oideachais/dagster_assets/
git rm -r sruth/oideachais/storage/
```

## Impact

- **LOC moved:** 5,646 (`dagster_assets/` 1,796 + `storage/` 5,557 + `__init__` re-exports 91)
- **LOC deleted (dead):** 1,544 (3 dead modules in `dagster_assets/` + 2 init/README files)
- **Net LOC impact:** -1,544 (dead code removed); 5,646 migrated to canonical homes
- **Files moved:** 11 (2 dagster asset modules + 9 storage files)
- **Files deleted:** 5 (3 dead modules + 2 init/README)
- **Test imports updated:** 11 (across 3 test files)
- **Spec refs updated:** 5 (1 line in `oideachais-pipeline/spec.md` × 4 references + 1 line in `refactor-quadrants-to-sruth/proposal.md`)
- **Risk:** medium — non-trivial file moves + multi-file spec ref updates + Dagster asset import path changes; validated via `from sruth.oideachais.dagster_defs.definitions import defs` (5 sensor groups + 18 sensors + migrated asset modules)

## Validation Gates

```bash
openspec validate oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets --strict
python -c "import sruth.oideachais; print('OK')"
python -c "from sruth.oideachais.dagster_defs.assets.model_conversion import model_conversion_assets, hf_models_downloaded, gguf_qwen2_5_math_7b, gguf_uccix_13b; print('OK')"
python -c "from sruth.oideachais.dagster_defs.assets.asset_generation import asset_generation_assets, image_prompts_designed; print('OK')"
python -c "from sruth.oideachais.core.storage import SerialDatabaseExecutor, DuckDBClient, LanceDBClient, CogneeConfig, DuckLakeConfig, StorageManager; print('OK')"
python -c "from sruth.oideachais.core.storage.clients.ducklake import DuckLakeClient; print('OK')"
python -c "from sruth.oideachais.core.storage.clients.lancedb_cloud import LanceDBCloudClient, CircuitBreaker, EmbeddingBatch, LanceDBCloudConfig; print('OK')"
python -c "from sruth.oideachais.core.storage.curriculum_vectors import CurriculumVectorSearch; print('OK')"
grep -rn "from sruth.oideachais.dagster_assets\|from oideachais.dagster_assets\|from sruth.oideachais.storage\.[a-z_]" sruth/ infrastructure/ apps/ web/ tests/ --include="*.py"  # MUST return 0
mise run lint:skills  # 123/123
```

## References

- Phase 2A investigation report (subagent task `ses_0ff5ad393ffeAWtFLnCQRG0JEJ`)
- `dagster_defs/definitions.py:165-181` — guarded try/except for `dagster_assets`
- `core/storage/__init__.py:13-18` — current canonical re-exports
- `AGENTS.md:97-105` — canonical surface routing table
- `dg.toml:15` — Dagster module_name `oideachais.dagster_defs.definitions`
