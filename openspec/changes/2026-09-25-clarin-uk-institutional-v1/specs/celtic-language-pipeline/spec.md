## ADDED Requirements

### Requirement: cu-1 — CLARIN-UK VLO loader wholesale-copied

The `dlt_sources/language/clarin.py` file MUST be wholesale-copied from the ciancheiltis sister repo with the `SisterLift:` provenance header prepended.

#### Scenario: provenance header present

- **WHEN** an operator runs `head -10 dlt_sources/language/clarin.py`
- **THEN** the output MUST contain `SisterLift: ciancheiltis @`

### Requirement: cu-2 — Corpas Náisiúnta na Gaeilge DLT source

The `dlt_sources/language/cng.py` file MUST provide a DLT source for the Corpas Náisiúnta na Gaeilge (100M words, 2000-2024, Foras na Gaeilge + DCU Gaois).

#### Scenario: CNG source importable

- **WHEN** an operator runs `uv run python -c "from dlt_sources.language.cng import cng_source; print(cng_source())"`
- **THEN** the output MUST NOT raise an ImportError

### Requirement: cu-3 — 3 dictionary DLT sources

The `dlt_sources/language/dictionaries/` directory MUST contain 3 DLT sources: `teanglann.py` (teanglann.ie), `focloir.py` (focloir.ie + Nua-Chorpas), and `nuachorpas.py` (English-Irish Dictionary project).

#### Scenario: 3 dictionary sources

- **WHEN** an operator runs `ls dlt_sources/language/dictionaries/`
- **THEN** the output MUST list `teanglann.py`, `focloir.py`, and `nuachorpas.py`

### Requirement: cu-4 — 3 placename DLT sources strengthened

The `dlt_sources/language/placenames/` directory MUST contain `logainm.py` (Logainm.ie) and `ainm.py` (Ainm.ie), with the existing `baml_src/celtic/gaois/{logainm,tearma}.baml` schemas strengthened.

#### Scenario: 2 placename sources

- **WHEN** an operator runs `ls dlt_sources/language/placenames/`
- **THEN** the output MUST list at least `logainm.py` and `ainm.py`

### Requirement: cu-5 — Dialect sources: Canúint + ABAIR + RIA

The `dlt_sources/language/dialect/` directory MUST contain `canuint.py` (strengthened), `abair.py` (Trinity College Dublin TTS/ASR), and `ria_corpas.py` (Royal Irish Academy historical 1600-1926).

#### Scenario: 3 dialect sources

- **WHEN** an operator runs `ls dlt_sources/language/dialect/`
- **THEN** the output MUST list `canuint.py`, `abair.py`, `ria_corpas.py`

### Requirement: cu-6 — CocoIndex institutional embedding

The `cocoindex_flows/celtic/institutional_embedding.py` App MUST embed Corpas Náisiúnta + NCCA + dictionaries cross-source into LanceDB.

#### Scenario: institutional App loads

- **WHEN** an operator runs `uv run python -c "from cocoindex_flows.celtic.institutional_embedding import institutional_embedding; print('OK')"`
- **THEN** the output MUST be `OK`

### Requirement: cu-7 — 12 Dagster institutional assets

The `orchestration/defs/2_materials/institutional/gaelic_institutional_assets.py` file MUST provide 12 assets (2 per source × 6 sources).

#### Scenario: 12 assets

- **WHEN** an operator runs `uv run python -c "from orchestration.defs.institutional.gaelic_institutional_assets import ASSETS; print(len(ASSETS))"`
- **THEN** the output MUST be `≥ 12`
