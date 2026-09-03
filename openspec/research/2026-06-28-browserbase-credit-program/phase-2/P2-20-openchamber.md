# P2-20 — openchamber (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

OpenChamber is the **agent IDE** for the Cianfhoghlaim agent fleet — a web-based IDE for building, testing, and deploying AI agents. It's the human-facing interface to the `agent-platform` subagent system.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/openchamber/compose.yaml` | OpenChamber web + Postgres (port 3030) |
| `stacks/openchamber/blueprint.yaml` | Pangolin private-resource |
| `oideachais/web/apps/oideachais-web/src/routes/agents.tsx` | Embeds OpenChamber in TanStack Start |

**Canonical OpenChamber compose** (`stacks/openchamber/compose.yaml`):

```yaml
openchamber:
  image: openchamber/openchamber:latest
  container_name: openchamber-web
  restart: unless-stopped
  ports:
    - "3030:8080"
  environment:
    DATABASE_URL: postgres://openchamber-postgres:5432/openchamber
    LITELLM_BASE_URL: http://litellm:4000/v1
    LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
    LANGFUSE_HOST: ${LANGFUSE_HOST}
  depends_on:
    - openchamber-postgres

openchamber-postgres:
  image: postgres:16-alpine
  container_name: openchamber-postgres
  environment:
    POSTGRES_DB: openchamber
    POSTGRES_USER: openchamber
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `OPENCHAMBER_DATABASE_URL` | `infisical://dev-baile/openchamber/database_url` | Locket |
| `OPENCHAMBER_LITELLM_BASE_URL` | `http://litellm:4000/v1` | docker network |

## CCC anchors

`stacks/openchamber/` · `oideachais/web/apps/oideachais-web/src/routes/agents.tsx`

Search terms: `"openchamber"`, `"OPENCHAMBER_DATABASE_URL"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-12 | Initial OpenChamber deploy |
| 2026-03 | Embedded in TanStack Start (oideachais-web) |
| 2026-05 | Wired to LiteLLM `minimax` alias |

## Anti-patterns

1. Don't run OpenChamber without LiteLLM — it can't generate
2. Don't use SQLite — use Postgres
3. Don't bypass Pangolin SSO — every agent run is auditable

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hosting | arm1-oci (control plane) | Always-on for human operators |
| DB | Postgres 16 | Same as rest of stack |
| LLM | LiteLLM `minimax` | Consistent with BAML |
| Auth | Pocket ID SSO via Pangolin | Single source |
| Embed | TanStack Start iframe | In-context for operators |

## Files to read next

`stacks/openchamber/` · `oideachais/web/apps/oideachais-web/src/routes/agents.tsx`
