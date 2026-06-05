# InvokeAI

## Overview
InvokeAI is a professional-grade Stable Diffusion image generation platform built on the SDXL architecture. Created and maintained by the InvokeAI team, it provides an OpenAI-compatible API with `/v1/models` and image generation endpoints, along with a rich web UI. The `ghcr.io/invokeai/invokeai:latest` image runs with 16GB memory and 8 CPU cores, pulling models from the shared HuggingFace cache.

## Why This Matters for Kings' College Galway
InvokeAI generates visual study assets — diagrams, illustrations, and historical reconstructions — for the Celtic education curriculum. When a Leaving Cert history lesson generates text content about the Battle of Clontarf, InvokeAI creates period-accurate illustrations. For Irish language flashcards, it generates culturally appropriate visual mnemonics. The shared HuggingFace cache ensures on-disk model weights are shared across the entire platform (LiteLLM, MLX-Omni, Pipecat), minimizing storage duplication on the MacBook M4.

## Key Features
- SDXL-based image generation with OpenAI-compatible API endpoints
- 16GB memory / 8 CPU core allocation for high-quality rendering
- Shared HuggingFace cache at `/stedding/huggingface` (read-only mount)
- External Postgres + Redis configuration for production persistence
- 60s startup grace for model warm-up from cache

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/invokeai
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/invokeai
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on the MacBook M4 workload host (bunchloch). Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `INVOKEAI_ROOT` | No | Root directory for InvokeAI data | `/invokeai` |
| `INVOKEAI_API_KEY` | Yes | API key for the InvokeAI server | — |
| `INVOKEAI_DATABASE_URL` | Yes | External Postgres connection URL | — |
| `INVOKEAI_REDIS_PASSWORD` | No | Redis password for queue backend | — |
| `HF_HOME` | No | HuggingFace home directory | `/stedding/huggingface` |
| `HF_HUB_CACHE` | No | HuggingFace hub cache | `/stedding/huggingface/hub` |
| `CONTAINER_REGISTRY` | No | Container registry | `ghcr.io/invokeai` |

## Access
- **URL**: `https://invokeai.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal ports**: 9090, 9091
- **Auth**: API key (`INVOKEAI_API_KEY`)

## Health Check
```bash
docker ps --filter name=invokeai --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/invoke-ai/InvokeAI
- **Documentation**: https://invoke-ai.github.io/InvokeAI
- **Latest release**: Pulls `ghcr.io/invokeai/invokeai:latest` — a professional-grade Stable Diffusion toolkit with continuous updates.
