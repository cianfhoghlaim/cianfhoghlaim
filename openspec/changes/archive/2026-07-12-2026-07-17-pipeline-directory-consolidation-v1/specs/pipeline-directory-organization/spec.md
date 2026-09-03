# pipeline-directory-organization

## ADDED Requirements

### Requirement: Pipeline packages SHALL share a parallel directory hierarchy

Pipeline packages SHALL share a parallel directory hierarchy at the
region level. `baml_src/`, `dlt/`, `orchestration/defs/`, and
`cocoindex/` SHALL each contain a region directory; each region
directory SHALL contain one subdirectory per jurisdiction, using the
snake_case full jurisdiction name (not an ISO 3-letter code or
legacy slug). The five region roots are `european_nations/`,
`commonwealth/`, `british_isles/`, `american_nations/`, and
`european_union/`.

#### Scenario: Each layer has a germany subdirectory

- **GIVEN** the post-v7 root layout with `baml_src/`, `dlt/`,
  `orchestration/defs/`, and `cocoindex/` at the repo root
- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/european_nations/germany/` SHALL exist
- **AND** `dlt/european_nations/germany/` SHALL exist with subdirs
  `education/`, `law/`, `medicine/`, `statistics/`, `government/`
- **AND** `orchestration/defs/1_ingestion/european_nations/germany/`
  SHALL exist with the same five sector subdirs each containing a
  `defs.yaml`
- **AND** `cocoindex/european_nations/germany/education_embedding.py`
  SHALL exist

### Requirement: Jurisdiction directories SHALL use full snake_case names

Jurisdiction directories SHALL use the snake_case full name (e.g.
`germany/`, `northern_ireland/`, `united_states/`,
`south_africa/`). ISO 3-letter codes (e.g. `deu/`, `aut/`,
`usa/`, `zaf/`) SHALL NOT appear as directory names. Short codes
SHALL remain valid as `source_id` strings, partition values, asset
keys, and BAML parameter values only.

#### Scenario: No ISO-3 codes in jurisdiction directory paths

- **GIVEN** the post-v7 root layout
- **WHEN** the directory consolidation change is materialised
- **THEN** the directories `baml_src/european_nations/deu/`,
  `dlt/european_nations/deu/`,
  `orchestration/defs/1_ingestion/european_nations/deu/`, and
  `cocoindex/european_nations_deu_education_embedding.py`
  SHALL NOT exist
- **AND** the equivalents at the full-name paths SHALL exist

### Requirement: British Isles SHALL use single full-name directories

British Isles SHALL use single full-name directories. Every British
Isles jurisdiction SHALL live under exactly one subdirectory of
`british_isles/`, using the snake_case full name: `england/`,
`scotland/`, `wales/`, `northern_ireland/`, `ireland/`,
`isle_of_man/`, `jersey/`, `guernsey/`. ISO slugs (`en/`, `sct/`,
`wls/`, `ni/`, `iom/`, `jey/`, `ggy/`) SHALL NOT appear as
directory names in `baml_src/british_isles/`, `dlt/british_isles/`,
`orchestration/defs/1_ingestion/british_isles/`, or
`cocoindex/british_isles/`.

#### Scenario: British Isles uses single full-name directories

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/british_isles/england/` SHALL contain the
  three .baml files `education.baml`, `law.baml`, `medicine.baml`
- **AND** `dlt/british_isles/england/` SHALL contain the five
  sector subdirs `education/`, `law/`, `medicine/`, `statistics/`,
  `government/`
- **AND** `cocoindex/british_isles/england/education_embedding.py`
  SHALL exist
- **AND** the legacy `en/`, `sct/`, `wls/`, `ni/`, `iom/`, `jey/`,
  `ggy/` directories SHALL NOT exist

### Requirement: cocoindex SHALL have a hierarchical subdirectory structure

`cocoindex/` SHALL have a hierarchical subdirectory structure. The
required subdirectories are `_shared/`, `american_nations/`,
`british_isles/` (with an `_cross/` subdir), `european_nations/`
(with a `_cross/` sibling), `european_nations_cross/`,
`commonwealth/` (with `_cross/` sibling), `commonwealth_cross/`,
`celtic/`, `subjects/`, `media/`, `portfolio/`,
`knowledge_graph/`, `infrastructure/`, `corpus/`, and
`biep_parity/`. Cross-jurisdiction CocoIndex v1 Apps SHALL be
named with a `_cross/` suffix (e.g.
`european_nations_cross/law_embedding.py`).

#### Scenario: Cross-jurisdiction apps use _cross suffix

- **WHEN** the directory consolidation change is materialised
- **THEN** `cocoindex/european_nations_cross/law_embedding.py`
  SHALL exist
- **AND** `cocoindex/european_nations_cross/medicine_embedding.py`
  SHALL exist
- **AND** `cocoindex/european_nations_law_embedding.py` SHALL NOT
  exist

### Requirement: Sub-state directories SHALL nest under jurisdiction directories

Sub-state directories SHALL nest under jurisdiction directories.
Where a jurisdiction has first-class sub-states (Canadian
provinces, Nigerian states), the sub-states SHALL be nested under
the jurisdiction directory in a `provinces/` or `states/`
subdirectory. Sub-state codes (e.g. `ab/`, `bc/`, `on/`, `qc/`
for Canada; `nga_los/` for Lagos) SHALL NOT appear as top-level
directories.

#### Scenario: Canadian provinces are nested under canada/

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/commonwealth/canada/provinces/alberta/`
  SHALL exist
- **AND** `dlt/commonwealth/canada/provinces/alberta/education/`,
  etc. SHALL exist
- **AND** the directories `dlt/commonwealth/can/ab/`,
  `dlt/commonwealth/can/bc/`, etc. SHALL NOT exist

### Requirement: Pipelines parity check SHALL exist

A pipelines parity check SHALL exist. `mise run pipelines:parity`
SHALL walk the four data-platform packages and emit a
per-jurisdiction matrix showing which layers contain the
jurisdiction. The check SHALL exit non-zero when run with
`PIPELINE_PARITY_STRICT=1` and any layer is missing for any
jurisdiction that exists in at least one layer.

#### Scenario: Parity check detects missing layer

- **GIVEN** `baml_src/european_nations/germany/` exists but
  `dlt/european_nations/germany/` does not
- **WHEN** `PIPELINE_PARITY_STRICT=1 mise run pipelines:parity` runs
- **THEN** the command SHALL exit non-zero
- **AND** the output SHALL list `germany` with a `dlt = MISSING`
  column

### Requirement: Backward compatibility shims SHALL exist for renamed paths

Backward compatibility shims SHALL exist for renamed paths. Every
renamed directory SHALL provide a deprecation shim: a stub
`__init__.py` (for Python packages) or a `LEGACY_ALIASES.md` (for
purely file-based layouts) that emits a `DeprecationWarning` on
import and re-exports the new location. The shim SHALL be retained
for at least one release cycle after the rename lands.

#### Scenario: Old import path emits a deprecation warning

- **GIVEN** a shim at `dlt/european_nations/deu/__init__.py`
- **WHEN** `from dlt.european_nations.deu import X` is executed
- **THEN** a `DeprecationWarning` SHALL be emitted with a message
  pointing to `dlt.european_nations.germany`
- **AND** `X` SHALL resolve to the new module's `X`