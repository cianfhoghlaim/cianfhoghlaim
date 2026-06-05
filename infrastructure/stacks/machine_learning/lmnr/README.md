# LMNR — LLM Observability and Monitoring

## Overview

LMNR (Language Model Network Router) is an open-source LLM observability platform providing trace collection, cost tracking, and analytics. It serves as an alternative or complement to Langfuse, with a focus on real-time tracing and ClickHouse-powered analytics. The stack includes a web frontend, an app server, ClickHouse for analytics storage, and PostgreSQL for application state.

## Why This Matters for Kings' College Galway

LMNR provides a second observability angle on the LLM infrastructure. While Langfuse captures per-trace detail, LMNR focuses on aggregate analytics — which models are being used most, what the cost trends look like across the LiteLLM aliases, and how latency varies by model and time of day. For a project running 6+ models through a single gateway, this operational visibility is essential for optimising the alias chains and identifying when a model is underperforming relative to its cost.

## Key Features

- **Real-time tracing** — Capture LLM calls as they flow through the gateway
- **ClickHouse analytics** — Columnar storage for fast aggregation queries
- **Cost tracking** — Per-model, per-alias cost breakdown
- **Web dashboard** — Frontend UI for trace inspection and analytics graphs

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/lmnr
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves database passwords and ClickHouse credentials from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `POSTGRES_USER` | Yes | PostgreSQL user | — |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password | — |
| `POSTGRES_DB` | Yes | PostgreSQL database name | — |
| `CLICKHOUSE_USER` | Yes | ClickHouse user | — |
| `CLICKHOUSE_PASSWORD` | Yes | ClickHouse password | — |

## Access

- **Web UI**: `https://lmnr.cianfhoghlaim.ie` (private, Member role)
- **PostgreSQL**: Port 5433 (internal)
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/lmnr-ai/lmnr>
- **Latest**: Active development (2025) — ClickHouse migration, query engine for trace analytics, frontend dashboard improvements

## Screenshot

LMNR's web frontend provides a trace explorer with search and filter capabilities, a dashboard showing cost and latency trends over time, per-model usage breakdowns, and individual trace detail views showing the full request/response cycle with token counts and timing.
