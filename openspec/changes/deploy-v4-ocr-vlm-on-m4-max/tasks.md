# Tasks: deploy-v4-ocr-vlm-on-m4-max

- [ ] 1. Trim the v4 VISION_MODELS registry in
  `cianfhoghlaim/ocr/models/registry.py` to remove the 4 oversized
  models: `qwen3-vl-235b-a22b`, `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`,
  `gemma-4-31B`
- [ ] 2. Update `cianfhoghlaim/ocr/models/llama_swap_config.yaml`
  to remove the same 4 entries
- [ ] 3. Update `cianfhoghlaim/ocr/models/vlm_finetune_comparison.py`
  to remove the same 4 entries from the `VLM_MODELS` dict
- [ ] 4. Update 3 openspec specs (meaisinfhoghlaim-ocr-htr,
  meaisinfhoghlaim-platform, oideachais-pdf-processing) to reflect
  the 20-model registry
- [ ] 5. Run the local test suite:
  `cd cianfhoghlaim && python -m pytest tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py -v`
- [ ] 6. Regenerate the litellm config from the v4 registry:
  `python scripts/generate_litellm_config.py > bonneagar/stacks/litellm/config/config.yaml`
- [ ] 7. Validate the litellm config:
  `python scripts/validate_litellm_config.py`
- [ ] 8. Download the 20 v4 GGUFs to M4:
  `python scripts/download_unsloth_models.py` (~25 GB)
- [ ] 9. Download the 5 MLX community variants to M4:
  `hf download mlx-community/<each-model> --local-dir /stedding/huggingface/mlx-community/`
- [ ] 10. Start llama-swap + mlx-omni + litellm on M4:
  `cd bonneagar/stacks/<stack> && docker compose up -d`
- [ ] 11. Deploy `spaces/oideachais-pdf-review/` to HF Spaces with
  ZeroGPU (per the updated app.py + requirements.txt + README.md)
- [ ] 12. Update `cianfhoghlaim/ocr/training/modal_finetune/finetune_irish.py`
  to use `unsloth/gemma-4-31B-it-GGUF` on Modal H100 80GB
- [ ] 13. Run `openspec validate deploy-v4-ocr-vlm-on-m4-max --strict`
- [ ] 14. Commit + push to origin/main
