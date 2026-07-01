# ci/hf-watchdog

## Purpose for the Cianfhoghlaim project

Daily HF Hub liveness check for the v4 OCR/VLM registry. Verifies every model_id in `cianfhoghlaim.ocr.models.VISION_MODELS` against the HF Hub API. Posts a Slack alert on any 404.

## Why it stays in komodo/pangolin/infisical GitOps

Runs as a daily container on bunchloch with zero side effects (no HTTP surface, no data persistence, no Pangolin route). Locket resolves the optional Slack webhook from Infisical; if the secret is absent, the watchdog logs to stdout instead. Reproducible via the IaC bootstrap; the Python watchdog code is part of the cianfhoghlaim package (not bundled in the ops dir).

## Cross-references

- **Ops**: `bonneagar/stacks/ci/hf-watchdog/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/ci/hf_watchdog.py` (the watchdog module)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:ci` + `project:cianfhoghlaim` + `v4:consolidated`
- **Pangolin**: not exposed (no HTTP surface; outbound HF Hub API calls only)

## Tags

- `host:bunchloch`
- `tier:ci`
- `project:cianfhoghlaim`
- `v4:consolidated`
