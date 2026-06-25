## ADDED Requirements

### Requirement: Round 11 Phase 2B — Legacy Storage + Dagster Asset Migration (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11
phase 2B (executed 2026-06-25) migrated 11 unique legacy files (5,646 LOC)
from the deprecated `sruth/oideachais/dagster_assets/` and
`sruth/oideachais/storage/` directories to their canonical homes in
`sruth/oideachais/dagster_defs/assets/` and
`sruth/oideachais/core/storage/{clients,config}/`, while removing 5 dead
files (1,544 LOC).

The canonical surfaces after this change:

| Legacy (removed) | Canonical (target) | LOC |
|:--|:--|--:|
| `sruth/oideachais/dagster_assets/model_conversion.py` | `sruth/oideachais/dagster_defs/assets/model_conversion.py` | 374 |
| `sruth/oideachais/dagster_assets/asset_generation.py` | `sruth/oideachais/dagster_defs/assets/asset_generation.py` | 281 |
| `sruth/oideachais/dagster_assets/{grammar_validation,pdf_benchmark,syntactic_parsing}.py` | (deleted — 0 importers) | 1,433 |
| `sruth/oideachais/storage/config.py` | `sruth/oideachais/core/storage/config.py` | 359 |
| `sruth/oideachais/storage/connections.py` | `sruth/oideachais/core/storage/connections.py` | 691 |
| `sruth/oideachais/storage/ducklake.py` | `sruth/oideachais/core/storage/ducklake.py` | 780 |
| `sruth/oideachais/storage/ducklake_client.py` | `sruth/oideachais/core/storage/clients/ducklake.py` | 882 |
| `sruth/oideachais/storage/ducklake_filesystem.py` | `sruth/oideachais/core/storage/clients/ducklake_filesystem.py` | 623 |
| `sruth/oideachais/storage/init_schemas.py` | `sruth/oideachais/core/storage/init_schemas.py` | 418 |
| `sruth/oideachais/storage/lance_iceberg.py` | `sruth/oideachais/core/storage/lance_iceberg.py` | 603 |
| `sruth/oideachais/storage/lancedb_cloud.py` | `sruth/oideachais/core/storage/clients/lancedb_cloud.py` | 664 |
| `sruth/oideachais/storage/curriculum_vectors.py` | `sruth/oideachais/core/storage/curriculum_vectors.py` | 427 |

#### Scenario: A developer adds a new HF → GGUF conversion asset

- **WHEN** any caller needs to add a new HuggingFace → GGUF model conversion for llama-swap
- **THEN** they MUST add a new `@asset` function to `sruth/oideachais/dagster_defs/assets/model_conversion.py` (which contains `hf_models_downloaded`, `gguf_qwen2_5_math_7b`, `gguf_uccix_13b`, etc.)
- **AND** register it in the `model_conversion_assets` list at the bottom of the file
- **AND** NOT add it to the deleted `sruth/oideachais/dagster_assets/model_conversion.py`

#### Scenario: A developer adds a new study asset generation asset

- **WHEN** any caller needs to add a new BAML-driven image generation asset (fibo_configs_built, study_assets_rendered, study_assets_published)
- **THEN** they MUST add a new `@asset` function to `sruth/oideachais/dagster_defs/assets/asset_generation.py`
- **AND** register it in the `asset_generation_assets` list at the bottom of the file
- **AND** NOT add it to the deleted `sruth/oideachais/dagster_assets/asset_generation.py`

#### Scenario: A developer uses the multi-backend storage config

- **WHEN** any caller needs the multi-backend `StorageConfig` (CogneeConfig, DuckLakeConfig, FalkorDBConfig, GarageConfig, LakehouseConfig, LanceDBConfig, MemgraphConfig, PlanetScaleConfig)
- **THEN** they MUST import from `sruth.oideachais.core.storage.config` (re-exported via `sruth.oideachais.core.storage`)
- **AND** NOT import from `sruth.oideachais.storage.config`

#### Scenario: A developer uses a DuckLake client

- **WHEN** any caller needs the DuckLake postgres-catalog + Garage-S3 client (`DuckLakeClient`)
- **THEN** they MUST import from `sruth.oideachais.core.storage.clients.ducklake`
- **AND** NOT import from `sruth.oideachais.storage.ducklake_client`

#### Scenario: A developer uses the LanceDB Cloud client

- **WHEN** any caller needs the managed LanceDB Cloud integration (`LanceDBCloudClient`, `LanceDBCloudConfig`, `EmbeddingBatch`, `CircuitBreaker`)
- **THEN** they MUST import from `sruth.oideachais.core.storage.clients.lancedb_cloud`
- **AND** NOT import from `sruth.oideachais.storage.lancedb_cloud`

#### Scenario: A developer uses curriculum vector search

- **WHEN** any caller needs the `CurriculumVectorSearch` BGE-M3-powered semantic search over curriculum content
- **THEN** they MUST import from `sruth.oideachais.core.storage.curriculum_vectors`
- **AND** NOT import from `sruth.oideachais.storage.curriculum_vectors`

#### Scenario: The canonical surface contract is preserved

- **GIVEN** `openspec/changes/oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets` is archived
- **WHEN** the Dagster Definitions load (`sruth.oideachais.dagster_defs.definitions`)
- **THEN** `defs.assets` MUST contain `model_conversion_assets` and `asset_generation_assets` (verified via `from sruth.oideachais.dagster_defs.assets.model_conversion import model_conversion_assets; assert len(model_conversion_assets) >= 8`)
- **AND** `defs.assets` MUST contain `asset_generation_assets` with ≥ 4 assets
- **AND** `sruth/oideachais/core/storage/__init__.py` MUST re-export all 25 newly-migrated symbols (verified via `from sruth.oideachais.core.storage import (CogneeConfig, DuckLakeConfig, StorageManager, DuckLakeClient, LanceDBCloudClient, CurriculumVectorSearch)`)
- **AND** the legacy `sruth/oideachais/dagster_assets/` and `sruth/oideachais/storage/` directories MUST NOT exist (verified via `not os.path.exists(...)`)

#### Scenario: No residual references after migration

- **WHEN** any developer runs `grep -rn "from sruth.oideachais.dagster_assets\|from oideachais.dagster_assets\|from sruth.oideachais.storage\.[a-z_]\|from oideachais.storage\.[a-z_]" --include="*.py" --include="*.md"`
- **THEN** zero matches MUST appear outside `openspec/changes/archive/` (the only residual refs are in archived openspec change metadata, which is intentional)
