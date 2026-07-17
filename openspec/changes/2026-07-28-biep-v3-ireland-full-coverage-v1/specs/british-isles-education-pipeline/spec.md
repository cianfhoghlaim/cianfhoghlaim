## MODIFIED Requirements

### Requirement: Ireland pipeline covers all 134+ cohorts via the registry

The system SHALL provide a single generic Ireland DLT pipeline
(`dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py`)
that reads the canonical registry
(`cianfhoghlaim.education._registry.subjects`) and materialises every
Ireland cohort (≥134 rows: 64 LC + 18 JC + 16 short courses + 36 CBAs).

The pipeline SHALL NOT introduce per-subject Python files.

#### Scenario: Ireland pipeline emits 134+ rows

- **WHEN** `seed_registry()` is run + the lakehouse stack is healthy
- **THEN** the `ireland_jurisdiction_pipeline()` returns a DLT pipeline
  that materialises ≥134 rows to the
  `cianfhoghlaim.education.ireland.*` namespace
- **AND** the companion notebook Tab 2 (Nation comparison) shows
  `ireland >= 134`

#### Scenario: 3 generic Ireland Dagster assets replace per-subject assets

- **WHEN** `dg list assets | grep ireland_` runs
- **THEN** exactly 4 entries are listed:
  - `ireland_documents_ingested` (Layer 1)
  - `ireland_extractions` (Layer 2)
  - `ireland_embeddings` (Layer 3)
  - `ireland_extractions_ragas_check` (Layer 2 asset_check)
- **AND** zero per-subject assets are present (`lc5_<subject>_*`,
  `jc_<subject>_*`, etc.)

#### Scenario: Generic pipeline writes the canonical namespace

- **WHEN** the Ireland pipeline runs
- **THEN** the resulting DuckDB tables match the shape
  `cianfhoghlaim.education.ireland.<stage>.<subject>[.<variant>]`
- **AND** the resulting LanceDB tables match the same shape
  (replacing the legacy `oideachais.lc.*` / `oideachais.jc.*` aliases
  per the Phase 0 rename)