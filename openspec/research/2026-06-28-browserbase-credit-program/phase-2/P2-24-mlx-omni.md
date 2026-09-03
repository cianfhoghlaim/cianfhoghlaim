# P2-24 — mlx-omni (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

MLX-omni is the **Apple-Silicon-native OpenAI-compatible server** that serves MLX-format models (Qwen3.6, Gemma 4) on the MacBook M4 Max. It's the Apple-Silicon counterpart to llama-swap (which serves GGUF models). Both are bundled in the LiteLLM `minimax` fallback chain.

The canonical Cianfhoghlaim pattern: MLX-omni serves MLX-format models on port 10240; LiteLLM routes to it for MLX-specific queries; llama-swap serves GGUF models as the final fallback.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/mlx-omni/compose.yaml` | MLX-omni service (port 10240) |
| `stacks/mlx-omni/README.md` | Setup + model registry |
| `stacks/litellm/config/config.yaml` (mlx-omni references) | LiteLLM integration |

**Canonical MLX-omni setup**:

```bash
# Install MLX-omni (Apple Silicon only)
pip install mlx-omni

# Start with MLX models (auto-quantized)
mlx-omni serve \
  --model mlx-community/Qwen3.6-27B-Instruct-4bit \
  --model mlx-community/gemma-4-26B-A4B-it-4bit \
  --model mlx-community/GLM-4.6V-Flash-4bit \
  --port 10240
```

**LiteLLM integration** (`stacks/litellm/config/config.yaml`):

```yaml
- model_name: local/document/granite-docling
  litellm_params:
    model: openai/granite-docling
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600  # Docling can be slow on dense PDFs

- model_name: local/ocr/olmocr-mlx
  litellm_params:
    model: openai/olmocr-2-7b-mlx
    api_base: http://mlx-omni:10240/v1
    api_key: not-needed
    timeout: 600
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `MLX_OMNI_API_URL` | `http://mlx-omni:10240/v1` | compose env |
| `MLX_OMNI_MASTER_KEY` | `not-needed` | compose env |

## CCC anchors

`stacks/mlx-omni/` · `stacks/litellm/config/config.yaml` (MLX entries)

Search terms: `"mlx-omni"`, `"mlx-community"`, `"http://mlx-omni:10240/v1"`.

## Drift log

| Date | Event |
|:--|:--|
| 2026-01 | Initial MLX-omni deploy (Qwen2.5 only) |
| 2026-04 | Added Gemma 3 + OLMoE support |
| 2026-05 | Added Qwen3.6 + Gemma 4 + GLM-4.6V (11 vision models) |

## Anti-patterns

1. Don't run MLX-omni on arm1-oci — it's M-series-only
2. Don't use 8-bit quantization on M-series — 4-bit is native + faster
3. Don't use MLX-omni for non-Apple-Silicon models — use llama-swap (GGUF)
4. Don't exceed 48 GB unified memory — MLX is memory-hungry at 4-bit

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hosting | MacBook M4 Max only | Apple Silicon native |
| Quantization | 4-bit | Native hardware support |
| Format | MLX (not GGUF) | M-series optimized |
| Fallback tier | 6th in `minimax` chain | Before llama-swap (GGUF) |
| Model registry | 11 vision + 4 text (Qwen3.6, Gemma 4, GLM-4.6V, Mistral) | Multilingual coverage |

## Files to read next

`stacks/mlx-omni/` · `stacks/litellm/config/config.yaml` (MLX entries) · `.agents/skills/mlx-omni/SKILL.md`
