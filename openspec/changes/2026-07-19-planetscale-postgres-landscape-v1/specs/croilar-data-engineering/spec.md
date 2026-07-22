# Spec Delta: croilar-data-engineering

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (croilar-data-engineering)

The system SHALL migrate the Croílár data-engineering stack (`Dagster + DLT + CocoIndex + BAML` for the 3 personas) to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Croilar Postgres targets PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/croilar/croilar-postgres/compose.yaml` is inspected
- **THEN** the Croilar Postgres SHALL be removed (or kept as a Phase B optional fallback)
- **AND** the croilar persona schemas SHALL migrate to PlanetScale PG

#### Scenario: Croilar credentials via Locket

- **GIVEN** the operator configures the Croilar persona
- **WHEN** the stack starts
- **THEN** Locket SHALL inject `DATABASE_URL` from `infisical://dev-baile/croilar/database_url`
