# Spec Delta: dagster-5-layer-component-architecture

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (dagster-5-layer-component-architecture)

The system SHALL migrate the Dagster 5-layer component architecture's Postgres-backed run history + event log storage to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 3: Dagster / DuckLake).

#### Scenario: Dagster connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/dagster/Dockerfile.dagster` env is read
- **THEN** `DUCKLAKE_POSTGRES_HOST` SHALL point at PlanetScale PG
- **AND** the `dagster_state` database SHALL be pre-created on the PlanetScale branch

#### Scenario: DuckLake tables migrate (Phase C)

- **GIVEN** the Phase C change has archived
- **WHEN** DuckLake metadata is queried
- **THEN** the underlying database SHALL be PlanetScale PG (not PlanetScale MySQL)
- **AND** the schema SHALL match the prior MySQL schema after the migration
