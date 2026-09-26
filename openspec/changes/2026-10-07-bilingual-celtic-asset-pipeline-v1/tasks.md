# Tasks: 2026-10-07-bilingual-celtic-asset-pipeline-v1

## 1. Group A — BAML contracts

- [x] **A1** `baml_src/british_isles/_cross/asset_generation.baml` — the 6 GenerateXxxAsset functions (one per Celtic language) + the AssetRecord type

## 2. Group B — CocoIndex flows (per language)

- [x] **B1** `cocoindex_flows/media/gaeilge/asset_index.py` — the Irish asset index flow (writes to `media.image_gen_chunks_gaeilge`)
- [x] **B2** `cocoindex_flows/media/cymraeg/asset_index.py` — the Welsh asset index flow
- [x] **B3** `cocoindex_flows/media/gaidhlig/asset_index.py` — the Scottish Gaelic asset index flow
- [x] **B4** `cocoindex_flows/media/gaelg/asset_index.py` — the Manx asset index flow
- [x] **B5** `cocoindex_flows/media/kernewek/asset_index.py` — the Cornish asset index flow
- [x] **B6** `cocoindex_flows/media/brezhoneg/asset_index.py` — the Breton asset index flow

## 3. Group C — Marimo notebooks (per language)

- [x] **C1** `notebooks/dashboards/gaeilge/asset_browser.py` — Irish asset browser
- [x] **C2** `notebooks/dashboards/cymraeg/asset_browser.py` — Welsh asset browser
- [x] **C3** `notebooks/dashboards/gaidhlig/asset_browser.py` — Scottish Gaelic asset browser
- [x] **C4** `notebooks/dashboards/gaelg/asset_browser.py` — Manx asset browser
- [x] **C5** `notebooks/dashboards/kernewek/asset_browser.py` — Cornish asset browser
- [x] **C6** `notebooks/dashboards/brezhoneg/asset_browser.py` — Breton asset browser

## 4. Group D — CLI demo

- [x] **D1** `scripts/celtic_assets.py` — CLI: `--lang gaeilge` generates all 6 variants in parallel

## 5. Group E — Spec materialisation

- [x] **E1** `openspec/specs/bilingual-celtic-asset-pipeline/spec.md` — 4 Requirements

## 6. Group F — Verification + commit + push

- [x] **F1** `uv run python scripts/celtic_assets.py --lang gaeilge --prompt "An Irish round tower at sunset"` runs end-to-end
- [x] **F2** All 6 marimo notebooks parse + import
- [x] **F3** `bunx openspec validate 2026-10-07-bilingual-celtic-asset-pipeline-v1 --strict` passes
- [x] **F4** `git add -A && git commit && git push`
- [x] **F5** Create PR via `gh pr create`
