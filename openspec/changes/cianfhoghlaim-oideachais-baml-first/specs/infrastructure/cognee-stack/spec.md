# Spec Delta — Cognee Stack (new Docker Compose)

## ADDED Requirements

### Requirement: Cognee Docker Compose Stack
The system SHALL provide a new `infrastructure/stacks/machine_learning/cognee/...` stack that brings up Cognee for the multi-stage knowledge graph.

#### Scenario: Stack Brings Up Cognee
- **GIVEN** `infrastructure/stacks/machine_learning/cognee/compose.yaml`
- **WHEN** `docker compose -f compose.yaml -f sidecar.yaml up -d` is run from the stack directory
- **THEN** the following services are brought up:
  - `cognee` (cognee-ai/cognee:latest, port 8000)
  - `postgres` (postgres:16-alpine, internal, pgvector for embeddings)
  - `locket` (the Infisical sidecar)
- **AND** the stack joins the `lakehouse_lakehouse` external network so that BAML extractions can call Cognee from the oideachais `api` and `dagster` services

#### Scenario: 6-File GOLD_STANDARD Compliance
- **GIVEN** the new cognee stack directory
- **WHEN** the directory is listed
- **THEN** it contains the 6 GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- **AND** `bun run validate-stacks` (the `stack-doctor` turbo task) passes

#### Scenario: Cognee Credentials
- **GIVEN** the cognee stack
- **WHEN** the LLM providers need to be configured
- **THEN** the stack reads `LITELLM_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` from Infisical via the Locket sidecar
- **AND** the BAML `client LiteLLM` route is the default (calls `litellm:4000` over the `lakehouse_lakehouse` network)
