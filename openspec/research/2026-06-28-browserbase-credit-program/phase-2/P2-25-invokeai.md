# P2-25 — invokeai (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

InvokeAI is the **Stable Diffusion XL + Z-Image-Turbo image generation server** that powers visual asset creation for the tuatha educational MMO and croilar portfolio. It runs in the LiteLLM fallback chain for image generation requests.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/invokeai/compose.yaml` | InvokeAI service (port 9090) |
| `stacks/invokeai/models/` | Pre-downloaded SDXL + Z-Image-Turbo checkpoints |
| `oideachais/agents/tuatha/mmo/assets/` | Generated tuatha assets (Crypteolas badges, realm illustrations) |
| `cognify/rules/invokeai_models.py` | Lists 3 active SDXL variants |

**Canonical InvokeAI compose**:

```yaml
invokeai:
  image: invokeai/invokeai:latest
  container_name: invokeai-server
  restart: unless-stopped
  ports:
    - "9090:9090"
  environment:
    INVOKEAI_ROOT: /var/lib/invokeai
    INVOKEAI_PORT: 9090
    INVOKEAI_HOST: 0.0.0.0
  volumes:
    - invokeai-models:/var/lib/invokeai/models
    - invokeai-cache:/var/lib/invokeai/.cache
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `INVOKEAI_API_URL` | `http://invokeai:9090/api/v1` | compose env |
| `INVOKEAI_MASTER_KEY` | `infisical://dev-baile/invokeai/master_key` | Locket |

## CCC anchors

`stacks/invokeai/` · `oideachais/agents/tuatha/mmo/assets/` · `cognify/rules/invokeai_models.py`

Search terms: `"invokeai"`, `"SDXL"`, `"Z-Image-Turbo"`, `"txt2img"`.

## Drift log

| Date | Event |
|--:|:--|
| 2025-10 | Initial InvokeAI deploy (SD 1.5) |
| 2025-12 | Upgraded to SDXL |
| 2026-03 | Added Z-Image-Turbo (faster inference) |
| 2026-04 | Wired to LiteLLM `image` alias |

## Anti-patterns

1. Don't use InvokeAI for text generation — use LiteLLM
2. Don't run InvokeAI on MacBook M4 — use arm1-oci (CPU-only is fine for SDXL)
3. Don't skip the model cache — SDXL checkpoints are 6 GB each

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hosting | arm1-oci | CPU-only is fine for SDXL (no GPU needed) |
| Models | SDXL + Z-Image-Turbo | Quality + speed |
| API | OpenAI-compatible (`/v1/images/generations`) | Works with LiteLLM |
| Auth | Master key (single) | Internal-only |
| Cache | Docker volume (1 TB) | Avoid re-downloads |

## Files to read next

`stacks/invokeai/` · `cognify/rules/invokeai_models.py`
