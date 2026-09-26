# Change: 2026-10-07-bilingual-celtic-asset-pipeline-v1

## Why

The `baml_src/british_isles/_cross/vernacular_languages.baml` defines the
6 Celtic languages (gaeilge + cymraeg + gaidhlig + gaelg + kernewek +
brezhoneg) but no asset generation code exists for any of them.
The `media.image_gen_chunks` LanceDB table is monolingual EN.

The Tuatha British Isles MMO can't render a Welsh round tower or a
Scottish-Gaelic chemistry diagram because:
1. There's no per-language BAML asset-generation function
2. There are no per-language CocoIndex flows
3. There are no per-language LanceDB tables (everything goes to one shared table)
4. There are no per-language marimo notebooks for asset browsing

This is Plan 7 of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — new (~9 files)
- `baml_src/british_isles/_cross/asset_generation.baml` — the 6-language asset generation BAML
- `cocoindex_flows/media/gaeilge/{__init__,asset_index}.py` + 5 more per-language flows
- `notebooks/dashboards/gaeilge/asset_browser.py` + 5 more per-language marimo notebooks
- `scripts/celtic_assets.py` — the CLI demo (`--lang gaeilge` generates all 6 variants in parallel)

### Spec materialised
- `openspec/specs/bilingual-celtic-asset-pipeline/spec.md` — 4 Requirements

### Reference surfaces
- `baml_src/british_isles/_cross/vernacular_languages.baml` — the existing enum
- `cocoindex_flows/media/image_generation_flow.py` — the existing image-gen flow (reused as the pattern)
- `agents/adk/tools/image_generation.py` — the image-gen tool (Plan 2)
- `orchestration/assets/ducklake_maintenance.py` — the lakehouse bridge (Plan 5)

## What this does NOT ship
- Live translation pipeline for the 4 rarer languages (gaelg + kernewek + brezhoneg) — Irish + Welsh + Scottish Gaelic only at launch; the others are deferred to a follow-up once parallel corpus data is sourced
- Cross-language entity linking in Cognee (deferred — would unify the per-language graphs)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
