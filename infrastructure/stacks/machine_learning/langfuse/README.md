# Langfuse — LLM Observability Platform (v3)

## Overview

Langfuse is an open-source LLM observability platform that traces every LLM call, scores outputs, manages prompts, and provides analytics dashboards. Think of it as Datadog for LLMs — it captures the full trace from user request through model invocation to final response, with cost tracking, latency measurement, and quality evaluation.

## Why This Matters for Kings' College Galway

Every LLM call in this project flows through the LiteLLM gateway, which automatically traces to Langfuse. This means every BAML extraction run (10 functions across 50+ exam papers), every curriculum embedding generation, and every study asset image prompt gets a full trace with input/output/tokens/latency/cost. When a RAGAS evaluation flags a learning outcome extraction as low-faithfulness, the Langfuse trace shows exactly which model, which prompt, and which document produced the poor result. This audit trail is essential for an educational platform — every piece of generated content must be traceable back to its source syllabus and its LLM invocation.

## Key Features

- **Full trace capture** — Input, output, model, tokens, latency, cost per call
- **Prompt management** — Version prompts with A/B testing and rollback
- **Evaluation** — Score traces with RAGAS metrics (faithfulness, relevance)
- **ClickHouse analytics** — High-performance columnar storage for trace data
- **S3 media storage** — Store generated images and documents alongside traces

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/langfuse
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DATABASE_URL` | Yes | PostgreSQL connection string | — |
| `SALT` | Yes | Password hashing salt | — |
| `ENCRYPTION_KEY` | Yes | 64-char hex encryption key | — |
| `CLICKHOUSE_URL` | No | ClickHouse HTTP URL | `http://clickhouse:8123` |
| `CLICKHOUSE_USER` | No | ClickHouse username | `clickhouse` |
| `CLICKHOUSE_PASSWORD` | Yes | ClickHouse password | — |
| `LANGFUSE_S3_EVENT_UPLOAD_BUCKET` | No | S3 bucket for events | `langfuse` |
| `TELEMETRY_ENABLED` | No | Allow anonymous telemetry | `true` |

## Access

- **Web UI**: `https://langfuse.cianfhoghlaim.ie` (private, Member role)
- **API**: `https://langfuse.cianfhoghlaim.ie/api`
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/langfuse/langfuse>
- **Documentation**: <https://langfuse.com/docs>
- **Latest**: v3.x (2025) — ClickHouse migration complete, prompt management UI overhaul, evaluation SDK v2, LLM-as-judge scoring

## Screenshot

Langfuse's web UI shows: a trace waterfall view (every LLM call in a pipeline rendered as nested spans with timing), a prompt management interface (version history, A/B test configuration, variable editor), a dashboard with cost/latency/volume charts, and an evaluations tab showing RAGAS scores per trace.
