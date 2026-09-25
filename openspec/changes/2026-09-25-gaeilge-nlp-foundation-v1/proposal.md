# Change: Irish NLP Foundation (Phase 1 of the 5-phase Celtic pipeline overhaul)

## Why

This is **Phase 1** of the 5-phase × 10-stage Celtic + multilingual education pipeline overhaul (see `openspec/changes/2026-09-25-celtic-pipeline-finalization-v1/proposal.md` §3 for the umbrella).

Cianfhoghlaim has 8 entry-points for Celtic-language content (BAML, CocoIndex, DLT, Dagster, MotherDuck, marimo, observability, agents), but the **Irish (Gaeilge) foundation is fragmented across 4+ files** with no single source-of-truth for the canonical `CelticLanguage` enum, no hardened caighdean standardisation pipeline, and no unified LC/JC Gaeilge syllabus extraction. The ciancheiltis sister repo (`/Users/cianmacandeisigh/dev/ciancheiltis`) carries 12-model teanga registry + 6 Celtic-language ADK agents, but the wholesale-copy into cianfhoghlaim proper has never been done.

Phase 1 closes these 10 specific gaps:

### Gaps this phase closes
1. **3+ duplicate `CelticLanguage` enums** (`baml_src/celtic/sources.baml`, `baml_src/celtic/curriculum/celtic_curriculum.baml`, `baml_extracts_education/_cross/biep_subject.baml`, `gemini_hackathon` mirror) — no single source of truth
2. **`caighdean_standardize.py`** (539 LOC) lacks BAML wrapper for use as a pre-extraction transformer
3. **LC + JC Gaeilge stage templates** (`ireland_lc_stage.baml`, `ireland_jc_stage.baml`) don't call caighdean_standardize pre-extraction
4. **`grammar_patterns.baml`** doesn't enumerate the 9 Irish séimhiú mutations as a first-class enum
5. **5 DLT sources missing** for NCCA LC Gaeilge (OL/HL) + JC Gaeilge (T1/T2) + Primary Gaeilge
6. **gaeilge_embedding.py** is a stub — uses old `lance.connect` API not the v1 factory
7. **No Dagster assets** for the 5 new Gaeilge sources
8. **No MotherDuck Dive** for the full Gaeilge curriculum (only `gaeilge_full_curriculum_dive.py` doesn't exist yet)
9. **No marimo notebook** as the operator-facing Gaeilge dashboard
10. **No wholesale-copies** from the ciancheiltis sister (teanga_registry.py + 5 BAML extractors)

## What changes (10 stages)

### Stage 1.1 — Unify `CelticLanguage` enum
- Canonical home: `baml_src/celtic/sources.baml` (already has 8 entries: `GA, GD, CY, GV, KW, EN, SCO, ULS`).
- Make `baml_src/celtic/curriculum/celtic_curriculum.baml` re-import it (BAML `enum X from "..."` syntax).
- Same for `baml_extracts_education/_cross/biep_subject.baml` (mirror via gemini_hackathon wholesale-copy).

### Stage 1.2 — Extend `grammar_patterns.baml` with `IrishMutation` enum
- Add 9-value `IrishMutation {S_FADA, S_NO_FADA, URÚ, ECLIPSIS_L, ECLIPSIS_N, ECLIPSIS_T, ECLIPSIS_D, ECLIPSIS_G, NO_MUTATION}` enum.
- Wire into `ExtractCelticGrammar` + `DocumentMutationTriggers`.

### Stage 1.3 — Harden `caighdean_standardize.py`
- Add wikitext extraction (`<ref>`, `{{ }}`, `[[ ]]` strips)
- Add TN6 hyperlink stripping
- Add Teanglann audio link capture
- Ship `baml_src/celtic/standardize.baml` with `StandardizeIrish` + `StandardizeScottishGaelic` + `StandardizeManx` BAML extractors

### Stage 1.4 — Wire `ireland_lc_stage.baml`
- Call `StandardizeIrish` pre-extraction on `pdf_text` arg
- Record before/after transformation in `LCSyllabusDocument.dialect_variants` field

### Stage 1.5 — Wire `ireland_jc_stage.baml`
- Same as 1.4 for the JC Gaeilge (T1/T2) syllabus

### Stage 1.6 — Build `gaeilge_embedding.py` v1 conformance App
- Use `celtic_caighdean` post-processor (callable Python function wrapping `caighdean_standardize.CaighdeanTransform`)
- Emit to `LanceDB cianfhoghlaim.celtic.gaeilge.{lc, jc, primary, aistear, senior}_chunks`

### Stage 1.7 — 5 DLT sources for NCCA syllabus
- `dlt_sources/education/ireland/british_isles/lc_gaeilge_ol/`
- `dlt_sources/education/ireland/british_isles/lc_gaeilge_hl/`
- `dlt_sources/education/ireland/british_isles/jc_gaeilge_t1/`
- `dlt_sources/education/ireland/british_isles/jc_gaeilge_t2/`
- `dlt_sources/education/ireland/british_isles/primary_gaeilge/`
- Each calls `ExtractCurriculumSyllabus` BAML function

### Stage 1.8 — Dagster assets for 5 new sources
- `orchestration/defs/2_materials/ireland_education/gaeilge_assets.py`
- 15 assets (3 per source: ingested / extractions / embeddings)
- Group names: `1_ingestion_ireland_gaeilge`, `2_materials_ireland_gaeilge_extractions`, `3_model_lifecycle_ireland_gaeilge_embeddings`

### Stage 1.9 — MotherDuck Dive + marimo
- `motherduck/dives/gaeilge_full_curriculum_dive.py` (per-subject + per-stage breakdown)
- `notebooks/36_gaeilge_full_curriculum.py` (the Gaeilge operator dashboard — analogous to `celtic_languages.py` but Irish-only with more depth)

### Stage 1.10 — Wholesale-copy + tests + verify + archive
- Wholesale-copy `meaisinfhoghlaim/models/teanga_registry.py` from ciancheiltis (the 12-model teanga registry)
- Wholesale-copy `dlt_sources/language/clarin.py` from ciancheiltis (CLARIN VLO loader)
- Run `bash scripts/verify.sh` (8/8 ticks)
- Run `mise run lint:registry`
- Run `openspec validate --strict`
- Archive this change

## Impact

- **Affected code**: ~30 new files (10 BAML functions + 5 DLT sources + 1 Dagster asset file + 1 MotherDuck Dive + 1 marimo notebook + 1 standardize.baml + 1 IrishMutation extension + 1 wholesale-copied teanga_registry.py + 1 wholesale-copied clarin.py + ~10 modifications)
- **Affected specs**: NEW `celtic-language-pipeline` (added by Phase 5.9 — not by this change)

## Out of scope (deferred to later phases)

- HuggingFace dataset integration (Phase 2)
- CLARIN-UK VLO + institutional corpora (Phase 3)
- Welsh + Manx + Cornish + Breton (Phase 4)
- Sister-repo wholesale-copy verification (Phase 5)
- Tuatha / Bonneagar / Cognee work
