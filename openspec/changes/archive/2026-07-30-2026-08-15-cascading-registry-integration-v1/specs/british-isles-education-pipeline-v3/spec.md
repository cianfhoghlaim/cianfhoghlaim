# Spec delta: `british-isles-education-pipeline-v3`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
BIEP v3 flagship spec to reference the schema introspection helpers.

## ADDED Requirements

### Requirement: BIEP v3 MUST expose its 24 tables via schema_introspect

The system SHALL update `openspec/specs/british-isles-education-pipeline-v3/spec.md`
to reference `notebooks/_shared/schema.py:schema_introspect_full(conn)`
as the canonical way to enumerate the 24 BIEP tables (6 subjects ×
4 tables: `_topics` / `_syllabus` / `_papers` / `_marking`).

#### Scenario: schema_introspect surfaces the 24 BIEP tables

- **GIVEN** the BIEP MotherDuck + DuckLake lakehouse at `md:cianfhoghlaim`
- **WHEN** the operator runs
  `notebooks._shared.schema.schema_introspect_full(connect_md())`
- **THEN** the 24 BIEP tables are surfaced with column metadata
- **AND** the BIEP dashboards (`19_*.py` through `23_*.py`) consume this API

#### Scenario: BIEP v3 connects to the deployment control panel

- **GIVEN** the 5-tab marimo control panel at `notebooks/00_control_panel.py`
- **WHEN** the BIEP v3 operator opens Tab 2 "Pipelines"
- **THEN** the 10 jurisdiction pipelines (`ireland_jurisdiction_pipeline` etc.) appear
- **AND** the operator can toggle each one on/off via `deployment-choice.yaml:enabled_pipelines`
