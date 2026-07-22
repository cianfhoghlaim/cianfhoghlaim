# cross-region-pipeline

## ADDED Requirements

### Requirement: American nations pipeline directory

American nations (Brazil, Mexico, United States, Venezuela) SHALL
have pipeline directories under `american_nations/`. The legacy
`americas/` directory SHALL NOT exist. California-specific sources
SHALL live under `american_nations/united_states/`.

#### Scenario: american_nations is the canonical region root

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/american_nations/brazil/`,
  `baml_src/american_nations/mexico/`,
  `baml_src/american_nations/united_states/`,
  `baml_src/american_nations/venezuela/` SHALL exist
- **AND** `dlt/american_nations/brazil/`, etc. SHALL exist
- **AND** `orchestration/defs/1_ingestion/american_nations/brazil/`,
  etc. SHALL exist
- **AND** `baml_src/americas/`, `dlt/americas/`,
  `orchestration/defs/1_ingestion/americas/` SHALL NOT exist

### Requirement: European nations jurisdiction directories use full names

European nations SHALL live under `european_nations/<full>/` using
the snake_case full name (e.g. `germany/`, `austria/`, `france/`).
The ISO 3-letter codes SHALL NOT appear as directory names.

#### Scenario: germany has parallel directories in three layers

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/european_nations/germany/`,
  `dlt/european_nations/germany/`,
  `orchestration/defs/1_ingestion/european_nations/germany/` SHALL
  exist
- **AND** `baml_src/european_nations/deu/`, etc. SHALL NOT exist