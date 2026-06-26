# Spec Delta — Round 11 Phase 3C

## ADDED Requirements

### Requirement: Country-First Layout — Single-Source Migration

The system SHALL migrate all single-source DLT files from the legacy flat-tree layout
(`dlt_sources/ireland/*.py`, `dlt_sources/uk/{england,northern_ireland,scotland,wales}/*.py`,
`dlt_sources/celtic/*.py`) to the canonical country-first layout
(`dlt_sources/{nation}/{domain}/{entity}.py`).

#### Scenario: Single-source IE education files migrated

- **WHEN** a file in `dlt_sources/ireland/` defines exactly one `@dlt.source` function and is in scope of the education domain
- **THEN** the system SHALL move it to `dlt_sources/ie/education/{filename}.py`
- **AND** the system SHALL update all importers in `dagster_defs/`, `tests/`, `dlt_utils/`, and remaining `dlt_sources/ireland/*.py` files

#### Scenario: Single-source UK education files migrated

- **WHEN** a file in `dlt_sources/uk/{england,northern_ireland,scotland,wales}/` defines exactly one `@dlt.source` function and is in scope of the education domain
- **THEN** the system SHALL move it to `dlt_sources/{en,ni,sct,wls}/education/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Single-source UK statistics files migrated

- **WHEN** a file in `dlt_sources/uk/{england,northern_ireland,scotland,wales}/` defines exactly one `@dlt.source` function and is in scope of the statistics domain
- **THEN** the system SHALL move it to `dlt_sources/{en,ni,sct,wls}/statistics/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Single-source Celtic nation-scoped files migrated

- **WHEN** a file in `dlt_sources/celtic/` defines exactly one `@dlt.source` function and is scope-specific to Ireland
- **THEN** the system SHALL move it to `dlt_sources/ie/{culture,education}/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Shared utility files migrated to dlt_sources/common/

- **WHEN** a file in `dlt_sources/ireland/` defines protocol classes, registries, or deduplication utilities used across multiple DLT sources
- **THEN** the system SHALL move it to `dlt_sources/common/{filename}.py`
- **AND** the system SHALL update all intra-tree and external importers

#### Scenario: Multi-source files NOT touched

- **WHEN** a legacy file defines more than one `@dlt.source` function
- **THEN** the system SHALL NOT move it in Phase 3C
- **AND** the system SHALL defer it to Phase 3D for per-source splitting first

#### Scenario: Legacy trees NOT deleted

- **WHEN** legacy flat trees (`dlt_sources/ireland/`, `dlt_sources/uk/`, `dlt_sources/celtic/`) still contain multi-source files deferred to Phase 3D
- **THEN** the system SHALL NOT delete the legacy trees
- **AND** the system SHALL defer tree deletion to Phase 3E