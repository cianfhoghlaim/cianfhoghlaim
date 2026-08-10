# llama-swap

## Purpose for the Cianfhoghlaim project

OpenAI-compatible HTTP server that swaps between local GGUF models
on bunchloch. Backed by [`mostlygeek/llama-swap:cpu`](https://github.com/mostlygeek/llama-swap)
(per the lakehouse-extensive-hydration-v1 change: `:v166` never existed
on GHCR, and Docker Desktop on macOS has no Metal GPU passthrough at
all — containers run in a Linux VM — so the `driver: metal` device
reservation this doc used to describe was never functional regardless
of image tag; both were fixed live). The `meaisínfhoghlaim` package
uses it for on-device GGUF inference of small Unsloth-trained
Celtic-language models and as the fallback for cloud-backed providers.

## Why it stays in komodo/pangolin/infisical GitOps

llama-swap is **local-only** (no Pangolin route, no public URL) —
it binds to `127.0.0.1:8080` on bunchloch and is reachable only
from within the agent-platform cluster network. The komodo
`deploy-llama-swap-bunchloch` procedure handles a 3-stage rollout:
(1) verify the GGUF cache is populated, (2) deploy the container,
(3) health-check the model list. Optional — if absent, all
inference falls back to litellm → cloud.

## Hardware + Cache

| Setting | Value |
|:--|:--|
| GPU | None — CPU-only (Docker Desktop on macOS has no Metal passthrough; a real GPU-accelerated deployment needs Linux+CUDA/ROCm, or llama-swap run natively on macOS outside Docker) |
| Context size | 32 768 (configurable via LLAMA_ARG_CTX_SIZE) |
| Layers offloaded to GPU | 0 (CPU-only, matching the GPU row above) |
| GGUF cache | `stedding/huggingface/gguf` (read-only bind mount) |
| Unsloth cache | `stedding/huggingface/unsloth` (read-only bind mount) |
| MLX-community cache | `stedding/huggingface/mlx-community` (read-only bind mount) |

## Cross-references

- **Ops**: `bonneagar/stacks/llama-swap/` (the 6-file GOLD_STANDARD + symlink to `../../../meaisinfhoghlaim/models/llama_swap_config.yaml`, confirmed live via `readlink`)
- **Code**: the `meaisinfhoghlaim/training/` training pipeline + the dagster `model_conversion` asset that converts HF → GGUF
- **Komodo procedure**: `deploy-llama-swap-bunchloch.toml` (3-stage)
- **Pangolin**: none (local-only)

## Tags

- `host:bunchloch`
- `tier:data-engineering` + `tier:language-model`
- `project:cianfhoghlaim`
