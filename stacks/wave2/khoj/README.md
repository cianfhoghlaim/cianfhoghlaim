# Khoj — Personal AI Assistant

Personal AI assistant that searches, browses, and reasons across
your notes, documents, and codebase. Provides desktop + browser
+ mobile UIs.

## Architecture

- **Container:** `khoj` (ghcr.io/khoj-ai/khoj:v1.30.0)
- **Port:** 42110 (Web UI)
- **Backend:** Centralised lakehouse-postgres (db=khoj)
- **LLM:** LiteLLM (M3 chokepoint) at http://litellm:4000/v1
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
wget --spider http://localhost:42110/api/health
```
