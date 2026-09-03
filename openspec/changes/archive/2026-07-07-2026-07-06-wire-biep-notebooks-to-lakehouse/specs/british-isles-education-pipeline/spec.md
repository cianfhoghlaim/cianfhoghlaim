## ADDED Requirements

### Requirement: BIEP Subject Notebooks — ibis-first wiring to local lakehouse

The 6 BIEP subject marimo notebooks (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) under
`cianfhoghlaim/notebooks/04_biep_motherduck/` MUST default to the
local `bunchloch-infra` lakehouse via the `ibis.duckdb.connect()` +
`ibis.lancedb.connect()` entrypoints, with the per-subject
`ducklake_<subject>` database name. The system SHALL reject any raw
`duckdb.connect()` call in these notebooks per the ibis-first
contract from the `oideachais-marimo-dashboards` spec.

#### Scenario: Math notebook reads from local Lakekeeper via ibis

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up
  per the upgrade-4-stacks-with-infisical change
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/04_biep_motherduck/01_curriculum_educator.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("ducklake:postgres:...")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
  rather than raw SQL strings
- **AND** the operation SHALL complete within 10 seconds against the
  empty Lakekeeper (returns 0-row DataFrames, not errors)

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 6 BIEP notebooks are grepped
- **THEN** every `import duckdb` is replaced by `import ibis`
- **AND** every `duckdb.connect(uri)` call is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** the `ibis` skill is referenced in the per-notebook
  `## KCG patterns used` docstring