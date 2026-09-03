# `agent-memory-systems` capability spec — delta

## ADDED Requirements

### Requirement: All audited stacks use canonical Infisical URI form
The system SHALL migrate every audited stack's `secrets.env` from the
legacy Jinja `{{ infisical:///key_name }}` form to the Locket-canonical
`infisical://dev-baile/<service>/key_name` form. The
`scripts/stack-doctor.sh` validator SHALL accept both forms during the
migration period.

#### Scenario: mlflow stack secrets.env uses canonical form
- **GIVEN** `infrastructure/stacks/mlflow/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/mlflow/<key>`
  (canonical Locket form)

#### Scenario: lakehouse stack secrets.env uses canonical form
- **GIVEN** `infrastructure/stacks/lakehouse/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/lakehouse/<key>`

#### Scenario: graphiti stack secrets.env uses canonical form
- **GIVEN** `infrastructure/stacks/graphiti/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/graphiti/<key>`

#### Scenario: falkordb stack secrets.env uses canonical form
- **GIVEN** `infrastructure/stacks/falkordb/secrets.env`
- **WHEN** every `{{ infisical:///` line is read
- **THEN** the value matches the regex `infisical://dev-baile/falkordb/<key>`

#### Scenario: stack-doctor validator accepts both URI forms
- **GIVEN** any stack with secrets.env using either form
- **WHEN** `bun run validate-stacks` runs
- **THEN** the validator reports zero "no infisical:// refs" warnings
  for that stack

### Requirement: Blueprint ports match the container's internal port
The system SHALL ensure every `blueprint.yaml` `destination-port`
matches the container's internal port (the right side of the
`host:container` mapping in `compose.yaml`), not the host port.

#### Scenario: langfuse blueprint port is 3000
- **GIVEN** `infrastructure/stacks/langfuse/blueprint.yaml`
- **AND** `infrastructure/stacks/langfuse/compose.yaml` web service
  maps `3001:3000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.langfuse.destination-port` is `3000`
  (the container's internal port)

#### Scenario: graphiti blueprint port is 8000
- **GIVEN** `infrastructure/stacks/graphiti/blueprint.yaml`
- **AND** `infrastructure/stacks/graphiti/compose.yaml` graph
  service exposes `8000:8000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.graphiti.destination-port` is `8000`

#### Scenario: cognee blueprint port is 8000
- **GIVEN** `infrastructure/stacks/cognee/blueprint.yaml`
- **AND** `infrastructure/stacks/cognee/compose.yaml` exposes
  `8100:8000`
- **WHEN** the blueprint is read
- **THEN** `private-resources.cognee.destination-port` is `8000`
  (unchanged from the original — the audit incorrectly suggested
  8100; the host port is 8100 but the container listens on 8000)

### Requirement: All audited stacks have a pangolin.yaml
The system SHALL provide a `pangolin.yaml` (6-label private-resource
form) for every web-facing stack: `mlflow`, `langfuse`, `lakehouse`,
`graphiti`, `falkordb`, `cognee`. The `logfire` stack is exempt
because its UI is SaaS at `https://logfire.pydantic.dev`.

#### Scenario: 6 new pangolin.yaml files exist
- **GIVEN** the 6 stacks listed above
- **WHEN** each `infrastructure/stacks/<name>/pangolin.yaml` is read
- **THEN** it contains a `pangolin.private-resources.<name>` block
  with all 6 labels: `name`, `mode`, `full-domain`,
  `destination-port`, `protocol`, `roles[0]`

#### Scenario: stack-doctor reports zero "no pangolin.yaml" warnings
- **GIVEN** the 6 web-facing stacks
- **WHEN** `bun run validate-stacks` runs
- **THEN** the validator reports zero "missing pangolin.yaml"
  warnings for these 6 stacks

### Requirement: Datadog Python observability is a graceful no-op
The system SHALL treat Datadog APM + LLMObs as an opt-in optional
backend. When the `ddtrace` / `datadog` packages are not installed
(they are not in the production image), the `setup_datadog_apm` and
`setup_datadog_llmobs` functions SHALL be no-ops. The Pydantic Settings
`datadog_enabled` field SHALL default to `False` so the no-op path is
the canonical default.

#### Scenario: setup_datadog_apm is a no-op when ddtrace is missing
- **GIVEN** a Python service that imports
  `from oideachais.observability.fastapi_middleware import setup_datadog_apm`
- **AND** the `ddtrace` package is not installed
- **WHEN** `setup_datadog_apm(app)` is called at app startup
- **THEN** the function returns `None` without raising

#### Scenario: unified_tracer datadog_enabled default is False
- **GIVEN** `sruth/oideachais/observability/unified_tracer.py`
- **WHEN** the `datadog_enabled` parameter is read
- **THEN** the default value is `False` (not `True`)

#### Scenario: Pydantic Settings datadog_enabled default is False
- **GIVEN** `sruth/oideachais/config/base.py` or
  `sruth/meaisinfhoghlaim/ocr/config/base.py`
- **WHEN** the `datadog_enabled` field default is read
- **THEN** the value is `Field(default=False)`

#### Scenario: logfire is the canonical Python tracing backend
- **GIVEN** the observability skill
  `.agents/skills/agent-observability/SKILL.md`
- **WHEN** "Layer 1: Traces" is read
- **THEN** it references Langfuse + Logfire (not Datadog APM + LLMObs)
