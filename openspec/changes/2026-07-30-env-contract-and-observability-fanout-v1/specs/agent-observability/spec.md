# Spec delta: `agent-observability`

This delta is part of the openspec change
`2026-07-30-env-contract-and-observability-fanout-v1`. It adds 2
requirements that wire the logfire OTel collector as a fan-out to BOTH
Logfire cloud AND Langfuse, and that mandate OTLP export from every
memory/observability backend.

## ADDED Requirements

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

## Why this matters

Today the agent-platform clusters (openchamber, openclaw, hermes) have
full Langfuse coverage but **zero Logfire coverage**; the data-platform
clusters (dagster, khoj, letta) have full Logfire coverage but **zero
Langfuse coverage**. Phase 7 (Monitor) of the 7-phase cognition pipeline
in `.agents/skills/agent-observability/SKILL.md` is the only place in the
whole platform where observability is "complete" — and today even Phase
7 is split.

The fan-out collector + the per-service OTLP wiring closes that gap:
every trace appears in both backends, and the "single pane of glass"
claim in the skill becomes literal.