## ADDED Requirements

### Requirement: Real DuckDB/DuckLake hydration pipeline

The system SHALL provide a single canonical DuckLake destination
(`dlt_sources.common.destinations_cianfhoghlaim.get_dlt_destination()`)
that real Dagster assets and standalone scripts use to write into the
live Garage S3 + Postgres DuckLake catalog, and a hydration script
(`scripts/hydrate_lc_full_corpus.py`) that walks the full local
`leaving_certificate/` corpus (all subjects in
`dlt_sources.filesystem.leaving_cert_source.LC_ALL_SUBJECTS`, not a
subset) and lands real per-file metadata plus real per-subject syllabus
cross-check extraction into that catalog.

`orchestration/resources.py::DuckLakeResource` SHALL NOT import a
nonexistent module — any caller of `DuckLakeResource.get_client()` or
`.get_dlt_destination()` SHALL succeed against a live local DuckLake
stack without a `ModuleNotFoundError`.

#### Scenario: A developer runs the full-corpus hydration script

- **GIVEN** the local `lakehouse-garage` and `lakehouse-postgres`
  containers are running
- **WHEN** `scripts/hydrate_lc_full_corpus.py` runs (with or without
  `--skip-extraction`)
- **THEN** `cianfhoghlaim.leaving_cert.corpus_documents` in the live
  DuckLake catalog contains one row per real file under
  `leaving_certificate/<subject>/` for every subject in
  `LC_ALL_SUBJECTS`
- **AND** without `--skip-extraction`,
  `cianfhoghlaim.leaving_cert.syllabus_cross_check` contains one row per
  subject with a real, extractable-text-layer syllabus PDF, sourced from
  a real MiniMax-primary/Qwen-secondary BAML extraction call — never
  fabricated data

#### Scenario: A Dagster asset writes through DuckLakeResource

- **GIVEN** an asset resolves `DuckLakeResource` from its resource defs
- **WHEN** it calls `.get_dlt_destination()` or `.get_client()`
- **THEN** the call succeeds (imports the real
  `dlt_sources.common.destinations_cianfhoghlaim` module, not the
  nonexistent `storage.ducklake_client`)
- **AND** if it calls `.get_client()`, the returned connection is
  already `ATTACH`ed to the live DuckLake catalog and `USE`s it

### Requirement: Real image-based OCR/VLM diagram extraction

The system SHALL support real page-image input to diagram extraction:
`ExtractSyllabusDiagram` (`baml_src/british_isles/ireland/education/
lc_extraction/syllabus_diagram.baml`) accepts an optional
`image: image[]?` parameter, and any caller that renders real page
images (via `meaisinfhoghlaim.document_factory.pdf_to_image_bridge`)
SHALL pass them through so the already-vision-configured `BIEPV3Vision`
client receives real pixels, not text-only inference. A caller with no
rendered images SHALL still work (backwards-compatible, `image=None`).

#### Scenario: A page image is rendered and passed to ExtractSyllabusDiagram

- **GIVEN** a subject's English-medium syllabus PDF exists locally
- **WHEN** `fibo_configs_from_syllabus_diagrams` or
  `lc5_chemistry_diagrams_extracted` runs
- **THEN** up to 8 real page images are rendered via `pdf_to_image_bridge`
  and passed as `image=[...]` to `ExtractSyllabusDiagram`
- **AND** the resulting BAML request body contains real base64 image
  content, not only extracted text

#### Scenario: No image renderer available

- **GIVEN** `pymupdf` is not installed or every page render fails
- **WHEN** `ExtractSyllabusDiagram` is called
- **THEN** the call still proceeds with `image=None`, using the
  existing text-only detection path — never a crash, never fabricated
  image data

### Requirement: OCR ensemble sends real image payloads

The system SHALL send actual rendered page-image bytes from the 4-path
OCR ensemble's vision paths: `meaisinfhoghlaim/ocr/ensemble/
ensembled_extractor.py`'s `_call_qwen3_vl` and `_call_gemma4` SHALL
never send a text string containing a local filesystem path in place of
real image content.

#### Scenario: qwen3-vl path is invoked

- **GIVEN** a PDF path is passed to `_call_qwen3_vl`
- **WHEN** the function builds its request body
- **THEN** the request's `content` is a multimodal list containing a
  real `image_url` data URI built from a rendered page, not a bare
  string containing the PDF's filesystem path

### Requirement: DuckDB/DuckLake-first notebook investigation surface

The system SHALL keep the 17 `notebooks/10_biep_pipeline_lakehouse_*.py`
marimo notebooks genuinely usable: they SHALL all parse as valid Python
(`ast.parse` succeeds) and SHALL NOT silently fabricate row counts or
other data when the real lakehouse connection is unavailable — a
connection failure SHALL surface visibly in the notebook's own output.

#### Scenario: A developer opens a lakehouse notebook with the stack down

- **GIVEN** the local DuckLake stack is not running
- **WHEN** a notebook cell attempts `connect_local_lakehouse()`
- **THEN** the cell's output visibly states the connection failed
- **AND** no cell renders a plausible-looking row count derived from a
  hash of the table name or similar fabrication

#### Scenario: A developer opens a lakehouse notebook with the stack up

- **GIVEN** the local DuckLake stack is running and hydrated (per the
  hydration pipeline requirement above)
- **WHEN** a subject-facing notebook (e.g. `02_syllabus_visualizer`) runs
- **THEN** it connects to the real local catalog first (not straight to
  the MotherDuck fallback)
- **AND** displays real row counts matching the hydration script's own
  verified counts
