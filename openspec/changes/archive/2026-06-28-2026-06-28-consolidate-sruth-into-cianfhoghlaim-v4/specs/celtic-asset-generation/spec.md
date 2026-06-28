# Spec Delta — celtic-asset-generation

## ADDED Requirements

### Requirement: 4 Successive Independent Asset Gen Pipelines (v4)

The system SHALL organise educational asset generation under 4 successive INDEPENDENT pipelines at `cianfhoghlaim/assets/asset_generation/`:

1. `official_documents/` — extracts assets from syllabus + exam papers + marking schemes (BAML + CocoIndex OCR-aware)
2. `subject_assets/` — generates subject-specific 3D assets (chemistry lab equipment + geography landscape + biology specimens + physics apparatus) via Qwen-Image-2512 / Z-Image-Turbo / FLUX.2-klein-9B
3. `language_assets/` — generates language-specific assets (gaeilge + cymraeg + gaidhlig + gaelg + kernewek + brezhoneg) via teanglann + gaois
4. `exporters/` — exports to Babylon.js + Godot + Unity + Unreal via crypteolas pipelines

Each pipeline is independently runnable from Dagster — they are NOT chained as a single pipeline.

#### Scenario: Independent activation

- **WHEN** Dagster materialises `assets/asset_generation/official_documents/syllabus.py`
- **THEN** the syllabus extraction runs alone, writing to `ducklake://oideachais.assets.official_documents.syllabus`
- **AND** subject_assets / language_assets / exporters do NOT trigger
- **AND** the four pipelines share no DAG dependencies

### Requirement: Asset Generation Source Schema Provisional (v4)

The asset generation source schema (`cianfhoghlaim/assets/asset_generation/{official_documents,subject_assets,language_assets,exporters}/`) SHALL be considered provisional — refactored after Plan 1 (Ireland + leabharlann) informs the best CocoIndex + DLT + DuckDB + DuckLake + Lance patterns for multi-nation + multi-language + multimodal processing. The system SHALL include a `README.md` at `cianfhoghlaim/assets/asset_generation/` that states this provisional status and lists the open refactor questions.

#### Scenario: Refactor notice

- **WHEN** a developer reads `cianfhoghlaim/assets/asset_generation/README.md`
- **THEN** the README states the schema is provisional and lists the open refactor questions
- **AND** the README cross-references `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/proposal.md`