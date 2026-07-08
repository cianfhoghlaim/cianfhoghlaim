# Letta — Stateful Agent Memory Layer

Stateful agent memory layer backing the 3 agent-facing surfaces
(OpenClaw + OpenChamber + Hermes). Persists user-level memory
across sessions — per the `agent-platform-cluster` spec
Requirement: Letta memory layer.

## Architecture

- **Container:** `letta` (letta/letta:v0.5.4)
- **Port:** 8283 (REST API + ADE Web UI)
- **Backend:** Centralised lakehouse-postgres (db=letta)
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
curl -fsS http://localhost:8283/v1/health
```
