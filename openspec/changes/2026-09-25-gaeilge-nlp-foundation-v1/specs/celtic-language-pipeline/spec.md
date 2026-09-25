## ADDED Requirements

### Requirement: ip-1 — CelticLanguage enum unified

The 8-entry `CelticLanguage` enum MUST have a single canonical source of truth at `baml_src/celtic/sources.baml`. All other BAML files in `baml_src/celtic/`, `baml_src/celtic/curriculum/`, and `baml_extracts_education/_cross/biep_subject.baml` MUST import (not re-declare) this enum.

#### Scenario: zero duplicate CelticLanguage declarations

- **WHEN** an operator runs `grep -rE "^enum CelticLanguage " baml_src/ baml_extracts_education/ --include='*.baml'`
- **THEN** the output MUST be exactly 1 (the canonical declaration)

### Requirement: ip-2 — IrishMutation enum

The `baml_src/celtic/grammar_patterns.baml` file MUST define a 9-value `IrishMutation` enum (S_FADA, S_NO_FADA, URÚ, ECLIPSIS_L, ECLIPSIS_N, ECLIPSIS_T, ECLIPSIS_D, ECLIPSIS_G, NO_MUTATION).

#### Scenario: 9 mutations present

- **WHEN** an operator runs `grep -A12 "^enum IrishMutation" baml_src/celtic/grammar_patterns.baml`
- **THEN** the output MUST show all 9 enum values

### Requirement: ip-3 — caighdean standardiser hardened

The `cocoindex_flows/_shared/caighdean_standardize.py` module MUST add 3 new capabilities: wikitext extraction (ref/TN6 strip), Teanglann audio link capture, and the BAML wrapper `baml_src/celtic/standardize.baml` with `StandardizeIrish` + `StandardizeScottishGaelic` + `StandardizeManx` extractors.

#### Scenario: 3 standardize extractors reachable

- **WHEN** an operator runs `uv run python -c "from baml_client.sync_client import b; print([n for n in dir(b) if 'Standardize' in n])"`
- **THEN** the output MUST list 3 functions

### Requirement: ip-4 — LC + JC stage templates call caighdean

The `baml_src/_shared/templates/ireland_lc_stage.baml` + `ireland_jc_stage.baml` MUST call `StandardizeIrish` pre-extraction on the `pdf_text` arg and record the before/after transformation in `LCSyllabusDocument.dialect_variants`.

#### Scenario: dialect_variants populated

- **WHEN** an operator runs `uv run python -c "from baml_client.types import LCSyllabusDocument; print('dialect_variants' in LCSyllabusDocument.model_fields)"`
- **THEN** the output MUST be `True`

### Requirement: ip-5 — 5 NCCA syllabus DLT sources

The `dlt_sources/education/ireland/british_isles/` directory MUST contain 5 new DLT sources: `lc_gaeilge_ol`, `lc_gaeilge_hl`, `jc_gaeilge_t1`, `jc_gaeilge_t2`, `primary_gaeilge`.

#### Scenario: 5 sources importable

- **WHEN** an operator runs `ls dlt_sources/education/ireland/british_isles/ | grep gaeilge`
- **THEN** the output MUST list 5 directories/files

### Requirement: ip-6 — 15 Dagster Gaeilge assets

The `orchestration/defs/2_materials/ireland_education/gaeilge_assets.py` file MUST provide 15 assets (3 per source × 5 sources).

#### Scenario: 15 assets

- **WHEN** an operator runs `uv run python -c "from orchestration.defs.ireland_education.gaeilge_assets import ASSETS; print(len(ASSETS))"`
- **THEN** the output MUST be `≥ 15`

### Requirement: ip-7 — MotherDuck Dive + marimo notebook

The `motherduck/dives/gaeilge_full_curriculum_dive.py` + `notebooks/36_gaeilge_full_curriculum.py` files MUST exist.

#### Scenario: 2 files exist

- **WHEN** an operator runs `ls motherduck/dives/gaeilge_full_curriculum_dive.py notebooks/36_gaeilge_full_curriculum.py`
- **THEN** both files MUST be listed

### Requirement: ip-8 — wholesale-copy teanga_registry + clarin

The `meaisinfhoghlaim/models/teanga_registry.py` (12-model teanga registry from ciancheiltis) + `dlt_sources/language/clarin.py` (CLARIN VLO loader from ciancheiltis) MUST both be wholesale-copied with `SisterLift:` headers.

#### Scenario: 2 wholesale-copies

- **WHEN** an operator runs `uv run python scripts/sister_lifts.py verify`
- **THEN** the output MUST report `OK: all N ledger-tracked wholesale-copied files have SisterLift headers` with N ≥ 2
