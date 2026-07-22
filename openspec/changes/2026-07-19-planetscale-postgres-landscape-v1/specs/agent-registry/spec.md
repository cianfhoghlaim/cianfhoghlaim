# Spec Delta: agent-registry

## ADDED Requirements

### Requirement: PlanetScale Postgres Centralisation (agent-registry)

The system SHALL migrate the 12-agent registry's observability substrate (logfire + langfuse) to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (rows 5 + 28).

#### Scenario: A consumer reads the registry

- **GIVEN** the registry spec is opened
- **WHEN** they look at the per-agent metadata
- **THEN** the `system_prompt` reference SHALL be preserved
- **AND** the observability substrate for the registry's traces SHALL point at PlanetScale PG (logfire database)
