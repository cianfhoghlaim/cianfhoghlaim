# MLX-Omni

## Overview
MLX-Omni is an Apple Silicon-native OpenAI-compatible API server that bridges MLX-format machine learning models to standard LLM clients. Created by madroidmaq and built specifically for Apple's MLX framework, it exposes a `/v1/models` and `/v1/chat/completions` endpoint from locally cached HuggingFace MLX models. The stack is built from source via a local Dockerfile for optimal Apple Silicon performance.

## Why This Matters for Kings' College Galway
MLX-Omni provides on-device, low-latency LLM inference for document intelligence workloads critical to the Celtic education pipeline. The bare-metal MacBook M4 runs Granite-Docling-MLX for PDF extraction of Leaving Cert exam papers, olmOCR-MLX for Gaelic manuscript OCR, and FIBO-MLX for structured extraction — all without cloud API costs or data egress concerns. Because these models share the `stedding/huggingface/mlx` cache, they benefit from the same curated model storage used across the platform's HuggingFace infrastructure.

## Key Features
- Apple Silicon-optimized MLX inference with 36GB unified memory allocation
- OpenAI-compatible `/v1/chat/completions` and `/v1/models` endpoints
- Shared HuggingFace cache at `/stedding/huggingface/mlx` (read-only mount)
- Auto-loads MLX models on demand with configurable default (Granite-Docling-MLX)
- 60s startup grace period for initial model loading

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/mlx-omni
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/mlx-omni
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on the MacBook M4 workload host (bunchloch). Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MLX_OMNI_API_KEY` | No | API key for MLX-Omni server | `not-needed` |
| `MLX_OMNI_HOST` | No | Listen address | `0.0.0.0` |
| `MLX_OMNI_PORT` | No | Listen port | `10240` |
| `MLX_OMNI_DEFAULT_MODEL` | No | Auto-loaded model | `mlx-community/granite-docling-258M-MLX` |
| `HF_TOKEN` | No | HuggingFace token for gated models (from Infisical) | — |
| `HUGGINGFACE_HUB_TOKEN` | No | HuggingFace Hub token alias | — |
| `HUGGINGFACE_TOKEN` | No | HuggingFace token alias | — |

## Access
- **URL**: `https://mlxomni.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 10240
- **Auth**: API key (`MLX_OMNI_API_KEY`) — optional, defaults to `not-needed`

## Health Check
```bash
docker ps --filter name=mlx-omni --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/madroidmaq/mlx-omni-server
- **Documentation**: https://github.com/madroidmaq/mlx-omni-server
- **Latest release**: Built from source via local `Dockerfile`; tracks the upstream repository for Apple Silicon MLX inference server updates.
