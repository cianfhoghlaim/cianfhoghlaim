# llama-swap

OpenAI-compatible HTTP server that swaps between local GGUF models.
Backed by [`mostlygeek/llama-swap:v166`](https://github.com/mostlygeek/llama-swap),
mounted via Docker with the Apple Silicon Metal backend.

## Why this exists

The Canaveg `meaisínfhoghlaim` package needs an on-device GGUF runtime for
the small Unsloth-trained Celtic-language models. LiteLLM (which lives in
the same data-plane group) handles cloud-backed models; this stack is the
local-runtime sibling.

## Composition

```
┌──────────────────────────────────────────┐
│ llama-swap (host port 8080)              │
│   • GGUF cache : ../../stedding/huggingface/gguf   (read-only)
│   • Unsloth   : ../../stedding/huggingface/unsloth  (read-only)
│   • MLX       : ../../stedding/huggingface/mlx-community (read-only)
└──────────────────────────────────────────┘
```

The config (`config.yaml` → symlink to `../../ocr/models/llama_swap_config.yaml`)
defines which model is served at which alias. The Dagster `model_conversion`
asset converts HF models → GGUF into `stedding/huggingface/gguf/` — that's
the pipeline that populates this server's cache.

## Health check

```bash
curl http://localhost:8080/v1/models      # list available models
curl http://localhost:8080/health         # server liveness
```

## Deploy

```bash
# Local (assumes mise has hydrated .env + the GGUF cache is populated)
docker compose -f compose.yaml -f sidecar.yaml up -d

# Production via Komodo on bunchloch
km run procedure deploy-llama-swap-bunchloch
```
