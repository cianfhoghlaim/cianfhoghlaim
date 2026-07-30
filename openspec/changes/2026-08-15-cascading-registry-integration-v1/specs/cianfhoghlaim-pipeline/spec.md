# Spec delta: `cianfhoghlaim-pipeline`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
DLT pipeline spec to reference `list_dlt_sources()`.

## ADDED Requirements

### Requirement: cianfhoghlaim-pipeline MUST surface the 1963 DLT sources via list_dlt_sources()

The system SHALL update `openspec/specs/cianfhoghlaim-pipeline/spec.md`
to reference `notebooks/_shared/schema.py:list_dlt_sources()` as
the canonical way to enumerate the 1963 DLT sources (920 `@dlt.source`
+ ~4900 `@dlt.resource` decorated functions across `dlt_sources/`).

#### Scenario: list_dlt_sources returns all 1963 DLT sources

- **GIVEN** the `dlt_sources/` directory tree with 13 subtrees
  (`british_isles/`, `european_nations/`, `european_union/`, `commonwealth/`,
  `american_nations/`, `common/`, `language/`, `official_media/`, `api_sources/`,
  `filesystem/`, `jobs/`, `portfolio/`, `apple_photos/`)
- **WHEN** the operator runs
  `notebooks._shared.schema.list_dlt_sources()`
- **THEN** the 1963 DLT sources are returned as `list[dict]` with
  `{source_name, file_path, primary_key, destinations, dagster_asset}`
- **AND** each entry is consumed by the deployment control panel Tab 2

#### Scenario: cianfhoghlaim-pipeline connects to DLT destination factories

- **GIVEN** the `dlt_sources/common/destinations_cianfhoghlaim.py:get_dlt_destination()` factory
- **WHEN** the pipeline orchestrator boots
- **THEN** the canonical 4 destinations (DuckLake + DuckDB + MotherDuck + Iceberg) are wired
- **AND** the `enabled_pipelines` toggle in `deployment-choice.yaml` controls whether each pipeline runs
