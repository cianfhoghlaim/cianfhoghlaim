## ADDED Requirements

### Requirement: Dagster sensor coverage for the 5 BAML stage templates

The system SHALL add Dagster sensors for the 5 BAML stage templates
so that when the BAML source changes, the corresponding Dagster
assets re-materialize.

The reason: per the 5-layer Dagster component architecture, Layer
2 (Materials) wraps BAML extraction. When BAML changes, the Dagster
sensors trigger the materials re-materialization.

#### Scenario: Every BAML template has a Dagster sensor

- **WHEN** `mise run dagster:sensor-job-coverage` runs
- **THEN** all 5 BAML stage templates MUST have a corresponding
  Dagster `@sensor` declaration
- **AND** the sensor's `job_name` matches the canonical asset job

### Requirement: BAML extraction → Dagster asset chain

The system SHALL wire the 5 lc6 BAML functions into the 42 Dagster
assets at `orchestration/defs/2_materials/england_education/` so each
asset materialization triggers the corresponding BAML extraction.

#### Scenario: Every Dagster asset calls BAML

- **WHEN** the operator runs `mise run dagster:asset-materialize --select "*england_education"`
- **THEN** each of the 42 England education Dagster assets
  materialises by calling at least 1 BAML function via
  `BAMLFunctionTool`