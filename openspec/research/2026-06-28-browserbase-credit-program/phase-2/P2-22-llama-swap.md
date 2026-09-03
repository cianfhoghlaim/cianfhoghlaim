# P2-22 — llama-swap (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

llama-swap is the **dynamic GGUF model swapper** that serves all local GGUF models (Qwen 2.5 Math, Qwen3.6, Llama 3.3, Mistral) on the MacBook M4 Max (48 GB unified memory). It's the offline safety net in the LiteLLM `minimax` 7-tier fallback chain.

The canonical Cianfhoghlaim pattern: llama-swap exposes an OpenAI-compatible API at `:8080`; LiteLLM routes to it as the final tier when all cloud providers fail.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/llama-swap/compose.yaml` | llama-swap service (port 8080) |
| `stacks/llama-swap/config.yaml` | Model registry (8 GGUF models) |
| `stacks/llama-swap/models/` | Pre-downloaded GGUF files (Q4_K_M quantized) |
| `cognify/rules/llama_swap_models.py` | Lists 8 active GGUF models |

**Canonical llama-swap config** (`stacks/llama-swap/config.yaml`):

```yaml
models:
  math/qwen25-math:
    name: "Qwen 2.5 Math 7B (GGUF Q4_K_M)"
    path: "/models/qwen25-math-7b-instruct-q4_k_m.gguf"
    context_size: 4096
  code/llama33-70b:
    name: "Llama 3.3 70B (GGUF Q4_K_M)"
    path: "/models/llama33-70b-instruct-q4_k_m.gguf"
    context_size: 8192
  general/mistral-nemo:
    name: "Mistral Nemo 12B (GGUF Q4_K_M)"
    path: "/models/mistral-nemo-12b-q4_k_m.gguf"
    context_size: 8192
  irish/gaelic-tinyllama:
    name: "Gaelic TinyLlama 1.1B (GGUF Q4_K_M)"
    path: "/models/gaelic-tinyllama-1.1b-q4_k_m.gguf"
    context_size: 2048
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `LLAMA_SWAP_API_URL` | `http://llama-swap:8080/v1` | compose env |
| `LLAMA_SWAP_MASTER_KEY` | `not-needed` (local only) | compose env |
| `MODELS_DIR` | `/Users/cianmacandeisigh/.cache/llama-swap` | per-host |

## CCC anchors

`stacks/llama-swap/` · `cognify/rules/llama_swap_models.py` · `stacks/litellm/config/config.yaml` (local/math/qwen25-math entry)

Search terms: `"llama-swap"`, `"GGUF"`, `"Q4_K_M"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-12 | Initial llama-swap deploy (qwen2.5-math only) |
| 2026-02 | Added 5 more models (Mistral, Llama, Phi-3, Gemma-2, TinyLlama-Irish) |
| 2026-05 | Added to LiteLLM `minimax` 7-tier fallback (final tier) |

## Anti-patterns

1. Don't run llama-swap on arm1-oci — too slow (no M-series GPU)
2. Don't load >2 models simultaneously — M4 has 48GB unified, each Q4_K_M model uses ~5GB
3. Don't use llama-swap for embeddings — use a dedicated embedding server (gte-Qwen2)
4. Don't use llama-swap for vision — use MLX-omni instead

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hosting | MacBook M4 Max only | Apple Silicon = fastest GGUF |
| Quantization | Q4_K_M | Best size/quality trade-off |
| Context size | 2048-8192 (per model) | Match model's training |
| Hot-swap | Yes (dynamic per-request) | One process, many models |
| Fallback tier | 7th (last) in `minimax` chain | Offline safety net |

## Files to read next

`stacks/llama-swap/` · `cognify/rules/llama_swap_models.py` · `.agents/skills/llama-swap/SKILL.md`
