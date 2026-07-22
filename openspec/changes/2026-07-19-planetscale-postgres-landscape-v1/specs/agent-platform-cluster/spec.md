# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (agent-platform-cluster)

The system SHALL migrate the 8-stack agent-platform-cluster (`lakehouse` + `litellm` + `langfuse` + `mlflow` + `logfire` + `cognee` + `graphiti` + `lancedb` + 3 agent surfaces) per the canonical 28-row matrix in `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: A consumer reads the cluster spec

- **GIVEN** the cluster spec is opened alongside the planetscale-postgres-data-strategy umbrella
- **WHEN** they look up `langfuse` / `mlflow` / `cognee` / `logfire`
- **THEN** they see the PlanetScale PG row in the matrix
- **AND** the cluster member row is annotated with "target: PlanetScale PG"

#### Scenario: Cognee moves to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` is inspected
- **THEN** `cognee-postgres` SHALL be removed
- **AND** `DATABASE_URL` SHALL point at PlanetScale PG
- **AND** the `pgvector` extension SHALL be enabled on the PlanetScale branch
