## Why

The README identity section (156 lines, hand-edited, lines 312–471 of `README.md`) references three family surnames — **Lyons** (via Uí Liatháin), **Conroy** (via Delbhna Tír Dhá Locha), and **Deacy** (via Eamonn Deacy Park) — and six supporting Gemini Deep Research PDFs at `leabharlann/gemini_deep_research/culture/`. None of the cited claims are currently queryable by agents, and three corroborating Wikipedia articles have not been ingested anywhere in the platform.

This change establishes the **6th domain** (`culture`) in the cross-domain-registry, the **6th Cognee dataset** (`culture_heritage`), a new BAML extraction schema tuned for cultural-heritage claim extraction, a new v1 CocoIndex App that embeds those claims into LanceDB, a Cognee cognify pass that builds the knowledge graph with cross-dataset edges, and four new Dagster assets that wire the full pipeline into the existing data-plane UI.

The change deliberately does NOT auto-sync the README identity section (per user preference — the README stays hand-edited so the prose is a personal expression, not a database view).

## What changes

**New files (13):**

- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/{ui_liathain,delbhna_tir_dha_locha,eamonn_deacy_park}-wikipedia.md` — 3 Obsidian-style clippings following the `deisi-wikipedia.md` precedent.
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_{ui_liathain,delbhna,eamonn_deacy_park}.json` — 3 JSON fixtures for `lookup_wikipedia()` consumption.
- `sruth/oideachais/baml_src/culture_extraction.baml` — 1 BAML file defining `CultureHeritageClaim` + `ExtractCultureClaims`.
- `sruth/oideachais/cocoindex_flows/culture_heritage_embedding.py` — 1 v1 CocoIndex App (12th in the platform).
- `sruth/oideachais/cognee_integration/culture_cognify.py` — 1 Cognee cognify pass for the `culture_heritage` dataset.
- `sruth/oideachais/dagster_defs/assets/culture_heritage_assets.py` — 1 Dagster asset module with 4 assets + 1 asset check.
- `openspec/changes/ingest-culture-heritage/specs/{cross-domain-registry,oideachais-leabharlann,celtic-asset-generation}/spec.md` — 3 spec deltas.

**Edited files (4):**

- `sruth/oideachais/sources.yaml` — 6 new entries under `domain: culture, nation: ie`.
- `sruth/oideachais/STATUS.md` — new row in the BAML × DLT × Dagster × CocoIndex matrix.
- `.erk/docs/agent/index.md` — link to the new culture subtree.
- `openspec/specs/cross-domain-registry/spec.md` — NEW spec (the cross-domain-registry capability did not yet exist as a top-level spec; it is created by this change as the canonical home for the 8-nation × 7-domain contract).

**Untouched:**

- `README.md` (stays hand-edited, stays unstaged).
- The 7 pre-existing unstaged changes from the prior session.
- The 6 PDFs under `leabharlann/gemini_deep_research/culture/` (no move).

## Impact

- **Additive only.** No files are renamed or deleted.
- **BAML client regeneration:** `baml-cli generate` regenerates the `baml_client/` Python package; downstream consumers (the new `culture_heritage_extract` asset) are bound at import time.
- **Cross-domain effect:** adds 6 new asset keys under `ie.culture.*`. Asset key collisions are guarded by the `cross-domain-registry` spec.
- **Cognee dataset:** introduces a 6th dataset (`culture_heritage`) alongside `oideachais`, `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`, `site_analysis`, `official_media`, `author_archive`. The new dataset enables cross-dataset edges to `oideachais` and `leabharlann`.
- **No front-end surface change.** No new TanStack routes, no new Convex functions, no new Tuatha quest.

## Non-goals

- No new front-end surface.
- No x402 or crypteolas changes.
- No new Tuatha MMO quest (cross-dataset edges MAY feed future quests, but no quest is in this change).
- No README auto-sync (the 156-line identity section remains hand-edited).