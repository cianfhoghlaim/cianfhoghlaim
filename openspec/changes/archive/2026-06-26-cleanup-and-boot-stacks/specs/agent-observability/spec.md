## REMOVED Requirements

### Requirement: Datadog APM + LLMObs
**Reason**: User decision (2026-06-26) consolidates observability around
the Langfuse + MLflow + Logfire tri-split. The Datadog agents on
`arm1-oci` (configured in
`infrastructure/komodo/procedures/auto-deploy-stacks.toml` lines
228-280) require a Datadog license + intake that KCG does not
currently use; the application code in
`sruth/oideachais/observability/unified_tracer.py` no-ops when
`DD_APM_ENABLED` is unset. The `.agents/skills/datadog/SKILL.md`
umbrella is retired.

**Migration**: All Datadog references are removed from
`.agents/skills/agent-observability/SKILL.md` (description
frontmatter, §1 layer diagram, §1 prose section, cross-reference
list) and the four Datadog agent stacks in
`infrastructure/komodo/procedures/auto-deploy-stacks.toml` are
deleted. The `DD_APM_ENABLED=true` env entry in
`infrastructure/komodo/procedures/crypteolas-pipeline.toml:40` is
removed. Existing Datadog agents on `arm1-oci` (if deployed) can be
left in place until decommissioned by the OCI operator.

## ADDED Requirements

### Requirement: Prometheus Service Removed from litellm
The system SHALL NOT include a Prometheus service in
`infrastructure/stacks/litellm/compose.yaml` or
`infrastructure/stacks/litellm/compose.dev.yaml`. The
`infrastructure/stacks/litellm/config/prometheus.yml` scrape config
SHALL NOT exist.

#### Scenario: Compose no longer references Prometheus
- **GIVEN** `infrastructure/stacks/litellm/compose.yaml`
- **WHEN** the file is read
- **THEN** no `prometheus:` service block appears
- **AND** no `prometheus_data:` volume declaration appears
- **AND** `bun run validate-stacks` still passes for the litellm stack

#### Scenario: No Grafana / Alertmanager depends on Prometheus
- **GIVEN** the complete `infrastructure/stacks/` tree
- **WHEN** every `compose.yaml` is searched for `prometheus:9090`
  references
- **THEN** zero matches are found (no consumer depends on the
  Prometheus endpoint)

### Requirement: Logfire Stack Self-Hosted Compose
The system SHALL provide a deployable `infrastructure/stacks/logfire/`
stack with at minimum `compose.yaml`, `blueprint.yaml`,
`secrets.env`, and `sidecar.yaml`. Pydantic Logfire is SaaS-only
(https://logfire.pydantic.dev) and does not publish a
self-hostable Logfire-server Docker image as of 2026-06-26; the
local service SHALL therefore deploy an OpenTelemetry Collector
that forwards OTLP traces to Logfire cloud. Because the local
collector only exposes OTLP gRPC/HTTP ports (no local HTTP UI),
`pangolin.yaml` SHALL be intentionally omitted and the absence
SHALL be documented in the stack README.

#### Scenario: Logfire compose file exists and parses
- **GIVEN** `infrastructure/stacks/logfire/`
- **WHEN** `bun run validate-stacks` runs
- **THEN** the logfire stack is recognised as a valid 5-file
  GOLD_STANDARD stack (compose + sidecar + secrets + blueprint + README)
- **AND** the compose file parses without error
- **AND** the stack README explicitly states why `pangolin.yaml`
  is absent and where the user-facing UI lives

### Requirement: OpenCode Configuration Single Source
The system SHALL have exactly one OpenCode MCP configuration file:
`opencode.json` at the repo root. The legacy `.opencode.yaml`
alternative configuration SHALL NOT exist.

#### Scenario: Runtime ignores any alternate config
- **GIVEN** `opencode.json` at repo root declares MCP servers
- **WHEN** an agent boots
- **THEN** it reads `opencode.json` only
- **AND** no `.opencode.yaml` alternative config exists at repo root

### Requirement: Infisical URI Format Conformance
Every `secrets.env` file in `infrastructure/stacks/` SHALL use the
canonical `infisical://dev-baile/<service>/<key>` URI format
compatible with the Locket sidecar at runtime. Jinja template
syntax (`{{ infisical:///... }}`) SHALL NOT be used.

#### Scenario: All 102 secrets.env files are Locket-compatible
- **GIVEN** every `infrastructure/stacks/*/secrets.env`
- **WHEN** the file is grepped for `{{ infisical:///`
- **THEN** zero matches are found
- **AND** every secret reference uses the `infisical://dev-baile/...`
  URI form

### Requirement: Blueprint Port Fidelity
Every `infrastructure/stacks/*/blueprint.yaml` SHALL declare a port
that matches the corresponding `compose.yaml` host port for the
primary service. The blueprint is documentation-only (Komodo
consumes `pangolin.yaml`), but the declared port SHALL be accurate.

#### Scenario: langfuse / graphiti / cognee ports are consistent
- **GIVEN** the 3 stacks with documented port mismatches
  (langfuse, graphiti, cognee)
- **WHEN** `blueprint.yaml` is read
- **THEN** the declared port matches the `compose.yaml` `ports:`
  entry for the primary service

### Requirement: MCP Command Path Correctness
Every `opencode.json` `mcp.<server>.command` array SHALL resolve to a
real file at the declared path. No command SHALL reference a path
that does not exist on disk.

#### Scenario: croilar-devtools MCP command resolves
- **GIVEN** `opencode.json` `mcp.croilar-devtools.command`
- **WHEN** the command path is resolved from the repo root
- **THEN** the file exists
- **AND** the bun runtime can load it without `MODULE_NOT_FOUND`

### Requirement: Pangolin Config Per Operational Stack
The system SHALL require that every operational Docker Compose stack
in `infrastructure/stacks/` has a `pangolin.yaml` file in addition to
`blueprint.yaml`, so that Komodo can apply the public/private
resource routes via the `file_paths` field. The blueprint is
documentation; the pangolin file is the source of truth for the
resource declaration.

#### Scenario: All 7 audited stacks have pangolin.yaml
- **GIVEN** the 7 stacks audited (mlflow, logfire, langfuse,
  lakehouse, graphiti, falkordb, cognee)
- **WHEN** each directory is listed
- **THEN** a `pangolin.yaml` file is present in each

### Requirement: LLM Observability Tri-Split
The system SHALL wire LLM observability through three orthogonal
destinations:
- **Langfuse v3** for LLM call traces (cost + prompt management)
- **MLflow** for ML experiment tracking + model registry + fine-tune
  lineage
- **Logfire (Pydantic)** for Python-level structured tracing

The system SHALL NOT depend on Datadog APM or LLMObs. All four
Datadog agent stacks configured in
`infrastructure/komodo/procedures/auto-deploy-stacks.toml` lines
228-280 SHALL be removed. The `.agents/skills/datadog/SKILL.md`
file SHALL NOT exist.

#### Scenario: unified_tracer.py fans out to 3 destinations
- **GIVEN** an LLM call wrapped in the `unified_tracer` decorator
- **WHEN** the call completes
- **THEN** a Langfuse trace is written with input/output/cost
- **AND** an MLflow experiment metric is logged if `experiment_name`
  is set
- **AND** a Logfire span is written if `LOGFIRE_TOKEN` is non-empty
- **AND** no Datadog dependency is imported

#### Scenario: Datadog references removed from agent-observability skill
- **GIVEN** `.agents/skills/agent-observability/SKILL.md`
- **WHEN** the file is read
- **THEN** the description frontmatter does not mention Datadog
- **AND** the 5-layer diagram replaces "Layer 1: Traces (Datadog
  APM + LLMObs)" with "Layer 1: Traces (Langfuse + Logfire)"
- **AND** no cross-reference to `.agents/skills/datadog/SKILL.md`
  exists

#### Scenario: Datadog stacks removed from Komodo procedures
- **GIVEN** `infrastructure/komodo/procedures/auto-deploy-stacks.toml`
- **WHEN** the file is searched for `datadog-`
- **THEN** zero matches are found
- **AND** the four Datadog stack definitions (oci, macbook, oracle,
  +1) are deleted
