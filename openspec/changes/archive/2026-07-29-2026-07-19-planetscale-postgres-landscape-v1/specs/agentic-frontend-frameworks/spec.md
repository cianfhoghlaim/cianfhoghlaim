# Spec Delta: agentic-frontend-frameworks

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (agentic-frontend-frameworks)

The system SHALL migrate the 7-layer agentic-web stack's Convex self-host DB to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 2: Convex).

#### Scenario: Convex connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/convex/compose.yaml` is inspected
- **THEN** `POSTGRES_URL` SHALL be set
- **AND** `POSTGRES_URL` SHALL resolve via Locket to PlanetScale PG
- **AND** the `convex-` prefixed schema SHALL be pre-created on the PlanetScale branch

#### Scenario: Hono + oRPC env vars

- **GIVEN** the Phase B change has archived
- **WHEN** the leaving-cert app starts
- **THEN** the per-subject Hono routes' `DATABASE_URL` env var SHALL point at PlanetScale PG (when they add Postgres connections in a follow-up)
- **AND** no local Postgres container SHALL be required for the leaving-cert app's data plane
