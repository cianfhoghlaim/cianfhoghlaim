# oideachais-pipeline

## ADDED Requirements

### Requirement: Pipeline directory parity SHALL hold for oideachais subjects

Pipeline directory parity SHALL hold for the
`oideachais.lc.<subject>.<level>_<lang>` BAML/DLT/CocoIndex
pipelines across `baml_src/`, `dlt/`,
`orchestration/defs/1_ingestion/`, and `cocoindex/`. A parity check
SHALL verify that each LC subject that has BAML extraction in
`baml_src/education/lc_extraction/` also has a DLT source in
`dlt/british_isles/ireland/education/`, a Dagster asset in
`orchestration/defs/1_ingestion/curriculum/lc6/`, and a CocoIndex
embedding in `cocoindex/subjects/<subject>_embedding.py`.

#### Scenario: Mathematics has parallel pipelines in every layer

- **WHEN** the parity check runs against the post-v7 layout
- **THEN** `baml_src/british_isles/ireland/education.baml` SHALL
  exist
- **AND** `dlt/british_isles/ireland/education/` SHALL exist
- **AND** `orchestration/defs/1_ingestion/curriculum/lc6/mathematics.yaml`
  SHALL exist
- **AND** `cocoindex/subjects/mathematics_embedding.py` SHALL exist