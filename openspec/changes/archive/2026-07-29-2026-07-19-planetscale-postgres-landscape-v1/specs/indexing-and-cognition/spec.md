# Spec Delta: indexing-and-cognition

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (indexing-and-cognition)

The system SHALL migrate the CCC v1 code-search + Cognee knowledge-graph host to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 7: Cognee + row 16: pgvector).

#### Scenario: Cognee uses PlanetScale pgvector

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` is inspected
- **THEN** `DATABASE_URL` SHALL point at PlanetScale PG
- **AND** `pgvector` SHALL be enabled on the PlanetScale branch
- **AND** the CCC vector indexing pipeline SHALL continue to use pgvector (no behavioural change)
