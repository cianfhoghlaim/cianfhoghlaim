# Spec Delta: cianfhoghlaim-pipeline

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (cianfhoghlaim-pipeline)

The system SHALL migrate the main 50-requirement cianfhoghlaim-pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) such that its DuckLake metadata backend moves from PlanetScale MySQL to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 4: DuckLake tables).

#### Scenario: DuckLake metadata backend moves from MySQL → PG

- **GIVEN** the Phase C change has archived
- **WHEN** DuckLake queries run
- **THEN** the metadata backend SHALL be PlanetScale PG (per the umbrella spec R6 conventions: PgBouncer pool or direct depending on the consumer)
- **AND** the prior PlanetScale MySQL connection SHALL be retired

#### Scenario: The oideachais lakehouse rows in R7

- **GIVEN** the operator opens `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7
- **WHEN** they look for the lakehouse rows
- **THEN** Lakekeeper (row 1), Dagster / DuckLake (row 3), and DuckLake tables (row 4) SHALL all be present
- **AND** each row SHALL reference the Phase B or Phase C change that performs the swap
