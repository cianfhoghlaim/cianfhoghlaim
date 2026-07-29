# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (infrastructure-stacks)

The system SHALL consolidate the data substrates of its 94 Docker Compose stacks according to the canonical decision matrix in `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: An operator audits a stack's substrate choice

- **GIVEN** the operator opens `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7
- **WHEN** they look up `<stack>` in the 28-row matrix
- **THEN** they see the current substrate, target substrate, compatibility verdict, and env var name
- **AND** they see whether Phase B or Phase C owns the swap

#### Scenario: Phase B archives

- **GIVEN** `2026-07-XX-planetscale-postgres-migration-phase-b-v1` has archived
- **WHEN** the operator inspects `bonneagar/stacks/<stack>/compose.yaml` for an ⭐-easy stack
- **THEN** the env var SHALL point at PlanetScale PostgreSQL
- **AND** the credentials SHALL be Locket-injected from Infisical path `dev-baile/<stack>/database_url`
- **AND** the local `postgres` service SHALL be removed (or kept as a Phase B optional for fallback)
