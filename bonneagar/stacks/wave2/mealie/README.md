# Mealie — Recipe Manager + Meal Planner

Self-hosted recipe manager + meal planner with web UI, full-text
search (Meilisearch), and shopping-list generation.

## Architecture

- **Container:** `mealie` (ghcr.io/mealie-recipes/mealie:v1.10.0)
- **Port:** 9925 (host) → 9000 (container)
- **Backend:** Centralised lakehouse-postgres (db=mealie)
- **LLM:** Optional recipe-image fallback via LiteLLM
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
curl -fsS http://localhost:9925/api/app/about
```
