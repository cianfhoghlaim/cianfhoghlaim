# Spec Delta: dagster-5-layer-component-architecture

## ADDED Requirements

### Requirement: Dagster DuckLake Postgres substrate — PlanetScale PG (Phase B.0 env swap)

The system SHALL migrate Dagster's DuckLake metadata backend connection to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R9 (row 3: Dagster / DuckLake, row 4: DuckLake tables).

#### Scenario: DUCKLAKE_POSTGRES_HOST env var after Phase B.0

- **GIVEN** the operator has created `dagster_state` on the PlanetScale branch
- **WHEN** `bonneagar/stacks/dagster/Dockerfile.dagster` env is read
- **THEN** `DUCKLAKE_POSTGRES_HOST` SHALL point at `infisical://dev-baile/dagster/database_url`
- **AND** `DUCKLAKE_POSTGRES_PORT` SHALL be `5432`
- **AND** `DUCKLAKE_POSTGRES_SSLMODE` SHALL be `require`
- **AND** `DUCKLAKE_POSTGRES_DB` SHALL be `dagster_state`

#### Scenario: The local dagster-postgres container stays as a fallback

- **GIVEN** Phase B.0 has shipped
- **WHEN** `bonneagar/stacks/dagster/compose.yaml` is inspected
- **THEN** the local `dagster-postgres` service SHALL still be present
- **AND** it SHALL be marked as a fallback (Phase B.1 retires it)

#### Scenario: Dagster assets read from PlanetScale PG

- **GIVEN** the Phase B.0 PR has merged
- **WHEN** a Dagster asset materializes
- **THEN** the DuckLake metadata read SHALL go to PlanetScale PG
- **AND** the BIEP lakehouse queries (which join Lance + DuckLake) SHALL continue to work