# Tasks: pipeline-ocr-vision-activation

> Cross-batch OCR/Vision activation contract.
> Absorbs `2026-08-13-ocr-vision-activation-completion-v1` (0/15) +
> `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (0/107).

## 1. OCR vision activation completion (from ocr-vision-activation-completion-v1)

- [ ] **O1.1** Replace `_run_path_baml()` stub at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:266-283` (currently raises `NotImplementedError`)
- [ ] **O1.2** Replace `_ragas_vote()` stub at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:472-494` (uses inline scoring instead of canonical `evaluate_ensemble()`)
- [ ] **O1.3** Fix the `is_scanned_pdf()` function (no unit tests) — add ≥3 unit tests
- [ ] **O1.4** Wire Dagster fanout for scanned PDFs
- [ ] **O1.5** Fix the `biiep_v2` → `biiep_v3` MLflow docstring drift

## 2. Unsloth v5 vision integration (from unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1)

- [ ] **U2.1** Add `bonneagar/stacks/unsloth-serve/` (6-file GOLD_STANDARD + dual-host overrides)
- [ ] **U2.2** Add `compose.arm1-oci.yaml` (OCI arm1 host override)
- [ ] **U2.3** Add `compose.bunchloch.yaml` (Bunchloch host override)
- [ ] **U2.4** Add 20 NEW `MODEL_REGISTRY` entries (`backend="unsloth"`)
- [ ] **U2.5** Add 20 NEW LiteLLM route entries (5 model families × 4 host tiers)
- [ ] **U2.6** Wire Hermes Agent runtime to Unsloth-serve
- [ ] **U2.7** Wire OpenClaw runtime to Unsloth-serve
- [ ] **U2.8** Wire OpenChamber (= OpenCode UI + agent fleet) to Unsloth-serve
- [ ] **U2.9** Add the 10-way comparison marimo notebook (Qwen3.8 + Hermes + OpenClaw + OpenCode + 6 others)

## 3. Verification

- [ ] Run `openspec validate pipeline-ocr-vision-activation --strict` — pass
- [ ] Run `mise run vision:ensemble:smoke` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianchoshlaim
openspec validate pipeline-ocr-vision-activation --strict
```
