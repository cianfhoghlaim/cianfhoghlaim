# Spec Delta: dagger-pipelines

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (dagger-pipelines)

The system SHALL declare PlanetScale PG as the canonical DB substrate for the 8 Dagger build functions that depend on a Postgres backend, per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: A Dagger function introspects a Lakekeeper PG database

- **GIVEN** the Phase B change has archived
- **WHEN** the Dagger function `inspect_lakekeeper_pg` runs
- **THEN** it SHALL connect to the PlanetScale PG `lakekeeper` database
- **AND** it SHALL read the catalog tables without copying data locally
- **AND** the connection SHALL use `?sslmode=verify-full` per the umbrella spec R6
