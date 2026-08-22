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

- **GIVEN** a RAG pipeline (e.g. `cianfhoghlaim/web/hono-api/src/routes/search.py`)
- **WHEN** the pipeline produces a result for a query
- **THEN** the RAGAS evaluator computes the 4 metrics and stores the
  scores in MLflow

### Requirement: Continuous RAG evaluation as a Dagster asset_check

The system SHALL run the Ragas evaluator as a
`dagster.AssetCheck` on every RAG-asset materialisation, with
the Ragas thresholds (`faithfulness >= 0.8`,
`answer_relevancy >= 0.7`) enforced as quality gates.

#### Scenario: Asset check fails on Ragas regression

- **GIVEN** a RAG asset (e.g. `cianfhoghlaim-curriculum-search`)
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

### Requirement: PlatformTracer facade

The system SHALL provide a `PlatformTracer` facade at
`cianfhoghlaim/observability/platform_tracer.py` that wraps the
3 observability destinations (Langfuse + MLflow + Logfire) per
the LLM Observability Tri-Split requirement. The facade SHALL be
re-exported from `cianfhoghlaim/observability/__init__.py` so
agent code can `from cianfhoghlaim.observability import
PlatformTracer, get_tracer`.

The facade SHALL provide:

- `PlatformTracer.span(name, span_type, metadata) -> context
  manager yielding a `PlatformSpan`
- `PlatformTracer.observe(name=, span_type=) -> decorator`
- `PlatformTracer.flush()` and `PlatformTracer.shutdown()` no-ops
  that delegate to the per-backend modules
- `PlatformTracer.backend_state(backend: str) -> BackendState`
- `PlatformTracer.active_backends() -> list[str]`
- `PlatformTracer.probe_backends(force=False)` for health checks
  with 60s caching

The facade SHALL be **non-raising** — every destination call is
wrapped in `try/except` so the calling agent never sees an
observability failure.

#### Scenario: span decorator wraps the Langfuse + MLflow + Logfire cascade

- **GIVEN** an LLM call wrapped in `@tracer.observe("my_function", span_type="tool")`
- **WHEN** the function is called
- **THEN** the call is traced to Langfuse (primary) via
  `create_generation` or `log_llm_call`
- **AND** an MLflow metric `duration_ms` is logged
- **AND** a Logfire span is written (when `LOGFIRE_TOKEN` is set)
- **AND** no exception escapes to the agent

#### Scenario: PlatformSpan metadata is merged idempotently

- **GIVEN** a `with tracer.span("agent.curriculum_call") as span:`
- **WHEN** the agent does `span.set_metadata({"subject": "maths"})`
- **THEN** `span.metadata["subject"] == "maths"`
- **AND** any subsequent `set_metadata({"k": 1})` augments
  rather than overwrites

### Requirement: Langfuse 5xx falls back to MLflow (5xx → Logfire cascade)

The system SHALL fall back from Langfuse → MLflow → Logfire when
each upstream destination raises a 5xx (or network) error.
Concretely:

When `PlatformTracer._flush_to_langfuse()` raises an
`httpx.HTTPStatusError` (5xx), the tracer SHALL mark Langfuse
as `BackendState.DOWN_5XX`, re-route the current span to MLflow,
and keep the same Tracer instance for subsequent calls (so the
fallback is sticky until `probe_backends(force=True)` succeeds).

When the MLflow destination also raises, the tracer SHALL
fall back to Logfire as a last-resort destination. The cascade
order MUST be: **Langfuse (primary) → MLflow (5xx fallback) →
Logfire (5xx last-resort)**.

#### Scenario: Langfuse returns 5xx → reroute to MLflow

- **GIVEN** the Langfuse backend probe returns
  `BackendState.DOWN_5XX`
- **AND** MLflow is reachable
- **WHEN** `with tracer.span("agent.curriculum_call"): pass`
  runs
- **THEN** no trace is written to Langfuse
- **AND** an MLflow metric is logged
- **AND** `active_backends()` returns `["mlflow", "logfire"]`
  (Langfuse excluded)

#### Scenario: All backends down → graceful no-op

- **GIVEN** all 3 backends probe as DOWN
- **WHEN** `with tracer.span("agent.curriculum_call"): pass`
  runs
- **THEN** no trace is written anywhere
- **AND** the surrounding block continues normally
- **AND** a `logger.warning("PlatformTracer: ... flush failed: ...")`
  is emitted

### Requirement: 5-layer observability hooks via `agents/observability_hooks.py`

The system SHALL provide a shared `agents/observability_hooks.py`
module containing the 5-layer observability wiring:

- **Layer 1**: `LangfuseLogger` — wraps the canonical
  `cianfhoghlaim.observability.langfuse_config.langfuse_trace`
  context manager with per-agent `trace_name` injection.
- **Layer 2**: `LogfireSpan` — wraps the canonical
  `cianfhoghlaim.observability.logfire_config.logfire_span`
  with per-agent span metadata.
- **Layer 3**: `MLflowTracker` — wraps the canonical
  `cianfhoghlaim.observability.mlflow_tracker.log_run`
  with per-agent experiment tagging.
- **Layer 4**: `RAGASScorer` — Dagster asset_check for
  RAGAS trace-based metrics.
- **Layer 5**: `structlogLogger` — structured JSON logging
  with per-agent context.

The `attach_observability(wiring)` function SHALL wire the
5 layers for a given `AgentFleetWiring` instance.

#### Scenario: `attach_observability` wires all 5 layers

- **GIVEN** an `AgentFleetWiring` for `curriculum_agent`
- **WHEN** `wire = attach_observability(wiring)`
- **THEN** the returned `wire` SHALL have:
  - `langfuse_wired=True` and `langfuse_trace_name` populated
  - `logfire_wired=True` and `logfire_span_name` populated
  - `mlflow_wired=True` and `mlflow_experiment_name` populated
  - `ragas_scorer_wired=True` and `ragas_dataset_name` populated
  - `structlog_wired=True` and `structlog_context` populated

#### Scenario: 5-layer observability contract verified

- **GIVEN** the 12 agents are wired via `agents/observability_hooks.py`
- **WHEN** `python -c "from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract; print(verify_5_layer_contract())"`
- **THEN** the output SHALL be `True`
- **AND** all 12 agents SHALL have all 5 layers wired

### Requirement: Observability contract verification

The system SHALL provide a `verify_observability_contract(agent_name)`
function that asserts the 5-layer observability contract for
a given agent. The function SHALL return `True` if all 5
layers are wired, `False` otherwise.

The `verify_observability_contract()` function (no args) SHALL
return a dict mapping `agent_name → bool` for all 12 agents.

#### Scenario: `verify_observability_contract` returns True for a wired agent

- **GIVEN** the `curriculum_agent` is wired via
  `agents/observability_hooks.py`
- **WHEN** `verify_observability_contract("curriculum_agent")`
- **THEN** the function SHALL return `True`

#### Scenario: `verify_observability_contract` returns a dict for all 12 agents

- **GIVEN** the 12 agents are wired via `agents/observability_hooks.py`
- **WHEN** `verify_observability_contract()`
- **THEN** the result SHALL be a dict with 12 keys
- **AND** all 12 values SHALL be `True`

### Requirement: Logfire collector fan-out to Langfuse + Logfire

The local `logfire-otel` OpenTelemetry collector MUST be configured to
forward every received trace to BOTH backends. The collector MUST include
BOTH of the following exporters in its `traces` pipeline:

1. **Logfire cloud** (the existing destination, via the `logfire`
   exporter + `LOGFIRE_TOKEN`)
2. **Langfuse** (NEW destination, via the `otlphttp` exporter pointing at
   `http://langfuse-web:3000/api/public/otel`, authenticated with the
   same `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` pair used by other
   consumers)

This produces a single pane of glass: every trace that lands in the
collector appears in both Logfire (for SQL-based trace querying) and
Langfuse (for LLM cost + prompt management + score-based eval).

The collector MUST resolve `LANGFUSE_PUBLIC_KEY` and
`LANGFUSE_SECRET_KEY` from its own `secrets.env` template (Locket-injected
at container start).

#### Scenario: a Dagster run traces to both backends

```
$ otelcol-cli --endpoint http://logfire-otel:4317 trace send \
    --service dagster --run-id abc123 --duration 4.2s
[dagster] sent to logfire    → https://logfire.pydantic.dev → trace=abc123
[dagster] sent to langfuse   → https://langfuse.cianfhoghlaim.ie → trace=abc123
```

#### Scenario: collector health is green; both exporters are wired

```
$ curl http://logfire-otel:8888/health/status
{"status":"Server available","pipelines":{"traces":{
  "exporters": ["logfire", "langfuse", "debug"],
  "receivers": ["otlp"],
  "processors": ["memory_limiter", "resource/logfire_metadata", "batch"]
}}}
```

### Requirement: OTLP export from every memory + observability backend

MUST emit OpenTelemetry traces. The system MUST emit these traces from
every backend service that performs LLM calls or FastAPI request serving
or experiment tracking to `http://logfire-otel:4317` via the standard
`OTEL_EXPORTER_OTLP_ENDPOINT` + `OTEL_SERVICE_NAME` env contract. The
system MUST additionally export cost + prompt metadata to Langfuse via
`LANGFUSE_HOST` + `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`.

Specifically, every one of the following services MUST set both env vars
in its `compose.yaml`:

| Service | Stack | OTEL_SERVICE_NAME value |
|:--|:--|:--|
| graphiti | `bonneagar/stacks/graphiti/` | `graphiti` |
| cognee | `bonneagar/stacks/cognee/` | `cognee` |
| mlflow | `bonneagar/stacks/mlflow/` | `mlflow` |
| agent-os (all 4 instances) | `bonneagar/stacks/agent-os/` | `agent-os-<svc>` (oideachais / crypteolas / browser / croilar) |

These services ALSO MUST set `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, and
`LANGFUSE_SECRET_KEY` so the SDK-side trace decorator (where used) can
attach cost + prompt metadata to the Langfuse project.

#### Scenario: graphiti FastAPI requests appear in Langfuse

```
# Before this change: graphiti emits NO traces (zero coverage)
# After this change:
$ curl -X POST http://graphiti:8000/entities \
    -d '{"name": "Cú Chulainn", "kind": "deity"}'
[graphiti] 201 Created
  → trace_id=abc123 → logfire (via OTLP fanout)
                   → langfuse (via OTLP fanout)
                   → both show the entity extraction + LLM call cost
```

#### Scenario: 4 AgentOS instances trace to the agent-os-* Langfuse project

```
$ curl http://oideachais-agentos:7777/health
[oideachais-agentos] 200 OK
  → trace_id=abc123 → logfire (via OTLP)
                   → langfuse project=agent-os (project_id=ps_aXYZ123)
                   → langfuse cost dashboard records $0.0009 LLM call
```

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

### Requirement: agent-observability MUST include lint:registry in the observability stack

The system SHALL update `openspec/specs/agent-observability/spec.md`
to include `scripts/registry_audit.py` (`mise run lint:registry`) as
the 6th layer of the observability stack (alongside Langfuse, MLflow,
RAGAS, Logfire, and the existing 5-layer sync_health sensor).

#### Scenario: registry_drift_count flows through sync_health metadata

- **GIVEN** the new `_get_registry_drift_count()` helper in `orchestration/defs/sync_assets.py`
- **WHEN** `mise run sync:dagster` materializes `dagster_sync_health`
- **THEN** the `registry_drift_count` field is emitted as Dagster metadata
- **AND** a `registry_drift_alert` sensor fires when the count > 0

#### Scenario: agent-observability connects to the deployment control panel

- **GIVEN** the 5-tab marimo control panel at `notebooks/00_control_panel.py`
- **WHEN** the operator opens Tab 5 "Registry"
- **THEN** the registry drift count is shown as a StatCard (default=ok, drift>0=warning)
- **AND** the last_audit timestamp is displayed

### Requirement: Langfuse v3 → v4 migration contract

The system SHALL migrate from `langfuse>=3.x` to `langfuse>=4.0,<5.0` by 2026-11-16 (the v3-Cloud deprecation date). The migration MUST land before that date because v3 will stop receiving security updates + the Python SDK v4 ships Observations-first data model.

The v4 migration contract covers:

1. **SDK v4 surface change**: Removed methods — `start_span`, `start_as_current_span`, `start_generation`, `start_as_current_generation`, `update_current_trace` (decomposed into `propagate_attributes()`, `set_current_trace_io()`, `set_current_trace_as_public()`), `DatasetItemClient` (replaced by `dataset.run_experiment()`).
2. **Env-var rename**: `LANGFUSE_BASEURL` → `LANGFUSE_BASE_URL`.
3. **OpenTelemetry-first**: Default OTel export filters via `is_default_export_span()`; opt-out via `Langfuse(should_export_span=lambda s: True)`.
4. **Pydantic v2 only**: Dropped Pydantic v1 support.
5. **Removed types**: `TraceMetadata`, `ObservationParams`.

#### Scenario: A new agent uses Langfuse tracing

- **GIVEN** the platform is on Langfuse v4
- **WHEN** an agent in `agents/meaisinfhoghlaim/agents/*.py` calls `langfuse.openai().chat.completions.create(...)` (or any framework wrapper)
- **THEN** the call MUST land in the Langfuse UI under "Observations" (not "Traces")
- **AND** the call MUST be visible to `@observe`-decorated BAML functions in the call chain

#### Scenario: A new env var pattern is added to Langfuse

- **WHEN** a new `langfuse-web` sidecar declares `LANGFUSE_BASE_URL`
- **THEN** the v4 server reads it correctly (was `LANGFUSE_BASEURL` in v3)
- **AND** the Locket sidecar MUST inject `LANGFUSE_BASE_URL=https://langfuse.cianfhoghlaim.ie` (not `LANGFUSE_BASEURL`)

### Requirement: LiteLLM v1.91 → v1.97 router updates

The system SHALL upgrade LiteLLM from `v1.91.0` to `v1.97.0` and adopt:

- **MCP Gateway GA** (v1.85.0) — single endpoint with per-key ACL.
- **OAuth 2.0 v2 resolver** (v1.91.0) — replaces Hermes's custom auth code.
- **MCP DCR (Dynamic Client Registration)** (v1.95.0) — new agents self-register without manual secret minting.
- **Rust `/v1/messages` endpoint** (v1.95.0) — high-throughput message bus, exposed via Pangolin reverse proxy under the LITELLM private resource.

#### Scenario: A new agent connects via MCP-OAuth 2.0 v2 + DCR

- **GIVEN** the platform is on LiteLLM v1.97 with MCP Gateway GA + OAuth 2.0 v2 + DCR enabled
- **WHEN** a 12-agent fleet agent connects to `http://litellm.cianfhoghlaim.ie/v1/mcp` for the first time
- **THEN** the DCR flow auto-registers the agent client (no manual operator step)
- **AND** the OAuth 2.0 v2 token flows back to the agent
- **AND** subsequent requests succeed with the v2 token

#### Scenario: The Pangolin reverse-proxy exposes /v1/messages

- **WHEN** `curl -s http://litellm.cianfhoghlaim.ie/v1/messages -X POST -d '{"messages": [...]}' -H 'content-type: application/json'` is called
- **THEN** the request routes through the Pangolin reverse proxy → LiteLLM Rust `/v1/messages` endpoint → response < 200ms

### Requirement: Langfuse v4 server + SDK deployed before 2026-11-16

The system SHALL migrate from `langfuse/langfuse:3` + Python SDK v3 to `langfuse/langfuse:4` + Python SDK v4 by 2026-11-16. The self-hosted server auto-migrates the v3 schema; no data loss is expected.

#### Scenario: A new trace is created post-migration

- **GIVEN** the platform is on Langfuse v4 + SDK v4
- **WHEN** an agent emits a trace via `@observe` or one of the wrapped helper functions (`llm_chat_with_prompts`, `run_dagster_asset_check`, etc.)
- **THEN** the trace lands in the **Observations** view (v4's default) under the project `cliste`
- **AND** the SDK `langfuse.__version__` prints `4.x`
- **AND** the env-var `LANGFUSE_BASE_URL` (NOT `LANGFUSE_BASEURL`) is set

### Requirement: 47 agent call-sites migrated to v4 method names

The system SHALL audit + replace every v3 SDK call in the 12-agent fleet (`agents/meaisinfhoghlaim/agents/*.py`) + the 5 BIEP notebook helpers (`notebooks/_shared/marimo_patterns.py`) + the 7 BAML-side observability wrappers.

#### Scenario: A call-site uses a deprecated v3 method

- **GIVEN** a Python file in `agents/meaisinfhoghlaim/agents/`
- **WHEN** `bunx ccc:search "start_as_current_span\|start_generation\|update_current_trace\|DatasetItemClient"` flags matches
- **THEN** each match is replaced with the v4 equivalent (`span(...)`, `propagate_attributes(...)`, `set_current_trace_io(...)`, `dataset.run_experiment(...)`, etc.)

### Requirement: Pydantic v2 only

The system SHALL drop Pydantic v1 imports (from `langfuse.pydantic_compat`) and use Pydantic v2 directly throughout.

#### Scenario: A agent call site imports langfuse.pydantic_compat

- **GIVEN** a Python file in `agents/meaisinfhoghlaim/agents/` or `notebooks/_shared/`
- **WHEN** `bunx ccc:search "from langfuse.pydantic_compat"` flags matches
- **THEN** each match is replaced with the Pydantic v2 native imports (no `pydantic_compat`)
- **AND** the file MUST `import pydantic` directly

### Requirement: mlflow pin (>=3.15.1,<4.0.0) — Priority 1 bump per the 2026-08-21 audit

The system SHALL pin `mlflow>=3.15.1,<4.0.0` per the 2026-08-21 upstream-version alignment audit. The 3.15.1 bump supersedes 3.12.0 (which was the floor) and includes:

- **3.13.0** — RBAC overhaul (per-resource permission APIs removed; unified `mlflow.set_workspace_permission` model); MLServer removed (`mlflow models serve` no longer bundles MLServer); `judge.align()` optimizer default changed from GEPA → MemAlign; **pytest integration** added (`@mlflow.test` decorator).
- **3.15.1** — Centralized MCP Registry; MLflow Assistant; shareable table views; proxy-less artifact transfers; multimodal LLM judges; `MLFLOW_ALLOW_FILE_STORE=true` env var is **required** for any legacy `mlruns/` SQLite fallback.

#### Scenario: A new BAML function evaluates a model with mlflow

- **GIVEN** the platform is on mlflow 3.15.1 + the operator added `MLFLOW_ALLOW_FILE_STORE=true` to `secrets.env`
- **WHEN** a BAML function calls `mlflow.log_metric(...)` or `mlflow.evaluate(...)`
- **THEN** the call MUST land in the MLflow UI under the experiment `cliste`
- **AND** the legacy `mlruns/` SQLite fallback MUST still work (since the test-suite jobs use it)

#### Scenario: A legacy judge.align() call uses the new default

- **GIVEN** the platform is on mlflow 3.15.1
- **WHEN** a BAML function calls `judge.align(...)` without specifying `optimizer=...`
- **THEN** the default `MemAlign` optimizer is used (NOT GEPA)
- **AND** the bump audits the 5 callsites to either pin `optimizer='gepa'` (legacy compat) or accept the new default

#### Scenario: The MCP Registry endpoint is exposed via Pangolin

- **GIVEN** `pangolin.yaml` has the `/api/mcp/registry` path
- **WHEN** `curl -s https://mlflow.cianfhoghlaim.ie/api/mcp/registry` is called
- **THEN** the response MUST be 200 OK with the MCP registry payload

### Requirement: mlflow 3.13+ MLServer removal — the agent deployment surface MUST NOT regress

The system MUST verify that no agent deployment depends on `mlflow models serve` + MLServer (the latter removed in 3.13). The 12-agent fleet uses the LiteLLM proxy for model serving; MLServer was never wired.

#### Scenario: An agent deployment reaches mlflow

- **WHEN** the 12-agent fleet runs an evaluation
- **THEN** the model is served via LiteLLM (NOT MLServer)
- **AND** mlflow 3.15.1 is used for tracking + evaluation ONLY (not serving)

### Requirement: Langfuse v4 implementation — 47-call-site migration contract

The system SHALL implement the v4 SDK migration contract (per the archived `2026-08-21-2026-08-21-langfuse-v3-to-v4-migration-v1` proposal's spec deltas) across all 12 agent fleet modules in `agents/meaisinfhoghlaim/agents/*.py`. The migration MUST:

- Replace every `with langfuse.start_as_current_span(name=...) as span:` with `with langfuse.span(name=...) as span:`.
- Replace every `with langfuse.start_as_current_generation(name=...) as gen:` with `with langfuse.generation(name=...) as gen:`.
- Decompose every `langfuse.update_current_trace(metadata=..., tags=..., session_id=...)` call into the v4 trio: `propagate_attributes(...)`, `set_current_trace_io(input=..., output=...)`, `set_current_trace_as_public()`.
- Replace every `from langfuse.api.resources.dataset_items import DatasetItemClient` with the v4 experiment-runner pattern: `from langfuse import get_dataset; get_dataset(name).run_experiment(run, dataset=...)`.
- Drop every `from langfuse.pydantic_compat import v1` import; use Pydantic v2 native (or `pydantic>=2`).

#### Scenario: A new agent uses the v4 SDK

- **GIVEN** the platform is on Langfuse v4 + SDK v4
- **WHEN** the operator runs `python3 -c "import langfuse; print(langfuse.__version__)"` inside `.venv`
- **THEN** the output MUST start with `4.`
- **AND** `from langfuse.pydantic_compat import v1` MUST NOT be referenced anywhere in the repo (verified via `grep -rn "from langfuse.pydantic_compat" agents/ meaisinfhoghlaim/ notebooks/`)
- **AND** `start_as_current_span` + `start_as_current_generation` + `update_current_trace` + `DatasetItemClient` MUST NOT be referenced anywhere in the repo (verified via `grep -rnE "start_as_current_(span|generation)|update_current_trace|DatasetItemClient" agents/ meaisinfhoghlaim/ notebooks/`)

#### Scenario: The env-var rename is complete

- **GIVEN** the platform is on Langfuse v4
- **WHEN** the operator runs `grep -rn "LANGFUSE_BASEURL" .env .infisical.env bonneagar/stacks/*/secrets.env bonneagar/stacks/*/compose.yaml 2>/dev/null`
- **THEN** the output MUST be empty (zero matches) — the legacy `LANGFUSE_BASEURL` is fully replaced by `LANGFUSE_BASE_URL`

### Requirement: Langfuse v4 server image bump — `langfuse/langfuse:4.x`

The system SHALL run `langfuse/langfuse:4.x` (any 4.0+ stable patch) in the self-hosted `langfuse-web` container, replacing the legacy `langfuse/langfuse:3`. The v3 → v4 schema migration is automatic on first boot of the v4 server.

#### Scenario: The v4 server is up

- **GIVEN** the platform is on Langfuse v4
- **WHEN** `docker inspect langfuse-web --format '{{.Config.Image}}'` runs
- **THEN** the image tag MUST start with `langfuse/langfuse:4`
- **AND** `curl -s http://localhost:3001/api/public/health` returns 200 OK

#### Scenario: A new trace is recorded post-migration

- **GIVEN** the platform is on Langfuse v4
- **WHEN** any `@observe`-decorated BAML function in `agents/meaisinfhoghlaim/agents/*.py` runs
- **THEN** the trace MUST land in the v4 **Observations** view (NOT v3's Traces view)
- **AND** the trace MUST be queryable via the v4 `Dataset.run_experiment()` API

### Requirement: LiteLLM v1.97.0 image bump — ghcr.io/berriai/litellm-database:v1.97.0

The system SHALL run `ghcr.io/berriai/litellm-database:v1.97.0` (or any 1.97.x stable patch) in the self-hosted `litellm` container, replacing the legacy `v1.91.0`. The bump brings:

- **1.85.0** — MCP Gateway GA (replaces Hermes's hand-rolled MCP code)
- **1.91.0** — OAuth 2.0 v2 resolver + DCR
- **1.95.0** — Rust `/v1/messages` endpoint
- **1.97.0** — Tool-result guardrails + SAML 2.0 SSO

#### Scenario: A new agent connects via the v1.97 MCP Gateway

- **GIVEN** the platform is on LiteLLM v1.97
- **WHEN** the operator runs `curl -s http://localhost:4000/v1/mcp/servers` to list the configured MCP servers
- **THEN** the response MUST be 200 OK with the MCP registry payload
- **AND** the v1.97 `tool-result guardrails` are applied per the agent's ACL

#### Scenario: The Rust /v1/messages endpoint is reachable

- **GIVEN** `pangolin.yaml` has the `/v1/messages` path exposed
- **WHEN** `curl -s -X POST http://litellm.cianfhoghlaim.ie/v1/messages -d '{"messages": [...]}' -H 'content-type: application/json'`
- **THEN** the request routes through the Pangolin reverse proxy → LiteLLM Rust `/v1/messages` endpoint
- **AND** the response latency is < 200ms for a single-message payload

#### Scenario: The 12-agent fleet still connects

- **WHEN** any `@observe`-decorated BAML function in `agents/meaisinfhoghlaim/agents/*.py` calls a model
- **THEN** the request goes through the v1.97 gateway successfully
- **AND** the trace lands in Langfuse v4 (the v3→v4 migration we just shipped)

### Requirement: LiteLLM v1.97 /v1/messages path exposed via Pangolin

The system SHALL expose LiteLLM's Rust `/v1/messages` endpoint (v1.95+) via the Pangolin reverse proxy. The path MUST be added to `bonnegar/stacks/litellm/pangolin.yaml` under the LITELLM private resource.

#### Scenario: The v1/messages path is reachable

- **GIVEN** the platform is on LiteLLM v1.97 + Pangolin v3
- **WHEN** the operator runs `curl -X POST https://litellm.cianfhoghlaim.ie/v1/messages`
- **THEN** the response MUST be 200 OK or 4xx (NOT 404)
- **AND** the response MUST come from the Rust endpoint (latency < 200ms for a small payload)

### Requirement: litellm config.yaml regenerated from MODEL_REGISTRY

The system SHALL regenerate `bonnegar/stacks/litellm/config/config.yaml` from the centralized `MODEL_REGISTRY` (per the 2026-08-15 centralized-model-registry openspec change) via `mise run ml:litellm:regenerate`. The regeneration MUST be idempotent + auto-runnable in CI.

#### Scenario: The config.yaml matches the current MODEL_REGISTRY

- **GIVEN** the operator has updated `MODEL_REGISTRY` with a new model entry
- **WHEN** they run `mise run ml:litellm:regenerate`
- **THEN** `config.yaml` is regenerated with the new model entry
- **AND** a re-run of the same task produces no further changes (idempotent)

## Cross-references

- [`.agents/skills/langfuse/SKILL.md`](../../.agents/skills/langfuse/SKILL.md)
- [`.agents/skills/mlflow/SKILL.md`](../../.agents/skills/mlflow/SKILL.md)
- [`.agents/skills/ragas/SKILL.md`](../../.agents/skills/ragas/SKILL.md)
- [`.agents/skills/datadog/SKILL.md`](../../.agents/skills/datadog/SKILL.md)
- [`cianfhoghlaim/observability/`](../../cianfhoghlaim/observability/) (the integration module)
- [`cianfhoghlaim/evaluation/`](../../cianfhoghlaim/evaluation/) (RAGAS pipeline)
