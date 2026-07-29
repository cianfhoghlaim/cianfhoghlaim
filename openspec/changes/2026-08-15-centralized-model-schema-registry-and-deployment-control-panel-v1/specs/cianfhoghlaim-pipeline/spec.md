# Spec delta: `cianfhoghlaim-pipeline`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the DLT sources registry exposure via
`notebooks/_shared/schema.py:list_dlt_sources()`.

## ADDED Requirements

### Requirement: DLT sources registry is exposed via list_dlt_sources()

The system SHALL expose all 920 `@dlt.source` decorated functions
+ their primary keys + their destinations via
`notebooks/_shared/schema.py:list_dlt_sources()` returning
`list[dict]` of `{source_name, primary_key, destinations, dagster_asset}`.

#### Scenario: list_dlt_sources() returns every DLT source

- **GIVEN** the `dlt_sources/` directory with 920 `@dlt.source`
  decorated functions
- **WHEN** the operator runs
  `python3 -c "from notebooks._shared.schema import list_dlt_sources; print(len(list_dlt_sources()))"`
- **THEN** the output is `>= 920`

#### Scenario: DLT destinations are centralized

- **GIVEN** the 4 DLT destination factories in
  `dlt_sources/common/destinations_cianfhoghlaim.py` +
  `destinations_tuatha.py` + `named_destinations.py` +
  `motherduck_options.py` + `iceberg_options.py`
- **WHEN** the operator runs `bun run cianfhoghlaim pipelines list`
- **THEN** the output groups pipelines by destination
  (DuckLake, DuckDB local, MotherDuck `md:oideachais`,
  MotherDuck `md:cianfhoghlaim`, Iceberg opt-in)
- **AND** the destination counts match the audit
  (DuckLake ~700, DuckDB local ~30, MotherDuck `md:cianfhoghlaim`
  per-jurisdiction + 14 from `md:oideachais`, Iceberg 0 wired)