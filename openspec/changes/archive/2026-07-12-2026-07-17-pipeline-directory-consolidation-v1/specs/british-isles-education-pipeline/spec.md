# british-isles-education-pipeline

## MODIFIED Requirements

### Requirement: BIEP sources SHALL live in full-name jurisdiction directories

BIEP sources SHALL live in `baml_src/british_isles/<full>/`,
`dlt/british_isles/<full>/`,
`orchestration/defs/1_ingestion/british_isles/<full>/`, and
`cocoindex/british_isles/<full>/`. The `<full>` placeholder SHALL
be one of: `england/`, `scotland/`, `wales/`, `northern_ireland/`,
`ireland/`, `isle_of_man/`, `jersey/`, `guernsey/`. The legacy
ISO/legacy slug directories (`en/`, `sct/`, `wls/`, `ni/`, `iom/`,
`jey/`, `ggy/`) SHALL NOT exist.

#### Scenario: scotland BIEP sources live at the full-name path

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/british_isles/scotland/education.baml` SHALL
  exist
- **AND** `dlt/british_isles/scotland/education/` SHALL exist
- **AND** `orchestration/defs/1_ingestion/british_isles/scotland/education/defs.yaml`
  SHALL exist
- **AND** `cocoindex/british_isles/scotland/education_embedding.py`
  SHALL exist
- **AND** `baml_src/british_isles/sct/`,
  `dlt/british_isles/sct/`,
  `orchestration/defs/1_ingestion/british_isles/sct/`, and
  `cocoindex/british_isles/sct_education_embedding.py` SHALL NOT
  exist

### Requirement: BIEP cross-jurisdiction CocoIndex apps SHALL live under _cross

BIEP cross-jurisdiction CocoIndex apps SHALL live under a `_cross/`
sibling directory. Specifically, the cross-jurisdiction BIEP
CocoIndex v1 App SHALL live at
`cocoindex/british_isles/_cross/education_embedding.py`. The
legacy path `cocoindex/biep_parity/` SHALL remain as a separate
conformance-test directory (it is not the BIEP v1 App itself).

#### Scenario: BIEP cross-jurisdiction app is in _cross/

- **WHEN** the directory consolidation change is materialised
- **THEN** `cocoindex/british_isles/_cross/education_embedding.py`
  SHALL exist
- **AND** `cocoindex/biep_parity/` SHALL still exist with the 7
  per-jurisdiction conformance embeddings