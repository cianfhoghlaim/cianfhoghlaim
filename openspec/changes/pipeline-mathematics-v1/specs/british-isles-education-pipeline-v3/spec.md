# Per-Subject Mathematics Pipeline (BIEP v3 M1 cohort 1 of 12)

## ADDED Requirements

### Requirement: Mathematics CocoIndex v1 App (BIEP v3 M1 cohort 1)

The system SHALL provide a CocoIndex v1 App at
`cocoindex_flows/british_isles/ireland/education/lc/mathematics.py`
that reads the Ireland Leaving Certificate Mathematics syllabus,
exam papers, and marking schemes from
`leaving_certificate/mathematics/<lang>/` and embeds them via the
canonical BAAI/bge-m3 1024-d multilingual embedder into the
LanceDB table
`cianhoghlaim.ireland.leaving_cycle.mathematics.<level>_<lang>_chunks`.

The App MUST conform to the BIEP v3 R1-R4 contract:
- **R1** — `from ....._shared._lifespan import shared_lifespan` (delegates to the canonical lifespan in `cocoindex_flows/_shared/_lifespan.py`)
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` ContextKeys
- **R3** — `app = coco.App(coco.AppConfig(name="ireland_lc_mathematics_embedding"))` at module scope (wrapped in `if COCOINDEX_AVAILABLE:` because the conformance check is too strict for nested paths and the `if` wrapper pre-existed in `lc_subject_embedding.py`)
- **R4** — At least one `@coco.fn(...)` decorator (2 in fact: `process_mathematics_file` + `mathematics_app_main`)

The App MUST handle both `en` and `ga` languages, plus all 3 NCCA
levels (Higher / Ordinary / Foundation).

#### Scenario: Mathematics pipeline runs end-to-end against the in-tree fixture

- **WHEN** the operator runs `uv run pytest tests/biep_parity_lc/test_mathematics.py -v`
- **THEN** all 9 tests pass
- **AND** `run_mathematics_subject(sourcedir=<tmp>)` returns 3 rows (HL/OL/FL)
- **AND** each row has a 1024-d `embedding` (matching BGE-M3 dim)
- **AND** each row has a non-empty `extracted_topic` + `extracted_level` + `extracted_year`
- **AND** the brute-force cosine-similarity query returns a Mathematics row

#### Scenario: Mathematics pipeline reads from the real corpus dir

- **WHEN** the operator sets `CIANFHOGHLAIM_LC_MATHEMATICS_ROOT=leaving_certificate/mathematics`
- **AND** runs `mise run biep:v3:m1 --subject mathematics`
- **THEN** the CocoIndex App walks `leaving_certificate/mathematics/en/` + `leaving_certificate/mathematics/ga/`
- **AND** emits one row per chunked + embedded PDF into the per-language LanceDB table

### Requirement: BAML fallback for per-subject pipelines

Per the kcg-runtime-inert-layers memory (defect #3), the
`baml_client/` generated module is currently unavailable because
`baml-cli generate --from baml_src` fails on duplicate class
definitions in `baml_src/_shared/templates/`. Until that defect
is remediated, each per-subject CocoIndex App MUST use a Python
fallback for its BAML extraction function.

The Python fallback MUST:
- Live in `_shared.py` (the per-subject shared scaffolding)
- Use a `baml_available()` probe at module-import time to decide
  between the BAML path and the fallback path
- Apply per-subject regex patterns calibrated for the LC
  Mathematics vocabulary (`algebra`, `calculus`, `geometry`,
  `trigonometry`, `statistics`, `probability`, `complex numbers`,
  `matrices`, `functions`, `sequences`, `series`, `differentiation`,
  `integration`, `coordinate geometry`) for the `topic` field;
  `(Higher|Ordinary|Foundation)` for the `level` field; and
  `(20\d{2})` for the `year` field
- Return a dict in the same shape as the BAML function's return
  type would: `{"subject": str, "extraction_source": str, "fields": {"topic": list[str], "level": list[str], "year": list[str]}}`

When the `baml_client/` defect is fixed and the client regenerates,
the per-subject modules MUST automatically pick up the BAML path
(the `try: from baml_client.baml_client import b` import is the
only piece that needs to succeed). The Python fallback MUST remain
in place as a final safety net.

#### Scenario: BAML fallback extracts canonical Mathematics vocabulary

- **WHEN** the operator calls `python_baml_fallback_extract("mathematics", "Students study calculus and differentiation. Higher Level. 2024 exam.")`
- **THEN** the returned `fields["topic"]` contains at least one of `calculus` / `differentiation`
- **AND** `fields["level"]` contains `Higher`
- **AND** `fields["year"]` contains `2024`
- **AND** `extraction_source == "python_fallback"`

#### Scenario: BAML availability probe reports False until defect #3 is fixed

- **WHEN** the operator runs `uv run python -c "from cocoindex_flows.british_isles.ireland.education.lc import baml_available; print(baml_available())"`
- **THEN** the output is `False`
- **AND** the `python_baml_fallback_extract` path is the one exercised by the per-subject pipeline
