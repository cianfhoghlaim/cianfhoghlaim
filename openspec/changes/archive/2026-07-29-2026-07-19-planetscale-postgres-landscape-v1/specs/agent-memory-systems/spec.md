# Spec Delta: agent-memory-systems

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (agent-memory-systems)

The system SHALL migrate the Cognee + Graphiti + LanceDB + FalkorDB + Memgraph memory backends per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Cognee connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` is inspected
- **THEN** the local Postgres SHALL be removed
- **AND** `DATABASE_URL` SHALL point at PlanetScale PG
- **AND** the `pgvector` extension SHALL be enabled on the PlanetScale branch

#### Scenario: FalkorDB, Memgraph, Graphiti, LanceDB continuity

- **GIVEN** the change has archived
- **WHEN** the per-stack compose.yaml is inspected for FalkorDB / Memgraph
- **THEN** FalkorDB and Memgraph (key-value / graph stores) SHALL remain on their specialised backends
- **AND** only the relational metadata stores SHALL move to PlanetScale PG
- **AND** the decision row in the umbrella spec R7 SHALL reflect this
