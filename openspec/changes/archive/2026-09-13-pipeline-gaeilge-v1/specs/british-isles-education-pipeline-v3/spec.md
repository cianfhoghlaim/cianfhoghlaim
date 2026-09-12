# Per-Subject Gaeilge Pipeline (BIEP v3 M1 cohort 5/12)

## ADDED Requirements

### Requirement: Gaeilge CocoIndex v1 App (BIEP v3 M1 cohort 5/12)

The system SHALL provide a CocoIndex v1 App at
`cocoindex_flows/british_isles/ireland/education/lc/gaeilge.py`
that reads the Ireland Leaving Certificate Gaeilge syllabus,
exam papers, and marking schemes from `leaving_certificate/gaeilge/<lang>/`
and embeds them via the canonical BAAI/bge-m3 1024-d multilingual
embedder into the LanceDB table `cianhoghlaim.ireland.leaving_cycle.gaeilge.{level}_{language}_chunks`.

The App MUST conform to the BIEP v3 R1-R4 contract:
- **R1** — `from ....._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` ContextKeys
- **R3** — `app = coco.App(coco.AppConfig(name="ireland_lc_gaeilge_embedding"))` at module scope
- **R4** — At least one `@coco.fn(...)` decorator (2 in fact)

The App MUST handle languages ("ga",).

#### Scenario: Gaeilge pipeline runs end-to-end against the in-tree fixture

- **WHEN** the operator runs `uv run pytest tests/biep_parity_lc/test_gaeilge.py -v`
- **THEN** all 4 tests pass
- **AND** `run_gaeilge_subject(sourcedir=<tmp>)` returns 3 rows (HL/OL/FL)
- **AND** each row has a 1024-d `embedding`
- **AND** each row has a non-empty `extracted_topic` + `extracted_level` + `extracted_year`

#### Scenario: Gaeilge pipeline reads from the real corpus dir

- **WHEN** the operator sets `CIANFHOGHLAIM_LC_GAEILGE_ROOT=leaving_certificate/gaeilge`
- **AND** runs `mise run biep:v3:m1 --subject gaeilge`
- **THEN** the CocoIndex App walks `leaving_certificate/gaeilge/en/` + (where applicable) `leaving_certificate/gaeilge/ga/`
- **AND** emits one row per chunked + embedded PDF into the per-language LanceDB table

### Requirement: BAML fallback for the Gaeilge pipeline

The Python BAML fallback MUST apply per-subject regex patterns
calibrated for the LC Gaeilge vocabulary
(gramadach, litríocht, filíocht, prós, drama, comhrá, scríbhneoireacht, éisteacht, léamh, tuiscint, saíocht, nuachlasaiceach) for the `topic` field;
`(Higher|Ordinary|Foundation)` for the `level` field; and
`(20\d{2})` for the `year` field
(Gaeilge uses `(Ardleibhéal|Gnáthleibhéal|Bonnleibhéal)` for the
level field).

#### Scenario: BAML fallback extracts canonical Gaeilge vocabulary

- **WHEN** the operator calls `python_baml_fallback_extract("gaeilge", "Leaving Certificate Gaeilge — gramadach agus litríocht. Higher Level. 2024.")`
- **THEN** the returned `fields["topic"]` contains at least one Gaeilge-specific keyword
- **AND** `fields["level"]` contains `Higher` (or `Ardleibhéal` for Gaeilge)
- **AND** `fields["year"]` contains `2024`
