# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Lakekeeper → PlanetScale PG (Phase B.0 hard switch)

The system SHALL migrate Lakekeeper from its local `postgres:16-alpine` container + `lakekeeper-migrate` companion to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R9.

#### Scenario: Lakekeeper compose.yaml after Phase B.0

- **GIVEN** the operator has created `lakekeeper` on the PlanetScale branch
- **WHEN** `bonneagar/stacks/lakekeeper/compose.yaml` is inspected
- **THEN** the local `postgres` service SHALL be absent
- **AND** the local `lakekeeper-migrate` service SHALL be absent
- **AND** the `lakekeeper` service env SHALL use `infisical://dev-baile/lakekeeper/database_url` for both `LAKEKEEPER__PG_DATABASE_URL_READ` + `_WRITE`
- **AND** `LAKEKEEPER__PG_ENCRYPTION_KEY` SHALL resolve via Locket

### Requirement: Convex → PlanetScale PG (Phase B.0 hard switch, clean start)

The system SHALL migrate Convex self-host from embedded SQLite to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R9.

#### Scenario: Convex compose.yaml after Phase B.0

- **GIVEN** the operator has created `convex_production` on the PlanetScale branch
- **AND** the self-hosted Convex deployment has no production data
- **WHEN** `bonneagar/stacks/convex/compose.yaml` is inspected
- **THEN** the local `convex-data` SQLite volume SHALL be absent
- **AND** the `backend` service env SHALL use `infisical://dev-baile/convex/database_url`
- **AND** `INSTANCE_SECRET` SHALL resolve via Locket

### Requirement: Dagster / DuckLake → PlanetScale PG (Phase B.0 env swap only)

The system SHALL migrate Dagster / DuckLake's metadata DB env var to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R9, while keeping the local `dagster-postgres` container in place as a fallback (retired in Phase B.1).

#### Scenario: Dagster Dockerfile.dagster after Phase B.0

- **GIVEN** the operator has created `dagster_state` on the PlanetScale branch
- **WHEN** `bonneagar/stacks/dagster/Dockerfile.dagster` is inspected
- **THEN** `DUCKLAKE_POSTGRES_HOST` SHALL be set to `infisical://dev-baile/dagster/database_url`
- **AND** `DUCKLAKE_POSTGRES_SSLMODE` SHALL be `require`
- **AND** the local `dagster-postgres` container SHALL remain in compose.yaml