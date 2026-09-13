---
name: llama-swap
description: Dynamic GGUF model swapping server for local LLM inference. Routes the `local/vision/*` and `local/unsloth/*` litellm aliases through llama-swap:8080. Use when adding/changing GGUF models in the Litellm gateway, or when troubleshooting GPU/CPU inference on the llama-swap daemon. Per the 2026-08-08-lakehouse-extensive-hydration-v1 change, llama-swap runs as `:cpu` (LLAMA_ARG_NGL=0) on Docker Desktop macOS — Metal GPU passthrough is NOT supported in Docker Desktop on macOS, so real GPU acceleration requires running llama-swap natively on the host (not in Docker).
---

# Llama-Swap - Dynamic GGUF Swapping Server

**Version:** v166 (image tag, but `:cpu` is the working one) | **Last Updated:** 2026-09-12

## Overview

Llama-swap is a dynamic model-swapping OpenAI-compatible server. It hosts
GGUF Q4_K_M models on :8080 and is the **only inference backend for the
`local/vision/*` LiteLLM aliases** (gemma-4, qwen3-vl, internvl3, etc.)

| Component | Value |
|-----------|-------|
| Image | `ghcr.io/mostlygeek/llama-swap:cpu` (CPU-only) |
| Port | 8080 (host) → 8080 (container) |
| Config | `/etc/llama-swap/config.yaml` |
| LLM routing | `local/vision/*` (via litellm :4000) |

## When to Use This Skill

- Adding a new GGUF model to llama-swap's model catalog
- Configuring `LLAMA_ARG_NGL` (GPU layers offloaded; 0 = CPU-only)
- Debugging slow inference (CPU vs Metal GPU)
- Switching from `:cpu` to a GPU-capable image (requires Linux host)

## GPU vs CPU Reality Check

Per the `2026-08-08-lakehouse-extensive-hydration-v1` commit message in
`bonneagar/stacks/llama-swap/compose.yaml`:

> **The `deploy.resources.reservations.devices: driver: metal` setting
> is NOT a real Docker feature.** Docker Desktop on macOS runs containers
> in a Linux VM with no Metal GPU passthrough of any kind, so this config
> could never have actually gotten GPU acceleration regardless of image
> tag. Switched to the real `:cpu` backend tag and `LLAMA_ARG_NGL=0` (0
> GPU layers, matching CPU-only reality) -- CPU inference on an 8B VLM
> is slow but genuinely works.

**For real GPU acceleration**, options are:
1. **Linux host with CUDA/ROCm**: change image tag from `:cpu` to a GPU tag
2. **macOS host, run llama-swap natively** (not in Docker): bypasses Docker Desktop
3. **Hetzner CAX/LGPU server**: deploy on the production GPU server

## Models Hosted

~24 GGUF models including:
- `gemma-4-9B-it-GGUF` (crosses the "thinking" threshold)
- `gemma-4-26B-A4B-it-GGUF` (26.5B MoE / 4B active, 14GB)
- `qwen3-vl-8b-instruct-q4_k_m` (vision-language)
- `internvl3-8b` (vision)
- ~20 more in `local/unsloth/*` and `local/vision/*` aliases

## Configuration File (`config.yaml`)

Located at `bonneagar/stacks/llama-swap/config.yaml` (mounted to
`/etc/llama-swap/config.yaml` in the container).

```yaml
models:
  - name: gemma-4-12b
    path: /models/gemma-4-12b-it.Q4_K_M.gguf
    context_size: 8192
    ngl: 0  # CPU-only (Docker Desktop on macOS)
```

## ⚠️ CURRENT STATUS (2026-09-12, Plan 3 audit)

- **Image tag**: `:cpu` (verified working, `:v166` doesn't exist on GHCR)
- **LLAMA_ARG_NGL**: 0 (CPU-only)
- **Working**: ✅ Confirmed - BAML clients route through litellm → llama-swap successfully
- **52 models** in litellm config route through llama-swap
- **Bottleneck**: Vision models (qwen3-vl-8b, gemma-4-VL) are slow on CPU (~30s/request)
- **Production fix**: deploy llama-swap on Linux GPU host or CAX41-LGPU server

## Cross-References

- **BAML clients**: `baml_src/clients_llama_swap.baml` (4 clients: LlamaSwapClient, LlamaSwapOCRClient, LlamaSwapExtractionClient, LlamaSwapReasoningClient)
- **litellm config**: `bonneagar/stacks/litellm/config/config.yaml` references `http://llama-swap:8080/v1`
- **Stack compose**: `bonneagar/stacks/llama-swap/compose.yaml`
