# Outline — Team Wiki + Knowledge Base

Fast, collaborative knowledge base for your team. Supports Markdown
editing, nested collections, public sharing, and a Slack-style
editor.

## Architecture

- **Container:** `outline` (outlinewiki/outline:0.78.0)
- **Port:** 3000 (Web UI)
- **Backend:** Centralised lakehouse-postgres (db=outline) + lakehouse-redis
- **SSO:** Pocket ID via OIDC
- **Host:** bunchloch (MacBook M4 Max)

## Files (6-file GOLD_STANDARD)

| File | Purpose |
|:--|:--|
| `compose.yaml` | Base compose — no Locket refs |
| `compose.dev.yaml` | Local dev override (no-op locket) |
| `sidecar.yaml` | Locket sidecar (Infisical) |
| `secrets.env` | Infisical URI template |
| `pangolin.yaml` | Pangolin private-resource route |
| `blueprint.yaml` | Pangolin private-resource blueprint |
| `.env.example` | Non-secret dev defaults |
| `.env.dev` | Dev secrets (gitignored) |

## Usage

```bash
# Production
docker compose -f compose.yaml -f sidecar.yaml up -d

# Development
docker compose -f compose.yaml -f compose.dev.yaml -f sidecar.yaml up -d
```

## Health check

```bash
wget --spider http://localhost:3000/_health
```
