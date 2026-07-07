## Why

The `2026-06-29-fix-ocr-vlm-registry-with-unfastened-priority` change
introduced 14 new Unsloth-backed v4 models in the registry, but the
`llama-swap` service stack does not exist yet. The `litellm` config
references `http://llama-swap:8080/v1` for the GGUFs, but no service
serves them. This change creates the `llama-swap` v166 stack at
`infrastructure/stacks/llama-swap/` to serve the 14 v4 Unsloth GGUFs.

## What changes

- Create `infrastructure/stacks/llama-swap/` with the 6-file
  GOLD_STANDARD pattern (compose.yaml, sidecar.yaml, secrets.env,
  pangolin.yaml, blueprint.yaml, .env.example)
- Symlink the v4 config: `llama-swap/config.yaml` →
  `../../ocr/models/llama_swap_config.yaml`
- Add 5 mise tasks: `llama-swap:up`, `llama-swap:down`,
  `llama-swap:logs`, `llama-swap:download-models`, `llama-swap:health`
- Pre-download the 14 v4 Unsloth GGUFs to `/models/unsloth/`
  (5-50 GB total) via `python scripts/download_unsloth_models.py`
- Deploy to arm1-oci via Komodo

## Impact

- The 14 v4 Unsloth GGUFs are now served at
  `http://llama-swap:8080/v1/chat/completions`
- LiteLLM can route to the v4 models (the `local/vision/<key>` entries
  from the `wire-v4-models-into-litellm-config` change)
- The 6-stage PDF pipeline can run Stage 1 (OCR) on a real model

## Out of scope

- Cloud deployment (the user has explicit M4 Max 48 GB + arm1-oci)
- Multi-GPU (llama-swap v166 has single-GPU mode; multi-GPU
  would require v178+ which is not yet released)
