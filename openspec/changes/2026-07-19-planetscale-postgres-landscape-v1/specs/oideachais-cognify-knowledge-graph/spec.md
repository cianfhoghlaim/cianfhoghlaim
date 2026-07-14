# Spec Delta: oideachais-cognify-knowledge-graph

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (oideachais-cognify-knowledge-graph)

The system SHALL move the 5-stage cross-stage cognify + the 3 leabharlann cognify datasets' Postgres backend to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 7: cognee).

#### Scenario: Cognify datasets are reachable from PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** the cognify CLI runs
- **THEN** the cognify datasets table SHALL be in the PlanetScale PG branch
- **AND** the FalkorDB + Graphiti backends SHALL remain unchanged
- **AND** the 3 leabharlann cognify datasets (`oideachais_leabharlann`, `oideachais_official_media`, `oideachais_academic_history`) SHALL be queryable via the same REST endpoints
