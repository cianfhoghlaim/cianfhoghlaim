# Tasks: wire-v4-models-into-litellm-config

- [ ] 1. Generate the litellm config from the v4 registry:
  `python scripts/generate_litellm_config.py > cianfhoghlaim/stacks/litellm/config/config.yaml`
- [ ] 2. Validate the generated config:
  `python scripts/validate_litellm_config.py` (must pass)
- [ ] 3. Verify all 26 model_ids are live on HF Hub:
  `python scripts/verify_hf_hub_audit.py --strict`
- [ ] 4. Update the openspec validation runs to include
  `python scripts/validate_litellm_config.py` as a pre-commit hook
- [ ] 5. Add a CI step that fails the build if any v3 model name
  (`qwen2.5-vl`, `gemma-3-vision`, `deepseek-ocr`, `uccix-13b`)
  appears in `config.yaml`
- [ ] 6. Run `openspec validate wire-v4-models-into-litellm-config --strict`
- [ ] 7. Commit + push to origin/main
