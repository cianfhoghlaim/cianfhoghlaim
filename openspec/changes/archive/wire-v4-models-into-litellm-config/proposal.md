## Why

The `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority` change
(archived 2026-06-29) added the 24-entry `VISION_MODELS` registry at
`cianfhoghlaim/ocr/models/registry.py`. But the `litellm/config/config.yaml`
was not updated — it still has the v3 model names (`qwen2.5-vl-7b`,
`gemma-3-vision`, `deepseek-ocr`, `uccix-13b`). This change wires all
14 v4 Unsloth-backed models into the LiteLLM gateway config so the
BAML clients + the 6-stage PDF pipeline can reach them.

## What changes

- Add 14 new `local/vision/<model_key>` entries to
  `cianfhoghlaim/stacks/litellm/config/config.yaml:model_list:`
- Add 9 v4 aliases: `vision`, `ocr`, `diagram`, `gaelic`,
  `irish`, `default`, `math`, `extract`, `embedding-bge-m3`
- Update the master `router_settings.fallbacks` list to use the v4
  primary keys
- Add the `hf:verify-ocr-registry`, `litellm:regenerate`,
  `litellm:validate` mise tasks (already in `mise.toml` per the
  parent change)
- Mirror the rewrite to the production copy of `config.yaml` after
  validation by `python scripts/validate_litellm_config.py`

## Impact

- 26 v4 model entries (vs 11 in the v3 config)
- 9 v4 aliases with explicit fallback chains
- All model_ids verified live on HF Hub via
  `python scripts/verify_hf_hub_audit.py` (17 Unsloth + 26 upstream = 100%)
- Backwards-compatible: the v3 aliases (`qwen2.5-vl`, `gemma-3-vision`)
  are removed in this change; the v4 `vision` alias routes through
  `local/vision/qwen3-vl-8b`

## Out of scope

- The llama-swap deployment (separate change `deploy-llama-swap-v166-stack`)
- The 6-stage PDF pipeline production wiring (separate change
  `wire-6-stage-pdf-pipeline-to-production`)
