# Spec delta: `british-isles-education-pipeline`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the 24 BIEP tables as a centralized schema view exposed
via `notebooks/_shared/schema.py:schema_introspect()`.

## ADDED Requirements

### Requirement: 24 BIEP tables are exposed via schema_introspect()

The system SHALL expose the 24 BIEP DuckDB tables (6 subjects × 4
tables: `_topics`, `_syllabus`, `_papers`, `_marking`) + the per-
jurisdiction cohort tables + the leabharlann tables via
`notebooks/_shared/schema.py:schema_introspect(conn)` returning
`list[dict]` of `{table_name, schema_name, column_name, column_type,
source: "duckdb" | "lance" | "baml"}`.

#### Scenario: schema_introspect() returns every BIEP table

- **GIVEN** the BIEP MotherDuck + DuckLake lakehouse at
  `md:cianfhoghlaim` populated
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import schema_introspect; from notebooks._shared.db import connect_md; print(len(schema_introspect(connect_md())))"`
- **THEN** the output is `>= 200` (24 BIEP tables × ~8 columns + 40+
  per-jurisdiction cohort tables + LanceDB + BAML)

#### Scenario: BIEP subject panels consume schema_introspect()

- **GIVEN** the BIEP subject panel notebooks (e.g. the 7-tab
  `notebooks/40_leaving_cert_subject_panel.py`)
- **WHEN** the operator opens the notebook
- **THEN** the column metadata is read from `schema_introspect()`,
  not from raw `DESCRIBE <table>` queries
- **AND** the column count matches the BIEP v3 contract