# Spec Delta: croilar-portfolio

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (croilar-portfolio)

The system SHALL migrate the Croílár public TanStack Start site + its companion `croilar-hono-api` stack's Postgres storage to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Croilar Hono API connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/croilar/croilar-hono-api/compose.yaml` is inspected
- **THEN** the Croilar persona state SHALL move from `croilar-postgres` to PlanetScale PG
- **AND** the cron persona vault keys SHALL continue to encrypt the Postgres-resident assets

#### Scenario: Croilar portfolio remains stateless

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/croilar/web` is inspected
- **THEN** no new database connection SHALL be added (the portfolio is intended to be read-mostly; static build + CDN)
