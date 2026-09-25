# Tasks: Welsh + Manx + Celtic Siblings HF Integration (Phase 4)

## Stage 4.1 — Welsh HF (techiaith ASR/TTS) → welsh_hf.py

- [ ] 4.1.1. New: `dlt_sources/education/wales/british_isles/__init__.py` (package marker)
- [ ] 4.1.2. New: `dlt_sources/education/wales/british_isles/welsh_hf.py` wrapping `techiaith/banc-trawsgrifiadau-bangor` + `techiaith/commonvoice_18_0_cy` + `techiaith/bu-tts-cy-en` + `techiaith/YouTube-Subtitles` → `celtic.welsh_hf.{asr, tts}`
- [ ] 4.1.3. Verify: smoke import

## Stage 4.2 — Welsh eval → extend vernacular_languages.baml

- [ ] 4.2.1. Extend `baml_src/british_isles/_cross/vernacular_languages.baml` with `ExtractWelshMathReasoning` + `ExtractWelshCausalReasoning` + `ExtractWelshNLI` + `ExtractMacsenIntent` + `ExtractWelshCEFR` (5 BAML functions for techiaith eval datasets)
- [ ] 4.2.2. Verify: `baml-cli generate` produces the 5 functions
- [ ] 4.2.3. New: `dlt_sources/education/wales/british_isles/welsh_eval.py` wrapping `techiaith/mgsm_cy` + `COPA-cy` + `wnli-cy` + `macsen_intent_parsing` + `UniversalCEFR/learn_welsh_cy` → `celtic.welsh_eval`

## Stage 4.3 — Welsh CEFR + institutions

- [ ] 4.3.1. New: `dlt_sources/education/wales/british_isles/welsh_cefr.py` wrapping `cardiffnlp/welsh-cefr` + `BethanAmy123/CEFR_Welsh_gogledd` + `BethanAmy123/WelshCEFR-South` + `BethanAmy123/WelshCEFR-North` → `celtic.welsh_cefr`
- [ ] 4.3.2. New: `dlt_sources/education/wales/british_isles/welsh_institutional.py` wrapping CorCenCC + Bangor Siarad + Welsh Government parallel (`gov.wales` + `cymraeg.gov.wales`)
- [ ] 4.3.3. New: `baml_src/british_isles/wales/_shared/institutional_extract.baml` with `ExtractCorCenCCEntry` + `ExtractWelshGovDocument`

## Stage 4.4 — Welsh parallel

- [ ] 4.4.1. New: `dlt_sources/education/wales/british_isles/welsh_parallel.py` wrapping 10 techiaith TM datasets + 6 locailabs datasets → `celtic.welsh_parallel`
- [ ] 4.4.2. Verify: smoke import

## Stage 4.5 — Manx + cross-Celtic

- [ ] 4.5.1. New: `dlt_sources/education/isle_of_man/british_isles/manx_hf.py` wrapping `k-mktr/manx_gaelic_nt_gv` + `manxaneletso/Chats_Memory` → `celtic.manx_hf`
- [ ] 4.5.2. New: `dlt_sources/celtic_cross/__init__.py` (new sibling tree)
- [ ] 4.5.3. New: `dlt_sources/celtic_cross/cross_celtic_pretrain.py` wrapping `Jendersen/welsh-breton-cornish-filtered-n-readied` + `JayJayThrowThrow/celtic-wiki-mix` + `celtic-wiki-mix-clean` → `celtic.cross_celtic_pretrain`

## Stage 4.6 — Cornish + Breton

- [ ] 4.6.1. New: `dlt_sources/breton_cornish/british_isles/__init__.py` (package marker)
- [ ] 4.6.2. New: `dlt_sources/breton_cornish/british_isles/cornish_hf.py` wrapping `CK0607/CORNISH2ENGLISH-ALPACA` + `Jendersen/cornish_english_translation` + Mozilla CV Cornish 27.0 → `celtic.cornish_hf`
- [ ] 4.6.3. New: `dlt_sources/breton_cornish/british_isles/breton_hf.py` wrapping 60+ Bretagne datasets (Banque_Sonore, UD_Breton-KEB, Prosody_Breton, fineweb-2_raw_breton, archive_sonores_1..30, PDF_en_breton, mozilla CV 17.0 br) → `celtic.breton_hf`
- [ ] 4.6.4. Strengthen existing `baml_extracts_education/player_assessment.baml` — replace the `KW @description("Kernewek/Cornish (TODO)")` placeholder with the real CornishLanguage `enum KW` extracted from `jendersen/cornish_english_translation`
- [ ] 4.6.5. Same for `BR` (Breton) placeholder

## Stage 4.7 — CocoIndex: strengthen + cross-Celtic

- [ ] 4.7.1. Strengthen existing `cocoindex_flows/vernacular/welsh_embedding.py` — add the HF integration layer (calls the DLT sources)
- [ ] 4.7.2. Same for `manx_embedding.py`
- [ ] 4.7.3. New: `cocoindex_flows/celtic/celtic_wiki_mix_embedding.py` (the `JayJayThrowThrow/celtic-wiki-mix` embed)
- [ ] 4.7.4. Strengthen existing `cornish_embedding.py` + `breton_embedding.py`

## Stage 4.8 — DLT consolidation

- [ ] 4.8.1. Register all 7 new sources (`welsh_hf`, `welsh_eval`, `welsh_cefr`, `welsh_institutional`, `welsh_parallel`, `manx_hf`, `cornish_hf`, `breton_hf`, `cross_celtic`) to the canonical registry

## Stage 4.9 — Dagster

- [ ] 4.9.1. New: `orchestration/defs/2_materials/vernacular/__init__.py` (extend aggregator)
- [ ] 4.9.2. New: `orchestration/defs/2_materials/vernacular/hf_vernacular_assets.py` (21 assets: 3 per source × 7 sources)

## Stage 4.10 — Per-phase verify + archive

- [ ] 4.10.1. `bash scripts/verify.sh` → 8/8
- [ ] 4.10.2. `mise run lint:registry` → 0 hardcoded model strings
- [ ] 4.10.3. `openspec validate --strict` → valid
- [ ] 4.10.4. `uv run pytest tests/vernacular/test_phase15_hf_vernacular_pipelines.py` (new test) → pass
- [ ] 4.10.5. `openspec archive 2026-09-25-celtic-hf-vernacular-v1 -y --skip-specs`
- [ ] 4.10.6. `git push origin main`
