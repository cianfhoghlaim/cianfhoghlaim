# bilingual-celtic-asset-pipeline Specification

## Purpose
`bilingual-celtic-asset-pipeline` is the contract for the 6-language
asset generation pipeline that turns canonical curriculum concepts
into per-language visual assets. Each of the 6 Celtic languages
(gaeilge + cymraeg + gaidhlig + gaelg + kernewek + brezhoneg) has its
own BAML `GenerateXxxAsset` function + its own CocoIndex flow + its own
LanceDB table.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change
(Plan 7 of `openspec/plans/2026-10-01-convergence-saga-v1.md`).

## ADDED Requirements

### Requirement: 6 BAML GenerateXxxAsset functions (one per Celtic language)

The system MUST provide 6 BAML asset-generation functions in
`baml_src/british_isles/_cross/asset_generation.baml` (one per Celtic
language):

1. `GenerateIrishAsset(prompt, role, language="ga")` — Irish (gaeilge)
2. `GenerateWelshAsset(prompt, role, language="cy")` — Welsh (cymraeg)
3. `GenerateScottishGaelicAsset(prompt, role, language="gd")` — Scottish Gaelic (gaidhlig)
4. `GenerateManxAsset(prompt, role, language="gv")` — Manx (gaelg)
5. `GenerateCornishAsset(prompt, role, language="kw")` — Cornish (kernewek)
6. `GenerateBretonAsset(prompt, role, language="br")` — Breton (brezhoneg)

Each function MUST return a typed `AssetRecord` with the canonical
fields: `asset_id`, `subject`, `language`, `title`, `prompt`, `palette_hex`,
`language_label`, `language_native_script`.

#### Scenario: Irish asset generated
- **WHEN** the operator runs `uv run python scripts/celtic_assets.py --lang gaeilge --prompt "An Irish round tower at sunset"`
- **THEN** `GenerateIrishAsset` is called via BAML
- **AND** the asset lands in `lance://media.image_gen_chunks_gaeilge`
- **AND** the marimo notebook at `notebooks/dashboards/gaeilge/asset_browser.py` shows it

### Requirement: 6 per-language CocoIndex flows + LanceDB tables

The system MUST provide 6 per-language CocoIndex flows (one per Celtic
language), each writing to its own LanceDB table:
- `cocoindex_flows/media/gaeilge/asset_index.py` → `media.image_gen_chunks_gaeilge`
- `cocoindex_flows/media/cymraeg/asset_index.py` → `media.image_gen_chunks_cymraeg`
- `cocoindex_flows/media/gaidhlig/asset_index.py` → `media.image_gen_chunks_gaidhlig`
- `cocoindex_flows/media/gaelg/asset_index.py` → `media.image_gen_chunks_gaelg`
- `cocoindex_flows/media/kernewek/asset_index.py` → `media.image_gen_chunks_kernewek`
- `cocoindex_flows/media/brezhoneg/asset_index.py` → `media.image_gen_chunks_brezhoneg`

Each flow conforms to the canonical R1-R4 conformance contract (per the
existing `cocoindex_flows/media/image_generation_flow.py` pattern).

#### Scenario: All 6 languages indexed in their own tables
- **WHEN** the operator runs `uv run python scripts/celtic_assets.py --all --prompt "An Irish round tower at sunset"`
- **THEN** 6 assets are generated in parallel (one per language)
- **AND** each asset lands in its own LanceDB table
- **AND** the marimo notebooks (one per language) can browse their respective tables

### Requirement: 6 per-language marimo asset browsers

The system MUST provide 6 per-language marimo asset browsers
(one per Celtic language) under `notebooks/dashboards/<lang>/asset_browser.py`.
Each browser MUST:
1. Query its language's LanceDB table via DuckLake SQL
2. Show the asset metadata + the OTel trace IDs (from Plan 5)
3. Link to the Cognee entity-asset graph (from Plan 6)

#### Scenario: Irish asset browser shows gaeilge assets
- **WHEN** the operator opens `notebooks/dashboards/gaeilge/asset_browser.py` in Marimo
- **THEN** the dashboard shows the gaeilge assets (from `media.image_gen_chunks_gaeilge`)
- **AND** clicking an asset expands to show the prompt (in gaeilge) + the OTel trace ID + the linked Cognee entities

### Requirement: CLI demo (all 6 languages in parallel)

The system MUST provide `scripts/celtic_assets.py` that can:
1. Generate one asset in one language (`--lang gaeilge --prompt "..."`)
2. Generate 1 asset in all 6 languages in parallel (`--all --prompt "..."`)
3. Show the timing + per-language results in a summary table

#### Scenario: All 6 languages generated in parallel
- **WHEN** the operator runs `uv run python scripts/celtic_assets.py --all --prompt "An Irish round tower at sunset"`
- **THEN** 6 assets are generated in parallel (one per Celtic language)
- **AND** the output shows a summary table: `gaeilge → 169ms / cy → 145ms / gd → 178ms / gv → 156ms / kw → 162ms / br → 171ms`
- **AND** all 6 assets land in their respective LanceDB tables
