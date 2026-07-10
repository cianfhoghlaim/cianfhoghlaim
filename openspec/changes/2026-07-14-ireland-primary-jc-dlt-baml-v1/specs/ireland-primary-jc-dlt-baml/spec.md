# Spec Delta — ireland-primary-jc-dlt-baml

This delta adds one new requirement to the existing `ireland-primary-jc-dlt-baml` capability, documenting that Phase 1 of the capability is now shipped. The 3 pre-existing requirements (Primary stage DLT sources / Junior Cycle DLT sources (24 subjects) / Stage-specific BAML schemas) are preserved unchanged.

## ADDED Requirements

### Requirement: Phase 1 ship — Primary + JC DLT loop is functionally complete

The `ireland-primary-jc-dlt-baml` capability SHALL be considered Phase 1 complete once all 3 DLT sources (`primary` + `junior_cycle` + `primary_jc_combined`), both stage-specific BAML extractor functions (`ExtractPrimaryArea` + `ExtractJCSubjectSpec`), and all 3 Layer 1 Ingestion `defs.yaml` cron assets (one per source) are present, AST-parse cleanly, and the BAML files generate zero parse errors under `mise run baml:generate`.

#### Scenario: 3 DLT sources ship at the canonical paths

- **GIVEN** the 2026-07-14-ireland-primary-jc-dlt-baml-v1 change has landed
- **WHEN** `ls cianfhoghlaim/dlt/british_isles/ireland/education/{primary,junior_cycle,primary_jc_combined}.py` is run
- **THEN** all 3 files exist
- **AND** each AST-parses cleanly under `uv run python3 -c "import ast; ast.parse(open('<file>').read())"`
- **AND** each follows the canonical BIEP v1 dlt pattern: `@dlt.resource(name=..., write_disposition="merge", primary_key=["url"])`, structlog observability, honours `USE_LOCAL_SCRAPES=true` (default) to read from `/stedding/ingest_queue/<stage>/`

#### Scenario: 2 stage-specific BAML schemas ship at the canonical paths

- **GIVEN** the change has landed
- **WHEN** `ls cianfhoghlaim/baml/education/{primary, junior_cycle}/*_extraction.baml` is run
- **THEN** both files exist (`primary_extraction.baml` + `junior_cycle_extraction.baml`)
- **AND** `mise run baml:generate` exits with 0 errors attributable to these 2 files
- **AND** each defines exactly 1 BAML function (`ExtractPrimaryArea` /
  `ExtractJCSubjectSpec`) that returns a stage-specific Pydantic class
  (`PrimaryAreaSpecStage` / `JCSubjectSpecStage`) constrained to the
  spec-mandated year levels (Primary: 8 NCCA year levels, JC: Year 1 +
  Year 2 + Year 3 only, no TY)
- **AND** each function uses the canonical `ExtractEn` client (which
  routes to `minimax-m3` per commit `667635dfd`)

#### Scenario: 3 Layer 1 Ingestion cron assets ship at the canonical paths

- **GIVEN** the change has landed
- **WHEN** `ls cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/{primary,junior_cycle,primary_jc_combined}/defs.yaml` is run
- **THEN** all 3 defs.yaml files exist
- **AND** each is valid YAML under `uv run python3 -c "import yaml; yaml.safe_load(open('<file>').read())"`
- **AND** each uses the `CelticIngestionComponent` type with `use_local_scrapes=true` and at least 1 asset_check (per the BIEP v1 wiring pattern from commit `ccd1a7e18`)

#### Scenario: K-12 → university pipeline is now complete across 3 specs

- **GIVEN** the BIEP v1 flagship has shipped (covering Senior Cycle / Leaving Cert 15-18yo via `british-isles-education-pipeline`)
- **AND** the `ireland-primary-jc-dlt-baml` Phase 1 has shipped (covering Primary 4-12yo + Junior Cycle 12-15yo via this change)
- **WHEN** the 3 capability specs are listed
- **THEN** they collectively cover the full K-12 → university pipeline:
  - Primary (5-6yo infants + 6-12yo) ← `ireland-primary-jc-dlt-baml` (this change)
  - Junior Cycle (12-15yo) ← `ireland-primary-jc-dlt-baml` (this change)
  - Senior Cycle / Leaving Cert (15-18yo) ← `british-isles-education-pipeline` (BIEP v1 flagship)
- **AND** no student age bracket is left uncovered in the canonical spec catalogue

#### Scenario: BAML class-name collision with the legacy stages/ schemas is avoided

- **GIVEN** the legacy canonical Primary + JC schemas at `baml/education/stages/primary.baml` + `stages/junior_cycle.baml` define classes named `PrimaryLearningOutcome` / `PrimaryStrand` / `JCSubjectSpec`
- **WHEN** the new stage-specific schemas at `baml/education/primary/primary_extraction.baml` + `junior_cycle/junior_cycle_extraction.baml` are evaluated
- **THEN** all 3 classes use the `Stage` suffix (`PrimaryLearningOutcomeStage` / `PrimaryStrandStage` / `PrimaryAreaSpecStage` / `JCLearningOutcomeStage` / `JCStrandStage` / `JCSubjectSpecStage`)
- **AND** no class name collides with the legacy canonical names
- **AND** the legacy canonical schemas remain unchanged (consumed by `dlt/.../primary.py` + `junior_cycle.py`)