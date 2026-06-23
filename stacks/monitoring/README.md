# Monitoring — Prometheus + Grafana + Loki + Alertmanager

## Overview

The monitoring stack provides centralised observability for the entire Cianfhoghlaim infrastructure. It combines Prometheus (metrics scraping and storage), Grafana (dashboards), Loki (log aggregation), Promtail (log shipping), and Alertmanager (alert routing) into a single deployable unit. All components sit on the shared `cianfhoghlaim` Docker network, enabling automatic discovery of every container's `/metrics` endpoint.

## Why This Matters for Kings' College Galway

Observability is not optional when running 89 Docker Compose stacks across 3 servers. Prometheus scrapes metrics from every service — LiteLLM request latency and token counts, llama-swap GPU memory pressure, Dagster pipeline run durations, Garage S3 operation throughput. Grafana dashboards make these metrics visible at a glance. Loki aggregates container logs across all hosts, enabling correlation queries ("show me all errors from the last Dagster curriculum extraction run"). Alertmanager routes alerts (high memory, disk near full, pipeline failure) to the team's communication channels. This stack is the difference between discovering a failed exam paper OCR run after the fact and catching it in real time.

## Key Features

- **Prometheus** — Time-series metrics with 30-day retention, service discovery via Docker labels
- **Grafana** — Custom dashboards for each service category (storage, ML, engineering, tools)
- **Loki** — Log aggregation with Prometheus-compatible query language (LogQL)
- **Promtail** — Lightweight log shipper that tags logs with container metadata
- **Alertmanager** — Alert routing with inhibition and grouping rules

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/monitoring
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `GF_SECURITY_ADMIN_PASSWORD` | Yes | Grafana admin password | — |
| `GF_SERVER_ROOT_URL` | No | Grafana public URL | `https://grafana.cianfhoghlaim.ie` |
| `PROMETHEUS_RETENTION_TIME` | No | Metrics retention | `30d` |
| `LOKI_RETENTION_PERIOD` | No | Log retention | `30d` |

## Access

- **Grafana**: `https://grafana.cianfhoghlaim.ie` (private, Admin role)
- **Prometheus**: `http://localhost:9090` (internal)
- **Alertmanager**: `http://localhost:9093` (internal)
- **Loki**: `http://localhost:3100` (internal)
- **Auth**: Grafana admin password + Pocket ID OIDC

## Upstream

- **Prometheus**: <https://github.com/prometheus/prometheus> — v2.55.1
- **Grafana**: <https://github.com/grafana/grafana> — latest via `grafana/grafana:latest`
- **Loki**: <https://github.com/grafana/loki> — latest via `grafana/loki:latest`

## Screenshot

Grafana provides customisable dashboards with time-series graphs, gauges, heatmaps, and tables. The default setup includes: Docker host metrics (CPU, memory, disk, network), per-container resource usage, LiteLLM request dashboard (latency percentiles, token counts, error rates), and Dagster pipeline run timeline. Prometheus at port 9090 shows its own expression browser and target status page.
