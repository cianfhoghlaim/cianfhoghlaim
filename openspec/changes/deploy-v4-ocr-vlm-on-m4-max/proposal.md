## Why

The `2026-06-29-fix-ocr-vlm-registry-with-unfastened-priority` change
created a 24-entry v4 OCR/VLM registry. The user's M4 Max has 48 GB
unified memory, which can hold at most 1 of the 4 largest models
(qwen3-vl-235b-a22b 130GB, glm-4.6v-full 107GB,
qwen3.6-35b-a3b-mtp 22GB marginal, gemma-4-31B 19GB marginal).
The user wants the M4 Max to be the primary inference target
for all models that fit, with the 4 oversized models removed
from the v4 registry (no Modal inference fallback).

This change trims the v4 registry to **20 models** (down from
24), all fitting comfortably on the M4 Max 48 GB unified memory.

## What changes

- Remove 4 models from `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`:
  - `qwen3-vl-235b-a22b` (130GB, doesn't fit on M4 48GB)
  - `glm-4.6v-full` (107GB, doesn't fit on M4 48GB)
  - `qwen3.6-35b-a3b-mtp` (22GB, marginal; use `qwen3.6-27b-mtp` 16GB instead)
  - `gemma-4-31B` (19GB, marginal; use `gemma-4-26B-A4B` 14GB instead)
- Update the `litellm/config/config.yaml` to route 5 MLX community
  variants via `mlx-omni:10240` (per-model backend URL strategy)
- Deploy `spaces/oideachais-pdf-review/` to HF Spaces with ZeroGPU
  (the in-app "suggested correction" feature uses
  `unsloth/gemma-3-4b-it-GGUF` and "explain why this is
  mis-categorised" uses `unsloth/gemma-4-26B-A4B-it-GGUF`)
- Update `cianfhoghlaim/ocr/training/modal_finetune/finetune_irish.py`
  to fine-tune the v4 Gemma 4 31B (was Llama-3.2-3B) on Modal H100 80GB
- Update 3 spec files (meaisinfhoghlaim-ocr-htr, meaisinfhoghlaim-platform,
  oideachais-pdf-processing) to reflect the 20-model registry

## Impact

- All 20 v4 models fit on M4 Max 48 GB unified memory (llama-swap
  dynamic-loads 1 model at a time, so 1 model + 1 mmproj must fit
  at any moment — the 4 largest were over the budget)
- litellm routes 5 MLX community variants via mlx-omni (Apple
  Silicon-optimized); 15 GGUF models via llama-swap; 4 specialist
  models via transformers (PyTorch)
- HF Spaces ZeroGPU gives the public demo a free GPU for the
  in-app LLM features
- Modal is used for Irish fine-tuning only (not inference)

## Out of scope

- Re-introducing the 4 removed models on Modal (the user wants them
  removed entirely; smaller alternatives serve the same purpose)
- 3-party model additions beyond the v4 registry (e.g. Pixtral,
  Molmo2-8B-7B variant) — separate openspec changes
