# Windmill

## Overview
Windmill is an open-source developer platform for turning scripts (Python, TypeScript, Go, Bash, SQL) into production-grade workflows, webhooks, and UIs. Created by Windmill Labs and available at `ghcr.io/windmill-labs/windmill`, it features the fastest workflow engine (13x vs Airflow), a visual flow builder, and built-in secret management. The stack runs a Postgres 16 backend, multiple worker replicas, a Caddy reverse proxy, and optional LSP + multiplayer services.

## Why This Matters for Kings' College Galway
Windmill powers the internal workflow automation layer for the Celtic education platform — scheduling curriculum scraping jobs, orchestrating LLM-powered content generation pipelines, and triggering study asset exports. It bridges the gap between the n8n visual workflow tool (used for team collaboration) and the Dagster data orchestration layer, handling lightweight automation tasks like webhook-to-DLT triggers, periodic health checks, and internal Slack/GitHub integrations. Its native Python worker support integrates directly with the platform's uv-based toolchain.

## Key Features
- Visual workflow builder with Python, TypeScript, Go, Bash, and SQL support
- 13x faster than Airflow with queue-based multi-worker architecture
- Native worker (in-process), regular worker, and optional Chromium reports worker
- Caddy reverse proxy for automatic HTTPS and routing
- Postgres 16 backend with configurable database URL

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/windmill
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/windmill
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `WM_IMAGE` | Yes | Windmill Docker image (from Infisical) | — |
| `DATABASE_URL` | Yes | Full Postgres connection URL (from Infisical) | — |
| `POSTGRES_PASSWORD` | Yes | Postgres password | `changeme` |
| `POSTGRES_DB` | No | Postgres database name | `windmill` |
| `MODE` (server) | No | Server mode | `server` |
| `MODE` (worker) | No | Worker mode | `worker` |
| `WORKER_GROUP` | No | Worker group name | `default` / `native` |
| `NUM_WORKERS` | No | Number of native workers | `8` |
| `SLEEP_QUEUE` | No | Native worker sleep queue ms | `200` |
| `LOG_MAX_SIZE` | No | Max log file size | `20m` |
| `LOG_MAX_FILE` | No | Max log files | `10` |
| `BASE_URL` | No | Caddy base URL | `:80` |

## Access
- **URL**: `https://windmill.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal ports**: 8000 (server), PostgreSQL (5432), Caddy (80, 25)
- **Auth**: Windmill's built-in authentication

## Health Check
```bash
docker ps --filter name=windmill --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/windmill-labs/windmill
- **Documentation**: https://www.windmill.dev/docs
- **Latest release**: v1.717.1 (2026-06-04) — Fixed relative-import cache invalidation when imported scripts change.
