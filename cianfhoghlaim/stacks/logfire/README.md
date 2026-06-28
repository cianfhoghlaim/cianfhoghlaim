# Logfire Stack (Pydantic Observability Platform)

This stack deploys an **OpenTelemetry Collector** that forwards OTLP traces
from any KCG service to **Logfire cloud** (`logfire.pydantic.dev`).

## Why an OTEL Collector?

Pydantic does not publish a self-hostable Logfire-server Docker image as of
2026-06-26. The Logfire SaaS endpoint at `logfire.pydantic.dev` is the only
ingestion target. Deploying a local OpenTelemetry Collector gives KCG:

1. A **real, deployable local service** (satisfies the 6-file GOLD_STANDARD
   pattern; the Komodo stack definition points at this directory).
2. A **self-hosted collection point** — raw traces never leave the cluster
   unless explicitly forwarded.
3. **Resilience** — the collector buffers to disk on `:4317/:4318` so a
   transient Logfire outage doesn't drop traces.
4. **Multi-source ingestion** — any language (Python, Go, Rust, JS) can
   emit OTLP to the collector; the collector fans out to Logfire.

## Quick routing

| Destination | Service | Hostname | Port | Pangolin route |
|:--|:--|:--|:--|:--|
| OTLP gRPC | `logfire-otel` | `logfire-otel` | 4317 | (internal only) |
| OTLP HTTP | `logfire-otel` | `logfire-otel` | 4318 | (internal only) |
| Health check | `logfire-otel` | `logfire-otel` | 8888 | (internal only) |
| Prometheus metrics | `logfire-otel` | `logfire-otel` | 8889 | (internal only) |
| Web UI | (cloud) | `https://logfire.pydantic.dev` | 443 | `logfire.cianfhoghlaim.ie` (private) |

## Application wiring (two paths)

### Path A — SDK direct (recommended for Python)

```python
import logfire
logfire.configure(
    token=os.environ["LOGFIRE_TOKEN"],  # from secrets.env via Locket
    project_name="oideachas-celtic-education",
    service_name="education-pipeline",
)
logfire.info("Extracted {n} learning outcomes", n=42)
```

This is what `sruth/oideachais/observability/logfire_config.py` does today.
The SDK sends HTTPS directly to Logfire cloud — the local collector is
bypassed.

### Path B — OTLP via local collector (recommended for multi-language)

```bash
# In any container/service that emits OTLP:
export OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire-otel:4317
export OTEL_SERVICE_NAME=my-service
```

The collector receives the trace, batches it, and forwards to Logfire cloud
with the `LOGFIRE_TOKEN` from secrets.env.

## Files

| File | Purpose |
|:--|:--|
| `compose.yaml` | The OpenTelemetry Collector service (otel/opentelemetry-collector-contrib:0.104.0) |
| `sidecar.yaml` | Locket sidecar for Infisical secret injection |
| `pangolin.yaml` | Private Pangolin route `logfire.cianfhoghlaim.ie` → cloud UI redirect |
| `blueprint.yaml` | Komodo resource-sync metadata |
| `secrets.env` | `infisical://dev-baile/logfire/write_token` URI for `LOGFIRE_TOKEN` |
| `config/otelcol.yaml` | OTEL Collector configuration (receivers, processors, exporters) |
| `README.md` | This file |

## Deployment

```bash
# Production (with Locket sidecar):
cd infrastructure/stacks/logfire
docker compose -f compose.yaml -f sidecar.yaml up -d

# Dev (no-op locket + .env fallback):
docker compose -f compose.yaml -f sidecar.yaml -f compose.dev.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LOGFIRE_TOKEN` | Yes | Project write token from logfire.pydantic.dev | (empty = exports fail) |
| `LOGFIRE_PROJECT_NAME` | No | Logfire project name | `oideachas-celtic-education` |
| `LOGFIRE_ENVIRONMENT` | No | Environment tag (`production` / `development`) | `production` |

## Health Check

```bash
docker ps --filter name=logfire-otel --format "table {{.Names}}\t{{.Status}}"
curl http://localhost:8888/  # OTEL collector health endpoint
```

## Upstream

- **Logfire docs**: https://logfire.pydantic.dev/docs/
- **OTEL Collector**: https://opentelemetry.io/docs/collector/
- **logfire exporter**: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/logfireexporter
