# Tasks: deploy-llama-swap-v166-stack

- [ ] 1. Create the 6-file GOLD_STANDARD pattern at
  `infrastructure/stacks/llama-swap/` (already done in the parent
  change; verify with `ls -la infrastructure/stacks/llama-swap/`)
- [ ] 2. Symlink the v4 config:
  `ln -sf ../../ocr/models/llama_swap_config.yaml
   infrastructure/stacks/llama-swap/config.yaml`
  (already done)
- [ ] 3. Add 5 mise tasks (already done in the parent change; verify
  with `mise tasks | grep llama-swap`)
- [ ] 4. Pre-download the 14 v4 Unsloth GGUFs:
  `python scripts/download_unsloth_models.py` (~30 min, 5-50 GB)
- [ ] 5. Pre-download the 5 MLX community GGUFs:
  `python scripts/download_unsloth_models.py --only mlx`
- [ ] 6. Start the service: `mise run llama-swap:up`
- [ ] 7. Verify the service is healthy:
  `mise run llama-swap:health` (must return 14+ models)
- [ ] 8. Deploy to arm1-oci via Komodo:
  `mise run komodo:deploy-llama-swap`
- [ ] 9. Run `openspec validate deploy-llama-swap-v166-stack --strict`
- [ ] 10. Commit + push to origin/main
