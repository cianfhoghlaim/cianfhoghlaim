# Per-Subject Computer Science Pipeline (BIEP v3 M1 cohort 6/12)

## ADDED Requirements

### Requirement: Computer Science CocoIndex v1 App (BIEP v3 M1 cohort 6/12)

The system SHALL provide a CocoIndex v1 App at
`cocoindex_flows/british_isles/ireland/education/lc/computer_science.py`
that reads the Ireland Leaving Certificate Computer Science syllabus,
exam papers, and marking schemes from `leaving_certificate/computer_science/<lang>/`
and embeds them via the canonical BAAI/bge-m3 1024-d multilingual
embedder into the LanceDB table `cianhoghlaim.ireland.leaving_cycle.computer_science.{level}_{language}_chunks`.

The App MUST conform to the BIEP v3 R1-R4 contract:
- **R1** — `from ....._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` ContextKeys
- **R3** — `app = coco.App(coco.AppConfig(name="ireland_lc_computer_science_embedding"))` at module scope
- **R4** — At least one `@coco.fn(...)` decorator (2 in fact)

The App MUST handle languages ("en", "ga").

#### Scenario: Computer Science pipeline runs end-to-end against the in-tree fixture

- **WHEN** the operator runs `uv run pytest tests/biep_parity_lc/test_computer_science.py -v`
- **THEN** all 4 tests pass
- **AND** `run_computer_science_subject(sourcedir=<tmp>)` returns 3 rows (HL/OL/FL)
- **AND** each row has a 1024-d `embedding`
- **AND** each row has a non-empty `extracted_topic` + `extracted_level` + `extracted_year`

#### Scenario: Computer Science pipeline reads from the real corpus dir

- **WHEN** the operator sets `CIANFHOGHLAIM_LC_COMPUTER_SCIENCE_ROOT=leaving_certificate/computer_science`
- **AND** runs `mise run biep:v3:m1 --subject computer_science`
- **THEN** the CocoIndex App walks `leaving_certificate/computer_science/en/` + (where applicable) `leaving_certificate/computer_science/ga/`
- **AND** emits one row per chunked + embedded PDF into the per-language LanceDB table

### Requirement: BAML fallback for the Computer Science pipeline

The Python BAML fallback MUST apply per-subject regex patterns
calibrated for the LC Computer Science vocabulary
(algorithms, data structures, programming, databases, networking, operating systems, software engineering, computational thinking, boolean logic, machine learning) for the `topic` field;
`(Higher|Ordinary|Foundation)` for the `level` field; and
`(20\d{2})` for the `year` field
(Gaeilge uses `(Ardleibhéal|Gnáthleibhéal|Bonnleibhéal)` for the
level field).

#### Scenario: BAML fallback extracts canonical Computer Science vocabulary

- **WHEN** the operator calls `python_baml_fallback_extract("computer_science", "Leaving Certificate Computer Science — algorithms and data structures. Higher Level. 2024.")`
- **THEN** the returned `fields["topic"]` contains at least one Computer Science-specific keyword
- **AND** `fields["level"]` contains `Higher` (or `Ardleibhéal` for Computer Science)
- **AND** `fields["year"]` contains `2024`
