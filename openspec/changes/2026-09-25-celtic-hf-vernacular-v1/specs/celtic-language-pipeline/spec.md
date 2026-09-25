## ADDED Requirements

### Requirement: cv-1 — Welsh HF DLT source

The `dlt_sources/education/wales/british_isles/welsh_hf.py` file MUST wrap 4 techiaith HuggingFace datasets (banc-trawsgrifiadau-bangor + commonvoice_18_0_cy + bu-tts-cy-en + YouTube-Subtitles).

#### Scenario: welsh_hf source importable

- **WHEN** an operator runs `uv run python -c "from dlt_sources.education.wales.british_isles.welsh_hf import welsh_hf_source; print('OK')"`
- **THEN** the output MUST be `OK`

### Requirement: cv-2 — 5 Welsh eval BAML functions

The `baml_src/british_isles/_cross/vernacular_languages.baml` file MUST extend `ExtractWelshSubjectSpec` with 5 eval functions: `ExtractWelshMathReasoning`, `ExtractWelshCausalReasoning`, `ExtractWelshNLI`, `ExtractMacsenIntent`, `ExtractWelshCEFR`.

#### Scenario: 5 Welsh eval functions

- **WHEN** an operator runs `uv run python -c "from baml_client.sync_client import b; print([n for n in dir(b) if 'ExtractWelsh' in n])"`
- **THEN** the output MUST include at least 5 functions (the subject spec + 4 eval extractors; MacsenIntent is its own prefix)

### Requirement: cv-3 — 7 new HF DLT sources

The cianfhoghlaim DLT pipeline MUST add 7 new HF sources: `welsh_hf`, `welsh_eval`, `welsh_cefr`, `welsh_institutional`, `welsh_parallel`, `manx_hf`, `cornish_hf`, `breton_hf`, `cross_celtic`.

#### Scenario: 7+ sources registered

- **WHEN** an operator runs `find dlt_sources -name "*_hf.py" -o -name "*_cefr.py" -o -name "*_parallel.py" | wc -l`
- **THEN** the output MUST be ≥ 7

### Requirement: cv-4 — Cornish + Breton KW/BR enum populated

The `baml_extracts_education/player_assessment.baml` file MUST replace the `KW @description("Kernewek/Cornish (TODO)")` and `BR @description("Brezhoneg/Breton (TODO)")` placeholders with real extracted enum values from `Jendersen/cornish_english_translation` + `Bretagne/UD_Breton-KEB`.

#### Scenario: KW + BR placeholders gone

- **WHEN** an operator runs `grep "TODO" baml_extracts_education/player_assessment.baml`
- **THEN** the output MUST be empty (or only reference other TODOs)

### Requirement: cv-5 — 21 Dagster vernacular HF assets

The `orchestration/defs/2_materials/vernacular/hf_vernacular_assets.py` file MUST provide 21 assets (3 per source × 7 sources).

#### Scenario: 21 assets

- **WHEN** an operator runs `uv run python -c "from orchestration.defs.vernacular.hf_vernacular_assets import ASSETS; print(len(ASSETS))"`
- **THEN** the output MUST be `≥ 21`

### Requirement: cv-6 — CocoIndex cross-Celtic mix App

The `cocoindex_flows/celtic/celtic_wiki_mix_embedding.py` App MUST embed the JayJayThrowThrow/celtic-wiki-mix + celtic-wiki-mix-clean datasets into LanceDB.

#### Scenario: celtic_wiki_mix App loads

- **WHEN** an operator runs `uv run python -c "from cocoindex_flows.celtic.celtic_wiki_mix_embedding import celtic_wiki_mix_embedding; print('OK')"`
- **THEN** the output MUST be `OK`
