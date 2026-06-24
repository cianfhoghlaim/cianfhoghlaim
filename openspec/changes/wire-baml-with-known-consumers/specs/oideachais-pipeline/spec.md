## MODIFIED Requirements

### Requirement: BAML functions for the 5 educational stages SHALL be defined
The oideachais quadrant SHALL provide BAML functions for each of
the 5 educational stages (Aistear, Primary, Junior Cycle, Senior
Cycle, Tertiary). Each function MUST live in its own dedicated
`.baml` module under `oideachais/baml_src/` and MUST use the
canonical `LitellmClient`.

#### Scenario: A new educational stage needs BAML extraction
- **WHEN** a contributor adds BAML extraction for a new stage
  (e.g. Aistear early-childhood)
- **THEN** they MUST create a new `baml_src/<stage>.baml` module
- **AND** they MUST use `client LitellmClient`
- **AND** they MUST register the function in the `dlt_sources/ireland/`
  re-export list

#### Scenario: A dlt source has PENDING_BAML placeholders
- **WHEN** a dlt source yields rows with placeholder fields like
  `"extracted_at": "PENDING_BAML"`
- **THEN** the dlt source MUST eventually invoke the corresponding
  BAML function to populate the real extraction
- **AND** the dlt source MUST have a corresponding Dagster asset
  wrapper that materialises the extracted tables

### Requirement: Aistear BAML extraction is wired
The oideachais quadrant SHALL provide an end-to-end Aistear (early
childhood) extraction pipeline. The pipeline MUST consist of:

1. A BAML function `ExtractAistearFramework` in
   `oideachais/baml_src/early_childhood.baml`
2. A dlt source `aistear_curriculum` in
   `oideachais/dlt_sources/ireland/aistear.py` that invokes the
   BAML function and yields 3 resources:
   `aistear_documents`, `aistear_principles`, `aistear_learning_goals`
3. A Dagster asset wrapper in
   `oideachais/dagster_defs/assets/ie/education/aistear_dlt_assets.py`
   that materialises all 3 resources into a `ie.education.aistear`
   DuckLake dataset

#### Scenario: An aistear PDF is materialised
- **WHEN** the `aistear_documents_ducklake` Dagster asset runs
- **THEN** it MUST scan the cache at
  `/stedding/ingest_queue/aistear/`
- **AND** for each PDF, it MUST call `b.ExtractAistearFramework`
  to extract the principles and learning goals
- **AND** it MUST write 1 row to `aistear_documents` per PDF,
  N rows to `aistear_principles`, and M rows to `aistear_learning_goals`

#### Scenario: The BAML client is not generated
- **WHEN** the `baml_client` package is not yet generated
- **THEN** the dlt source MUST gracefully degrade (no exception)
- **AND** the Dagster asset MUST emit a warning and materialise
  the documents table with placeholder fields, but skip the
  principles and learning_goals tables
