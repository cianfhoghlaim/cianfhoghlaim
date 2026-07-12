# Immich — Self-hosted Photo Management

Self-hosted Google Photos replacement. Provides photo + video
backup, ML-powered face/object recognition, and timeline browsing.

This stack is the downstream consumer of the Apple Photos library
extraction (via the `oideachais-mcp-filesystem` MCP server) — see
the `apple-photos-ingestion` skill.

## Architecture

- **Containers:** `immich-server` + `immich-machine-learning`
- **Port:** 2283 (Web UI)
- **Backend:** Centralised lakehouse-postgres (db=immich) + lakehouse-redis
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
curl -fsS http://localhost:2283/api/server/ping
```
