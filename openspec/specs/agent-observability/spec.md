# Agent Observability Capability

## Purpose

`agent-observability` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `cianfhoghlaim/observability/` (the
Langfuse + MLflow + Logfire + Datadog integration) and
`cianfhoghlaim/evaluation/ragas_pipeline.py` (the RAGAS evaluation
harness). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was renamed from `observability` to disambiguate it from
infrastructure-level observability (Prometheus + Grafana + Loki, which is
under `infrastructure-stacks`).

## Background

LLM observability, tracing, prompt management, and evaluation frameworks
for monitoring and optimizing AI systems. The full 441-line description
that was here in the old `observability` spec is in the skills
[`.agents/skills/{langfuse,mlflow,ragas,datadog}/SKILL.md`](../../.agents/skills/).
## Requirements
### Requirement: LLM call tracing

The system SHALL trace every LLM call with input, output, metadata, and
session information.

#### Scenario: Decorator-based tracing

- **GIVEN** a function decorated with `@langfuse.observe()`
- **WHEN** the function is called
- **THEN** the call is traced with input, output, and metadata to
  Langfuse

#### Scenario: Session tracking

- **GIVEN** multiple LLM calls in a session
- **WHEN** tracking session performance
- **THEN** all calls are grouped under the session in Langfuse

### Requirement: RAG evaluation

The system SHALL evaluate RAG pipelines using RAGAS metrics
(faithfulness, answer relevance, context precision, context recall).

#### Scenario: RAGAS evaluation

- **GIVEN** a RAG pipeline (e.g. `cianfhoghlaim/api/routes/search.py`)
- **WHEN** the pipeline produces a result for a query
- **THEN** the RAGAS evaluator computes the 4 metrics and stores the
  scores in MLflow

### Requirement: Continuous RAG evaluation as a Dagster asset_check

The system SHALL run the Ragas evaluator as a
`dagster.AssetCheck` on every RAG-asset materialisation, with
the Ragas thresholds (`faithfulness >= 0.8`,
`answer_relevancy >= 0.7`) enforced as quality gates.

#### Scenario: Asset check fails on Ragas regression

- **GIVEN** a RAG asset (e.g. `oideachais-curriculum-search`)
  with Ragas faithfulness baseline 0.92
- **WHEN** a new deployment changes the embedding model
- **THEN** the next asset materialisation's `AssetCheck`
  reports `faithfulness = 0.71` (< 0.8 gate)
- **AND** the asset materialisation is marked as `failed`
- **AND** a Slack notification is sent to the `#kcg-rag` channel
  via the Langfuse webhook

### Requirement: KCG MCP inventory (5 canonical servers)

The `agent-observability` skill SHALL inventory the 5
canonical KCG Model Context Protocol (MCP) servers
configured in `opencode.json` for agent integration:

| Server | Port | Purpose | Backed by |
|:--|:--|:--|:--|
| `cognee` | 8000 | Knowledge graph (cognify) | `cognee-oss` |
| `ccc` | (local CLI) | Semantic code search | `cocoindex` |
| `graphiti` | 8080 | Bi-temporal knowledge graph | `graphiti-core` |
| `langfuse` | 3000 | LLM observability + traces | `langfuse` |
| `motherduck` | (cloud) | Managed DuckDB query | `motherduck` |
| `firecrawl` | (cloud) | Web scraping | `firecrawl` |
| `browserbase` | (cloud) | Browser automation | `browserbase` |
| `chrome-devtools` | (local) | Chrome DevTools MCP | `chrome-devtools-mcp` |
| `infisical` | (cloud) | Secret management | `infisical` |

The MCP inventory lives at
`.agents/skills/agent-observability/references/mcp-servers.md`
(deep-dive reference) and is summarised in the
`agent-observability/SKILL.md` body under `§KCG MCP
inventory`.

#### Scenario: A new MCP server is added to opencode.json

- **GIVEN** a developer adds a new MCP server (e.g.
  `playwright`) to `opencode.json`
- **WHEN** they look at the KCG MCP inventory in
  `agent-observability/SKILL.md` §KCG MCP inventory
- **THEN** they see the 9 existing canonical servers and
  can decide:
  - Whether the new server fits an existing slot (e.g.
    it replaces one of the 9)
  - Or whether it's a new category
- **AND** the inventory is updated in the skill body +
  the reference file

#### Scenario: An MCP server fails to start

- **GIVEN** the dagster Cognee integration runs a
  `cognee_search` step
- **WHEN** the cognee MCP server is unreachable
- **THEN** the step fails with a clear error pointing
  to the inventory entry for `cognee` MCP server
- **AND** the langfuse trace records the failure
- **AND** the agent can fall back to direct Cognee CLI
  invocation

### Requirement: Prometheus Service Removed from litellm
The system SHALL NOT include a Prometheus service in
`bonneagar/stacks/litellm/compose.yaml` or
`bonneagar/stacks/litellm/compose.dev.yaml`. The
`bonneagar/stacks/litellm/config/prometheus.yml` scrape config
SHALL NOT exist.

#### Scenario: Compose no longer references Prometheus
- **GIVEN** `bonneagar/stacks/litellm/compose.yaml`
- **WHEN** the file is read
- **THEN** no `prometheus:` service block appears
- **AND** no `prometheus_data:` volume declaration appears
- **AND** `bun run validate-stacks` still passes for the litellm stack

#### Scenario: No Grafana / Alertmanager depends on Prometheus
- **GIVEN** the complete `bonneagar/stacks/` tree
- **WHEN** every `compose.yaml` is searched for `prometheus:9090`
  references
- **THEN** zero matches are found (no consumer depends on the
  Prometheus endpoint)

### Requirement: Logfire Stack Self-Hosted Compose
The system SHALL provide a deployable `bonneagar/stacks/logfire/`
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
- **GIVEN** `bonneagar/stacks/logfire/`
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

The system SHALL require every `secrets.env` file under
`bonneagar/stacks/` to use the canonical `infisical://dev-baile/<service>/<key>`
URI format compatible with the Locket sidecar at runtime. Jinja template
syntax (`{{ infisical:///... }}`) SHALL NOT be used.

#### Scenario: Bunchloch local Infisical compose pins the 2026-07 release

- **GIVEN** `bonneagar/stacks/infisical/compose.yaml`
- **AND** Firecrawl-verified latest stable is `infisical/infisical:v0.161.12`
  (2026-07-03, confirmed via https://github.com/Infisical/infisical/releases)
- **WHEN** the file is read
- **THEN** the `backend` service SHALL declare
  `image: infisical/infisical:v0.161.12` (NOT `:latest`)
- **AND** the `db` service SHALL declare `image: postgres:16-alpine` (NOT
  `:14-alpine`; PostgreSQL 16 is upstream-recommended)
- **AND** the `redis` service SHALL declare `image: redis:7.4-alpine` (NOT
  `:alpine`)

#### Scenario: Consumer stacks (lakehouse, litellm, mlflow, unstract) secrets.env are Locket-compatible

- **GIVEN** all 4 consumer stack `secrets.env` files:
  `bonneagar/stacks/{lakehouse,litellm,mlflow,unstract}/secrets.env`
- **WHEN** each file is grepped for `{{ infisical:///`
- **THEN** zero matches SHALL be found
- **AND** every secret reference uses the `infisical://dev-baile/...`
  URI form
- **AND** the `unstract/secrets.env` SHALL declare at minimum 20 canonical
  `infisical://dev-baile/unstract/<key>` entries covering the full
  upstream 15-service env surface

### Requirement: Blueprint Port Fidelity
Every `bonneagar/stacks/*/blueprint.yaml` SHALL declare a port
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
in `bonneagar/stacks/` has a `pangolin.yaml` file in addition to
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

## Cross-references

- [`.agents/skills/langfuse/SKILL.md`](../../.agents/skills/langfuse/SKILL.md)
- [`.agents/skills/mlflow/SKILL.md`](../../.agents/skills/mlflow/SKILL.md)
- [`.agents/skills/ragas/SKILL.md`](../../.agents/skills/ragas/SKILL.md)
- [`.agents/skills/datadog/SKILL.md`](../../.agents/skills/datadog/SKILL.md)
- [`cianfhoghlaim/observability/`](../../cianfhoghlaim/observability/) (the integration module)
- [`cianfhoghlaim/evaluation/`](../../cianfhoghlaim/evaluation/) (RAGAS pipeline)
