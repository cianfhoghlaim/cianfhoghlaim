# n8n Workflow Automation

## Overview
n8n is a fair-code workflow automation platform with a visual node editor that connects 400+ integrations. Created by n8n GmbH and pinned at version `1.94.1`, it provides a visual pipeline builder for automating complex multi-step processes. The stack runs in queue mode with a Postgres 16 backend, Redis 7 for job queuing, and an `n8n-init` one-shot container that seeds the 6 team workflows from the `workflows/` directory on first start.

## Why This Matters for Kings' College Galway
n8n is the team collaboration workflow layer that glues together the Celtic education platform's operational tasks. It powers the scheduling pipeline that triggers Dagster curriculum extraction jobs, routes Vikunja task notifications to Slack, processes cal-diy booking webhooks for study session scheduling, and orchestrates LLM-powered content generation steps through the LiteLLM gateway. The 6 seeded workflows cover team operations (standup reports, PR review routing, curriculum ingestion triggers) using the OpenCode Go API as the unified LLM backbone for all AI-powered workflow steps.

## Key Features
- Visual node editor with 400+ integrations and sub-workflow support
- Queue mode with Redis 7 for multi-worker scaling and reliable execution
- Postgres 16 backend for workflow history, credentials, and executions
- Pocket ID OIDC SSO integration for team authentication
- `n8n-init` one-shot container for automatic workflow seeding on first deploy
- PlanetScale-backed production database with local Postgres fallback

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/n8n
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/n8n
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `N8N_HOST` | No | Public hostname | `n8n.cianfhoghlaim.ie` |
| `N8N_PORT` | No | Listen port | `5678` |
| `N8N_PROTOCOL` | No | Protocol | `https` |
| `N8N_WEBHOOK_URL` | No | Webhook base URL | `https://n8n.cianfhoghlaim.ie/` |
| `N8N_ENCRYPTION_KEY` | Yes | Encryption key for credentials | — |
| `N8N_USER_MANAGEMENT_JWT_SECRET` | Yes | JWT secret for user auth | — |
| `N8N_DB_POSTGRES_PASSWORD` | Yes | Postgres password (aliased) | — |
| `N8N_POSTGRES_DB` | No | Postgres database name | `n8n` |
| `N8N_POSTGRES_USER` | No | Postgres username | `n8n` |
| `N8N_POSTGRES_PASSWORD` | No | Postgres password | — |
| `N8N_WEBHOOK_SECRET` | Yes | Webhook verification secret | — |
| `N8N_BASIC_AUTH_ACTIVE` | No | Enable basic auth | `false` |
| `N8N_DIAGNOSTICS_ENABLED` | No | Telemetry opt-out | `false` |
| `N8N_METRICS` | No | Enable metrics | `true` |
| `EXECUTIONS_DATA_PRUNE` | No | Auto-prune execution data | `true` |
| `EXECUTIONS_DATA_MAX_AGE` | No | Max age in hours | `336` |
| `GENERIC_TIMEZONE` | No | Default timezone | `Europe/Dublin` |
| `OPENAI_API_KEY` | No | LLM API key (routed through LiteLLM) | — |
| `OPENAI_BASE_URL` | No | LLM base URL | — |
| `OIDC_CLIENT_ID` | No | Pocket ID OIDC client ID | — |
| `OIDC_CLIENT_SECRET` | No | Pocket ID OIDC client secret | — |
| `OIDC_ISSUER` | No | OIDC issuer URL | `https://auth.cianfhoghlaim.ie` |
| `DATABASE_URL` | No | PlanetScale database URL (production) | — |
| `FALLBACK_DATABASE_URL` | No | Local Postgres fallback URL | — |

## Access
- **URL**: `https://n8n.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 5678
- **Auth**: Pocket ID OIDC SSO

## Health Check
```bash
docker ps --filter name=n8n --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/n8n-io/n8n
- **Documentation**: https://docs.n8n.io
- **Latest release**: Pinned at `docker.n8n.io/n8nio/n8n:1.94.1` for stability.
