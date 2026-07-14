# Spec Delta: agent-observability

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (agent-observability)

The system SHALL migrate the Langfuse + Logfire + MLflow + RAGAS observability stack to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: Langfuse connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/langfuse/compose.yaml` is inspected
- **THEN** `langfuse-postgres` SHALL be removed
- **AND** `DATABASE_URL` SHALL point at PlanetScale PG (per R7 row 5)

#### Scenario: MLflow connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/mlflow/compose.yaml` is inspected
- **THEN** `mlflow-postgres` SHALL be removed
- **AND** `MLFLOW_TRACKING_URI` SHALL point at PlanetScale PG (per R7 row 6)

#### Scenario: RAGAS gate queries the Phase B

- **GIVEN** the RAGAS eval runs
- **WHEN** it logs scores to MLflow
- **THEN** the trace_id correlating the Langfuse + MLflow records SHALL exist
- **AND** the data SHALL reside on PlanetScale PG (single source of truth)
