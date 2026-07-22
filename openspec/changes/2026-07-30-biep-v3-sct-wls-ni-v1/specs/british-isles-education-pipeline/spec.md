## MODIFIED Requirements

### Requirement: Scotland + Wales + NI pipelines cover all 380 cohorts

The system SHALL provide a generic multi-jurisdiction DLT pipeline
(`dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py`)
that handles Scotland + Wales + Northern Ireland via a single factory
function. The pipeline SHALL materialise 380+ cohorts:

- Scotland: 50 SCQF subjects × 3 levels (National 5 + Higher + Adv Higher) = 150 cohorts
- Wales: 80 WJEC subjects × 2 levels (GCSE + A-Level) = 160 cohorts
- Northern Ireland: 35 CCEA subjects × 2 levels (GCSE + A-Level) = 70 cohorts

#### Scenario: 3-jurisdiction pipeline emits 380+ rows

- **WHEN** `seed_registry()` is run + the lakehouse stack is healthy
- **THEN** the `sct_wls_ni_jurisdiction_pipeline(jurisdiction)` factory
  materialises ≥380 rows total across the 3 jurisdictions
- **AND** the companion notebook Tab 2 shows
  `scotland >= 150, wales >= 160, northern_ireland >= 70`

#### Scenario: 3 generic Dagster assets handle all 3 jurisdictions

- **WHEN** `dg list assets | grep sct_wls_ni_` runs
- **THEN** 4 assets are listed:
  - `sct_wls_ni_documents_ingested` (Layer 1, iterates over 3 jurisdictions)
  - `sct_wls_ni_extractions` (Layer 2, iterates over 3 jurisdictions)
  - `sct_wls_ni_embeddings` (Layer 3, iterates over 3 jurisdictions)
  - `sct_wls_ni_extractions_ragas_check` (Layer 2 asset_check)
- **AND** zero per-jurisdiction per-subject assets are present