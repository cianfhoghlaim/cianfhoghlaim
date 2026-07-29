# Spec Delta: meaisinfhoghlaim-platform

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (meaisinfhoghlaim-platform)

The system SHALL migrate the 10 meaisínfhoghlaim sub-packages (Cognee + Logfire + per-package event log state) to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: A consumer reads the platform spec

- **GIVEN** the platform spec is opened alongside the planetscale-postgres-data-strategy umbrella
- **WHEN** they look up `cognee` / `logfire` / per-package event logs
- **THEN** they see the PlanetScale PG row in the matrix
- **AND** each sub-package SHALL read from the canonical Locket-injected secret

#### Scenario: Migration is per-package, not big-bang

- **GIVEN** the Phase B change has archived
- **WHEN** the operator inspects a sub-package
- **THEN** only the sub-package's compose.yaml + secrets.env SHALL be touched
- **AND** the platform-level commands SHALL remain unchanged
