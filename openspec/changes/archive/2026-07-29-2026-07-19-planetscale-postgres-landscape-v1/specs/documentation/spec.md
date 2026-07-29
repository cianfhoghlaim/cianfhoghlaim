# Spec Delta: documentation

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (documentation)

The system SHALL cross-reference the PlanetScale Postgres Data Strategy umbrella in the canonical `docs/` frontmatter schema so that any future spec + ADR + operator doc that mentions a Postgres connection can resolve the substrate decision quickly.

#### Scenario: An agent searches docs for a Postgres connection

- **GIVEN** an agent searches `docs/` for "PlanetScale postgres"
- **WHEN** they read the relevant doc
- **THEN** the doc SHALL cross-reference `openspec/specs/planetscale-postgres-data-strategy/spec.md`
- **AND** the doc SHALL cross-reference `openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md`
- **AND** the operator SHALL be able to pick the substrate from R7 in 1 hop
