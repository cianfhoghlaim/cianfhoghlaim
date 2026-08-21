# Lakehouse OTel Fan-Out Architecture (added 2026-08-25)

Per the [2026-08-25-lakehouse-observability-and-cross-stack-integration-v1](../../openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/) change.

## Overview

The unified lakehouse stack emits OpenTelemetry traces from its 16 services.
These traces are routed through an OTLP collector that **fans out** to three
backends so the operator can observe traces in the right context:

```
[cognee + graphiti + falkordb + memgraph + lance-namespace + nimtable + olake + memgraph + lakekeeper]
                              |
                              | OTLP/gRPC + OTLP/HTTP
                              v
                +-------------------------------+
                |       otel-collector           |  (profile: `otel`)
                |   (otel/opentelemetry-collector) |
                +-------------------------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        +-----------+   +-----------+   +-----------+
        | logfire   |   | langfuse  |   | mlflow    |
        | (cloud)   |   | (self)    |   | (local)   |
        +-----------+   +-----------+   +-----------+
```

## Local mode (profile `otel`)

When `docker compose --profile otel up -d` is used, the local `otel-collector`
service (inside the lakehouse compose project) handles fan-out. The config
at `bonneagar/stacks/lakehouse/otel-collector.yaml` includes exporters
for all three backends.

## Cross-stack mode (production)

When the existing **logfire stack** (`bonneagar/stacks/logfire/`) is also
deployed, operators can point the lakehouse services at
`http://logfire-otel:4317` (the cross-stack collector) instead of the
local one. The logfire stack already has the same fan-out config in
its `config/otelcol.yaml`.

Configuration:
```bash
# .env.local
LAKEHOUSE_OTLP_ENDPOINT=http://logfire-otel:4317   # cross-stack fan-out
# OR
LAKEHOUSE_OTLP_ENDPOINT=http://otel-collector:4317  # local fan-out
```

## Services that emit traces

Per `scripts/lakehouse-stack-doctor.sh` (Check 9 — added 2026-08-25),
every **application service** in the unified lakehouse stack MUST set
`OTEL_EXPORTER_OTLP_ENDPOINT`. The check excludes storage infrastructure
(garage + postgres + clickhouse + redis) and read-only web UIs
(lancedb-viewer + memgraph-lab) which don't emit application traces.

10 application services currently emit traces:
1. **lakekeeper** — Iceberg REST Catalog traces
2. **lance-namespace** — table registration traces
3. **nimtable** — Iceberg catalog UI traces
4. **olake** — CDC job traces
5. **cognee** — knowledge graph builder traces
6. **graphiti** — bi-temporal KG API traces
7. **falkordb** — graph query traces
8. **memgraph** — Bolt protocol traces
9. (otel-collector is the destination, not a source)

## Required env vars

For the local fan-out (profile `otel`), the operator MUST set:
```bash
# .env.local
LOGFIRE_TOKEN=infisical://dev-baile/pydantic-logfire/write_token
LOGFIRE_PROJECT_NAME=oideachas-celtic-education
LOGFIRE_ENVIRONMENT=development
LANGFUSE_PUBLIC_KEY=infisical://dev-baile/langfuse/public_key
LANGFUSE_SECRET_KEY=infisical://dev-baile/langfuse/secret_key
LANGFUSE_AUTH_HEADER=infisical://dev-baile/langfuse/auth_header  # base64(PUBLIC:SECRET)
MLFLOW_TRACKING_URI=postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres:5432/mlflow
```

## Cross-references

- `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/` — the PR that landed this architecture
- `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/` — PR #2 that added the otel-collector stub
- `openspec/changes/archive/2026-07-30-env-contract-and-observability-fanout-v1/` — the original logfire+langfuse fan-out spec
- `scripts/lakehouse-stack-doctor.sh` — the CI gate that enforces OTEL_EXPORTER_OTLP_ENDPOINT on every application service
- `notebooks/_shared/schema.py:lakehouse_health()` — the marimo helper for cross-stack health checks
