# Spec Delta — `ireland-primary-jc-dlt-baml` (new capability)

## Purpose

`ireland-primary-jc-dlt-baml` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `oideachais/dlt_sources/ireland/primary.py`, `oideachais/dlt_sources/ireland/junior_cycle.py`, and `oideachais/dagster_defs/assets/ie/education/curriculum_dlt_assets.py` (or the new `leabharlann_demo_assets.py`). See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

dlt sources + BAML extraction + Dagster assets for the Ireland primary curriculum and the Junior Cycle curriculum. Closes the BAML-without-dlt gap identified in `oideachais/REFACTORING.md` Feature 1.

## ADDED Requirements

### Requirement: Ireland Primary dlt source
The system SHALL provide a `@dlt.source` for the Ireland primary curriculum, yielding 4 resources.

#### Scenario: Primary specifications
- **GIVEN** the `ireland_primary_raw` Dagster asset is materialised
- **WHEN** the source walks the primary curriculum scrape cache
- **THEN** it SHALL yield one row per primary curriculum specification PDF (12 curriculum areas × ~3 docs)
- **AND** each row SHALL be tagged with `account="ireland_primary"`, `domain=<curriculum area code>`, and `cycle="primary"`
- **AND** the primary key SHALL be `(file_hash, document_id)`

#### Scenario: Primary strands + learning outcomes + curriculum areas
- **GIVEN** a primary specification PDF is yielded
- **WHEN** the `extraction_metadata` resource is enabled
- **THEN** the BAML function `b.ExtractPrimaryFramework(text)` SHALL be invoked
- **AND** the returned `PrimaryCurriculumArea[]` SHALL be persisted as rows
- **AND** the function `b.ExtractPrimaryLearningOutcomes(text)` SHALL also be invoked
- **AND** the returned `PrimaryLearningOutcome[]` SHALL be persisted as rows

#### Scenario: Memoisation
- **GIVEN** the same `file_hash` has been extracted before
- **WHEN** the asset re-materialises
- **THEN** the BAML call SHALL be skipped and the cached rows SHALL be reused
- **AND** the cache key SHALL be `(file_hash, baml_function_name)`

### Requirement: Ireland Junior Cycle dlt source
The system SHALL provide a `@dlt.source` for the Ireland Junior Cycle curriculum, yielding 3 resources.

#### Scenario: Junior Cycle specifications
- **GIVEN** the `ireland_junior_cycle_raw` Dagster asset is materialised
- **WHEN** the source walks the JC curriculum scrape cache
- **THEN** it SHALL yield one row per JC subject spec (18 subjects × 1 spec)
- **AND** each row SHALL be tagged with `account="ireland_junior_cycle"`, `subject=<JuniorCycleSubject enum>`, and `cycle="junior_cycle"`
- **AND** the primary key SHALL be `(file_hash, subject)`

#### Scenario: JC short courses + CBA tasks
- **GIVEN** a JC spec PDF is yielded
- **WHEN** the `extraction_metadata` resource is enabled
- **THEN** the BAML function `b.ExtractJCSpec(text)` SHALL be invoked
- **AND** the returned `JCSubjectSpec` SHALL be persisted as a row
- **AND** the function `b.ExtractCBADescriptor(text)` SHALL also be invoked
- **AND** the returned `CBATask[]` SHALL be persisted as rows

### Requirement: Dagster assets for primary + JC
The system SHALL register 2 new Dagster assets that materialise the primary and JC sources.

#### Scenario: ireland_primary_raw asset
- **GIVEN** the `ireland_primary_raw` asset is materialised
- **WHEN** it runs
- **THEN** it SHALL invoke `ireland_primary_source()` with the appropriate base path
- **AND** the asset metadata SHALL include `row_counts` and `total_rows`

#### Scenario: ireland_junior_cycle_raw asset
- **GIVEN** the `ireland_junior_cycle_raw` asset is materialised
- **WHEN** it runs
- **THEN** it SHALL invoke `ireland_junior_cycle_source()` with the appropriate base path
- **AND** the asset metadata SHALL include `row_counts` and `total_rows`

## MODIFIED Requirements

*(None.)*

## REMOVED Requirements

*(None.)*
