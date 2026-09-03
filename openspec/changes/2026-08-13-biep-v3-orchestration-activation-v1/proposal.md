# Change: BIEP v3 orchestration activation (close the 2 deployment-side blockers)

## Why

The BIEP v2 OCR/VLM ensemble code (per
`2026-08-13-ocr-vision-activation-completion-v1`) is now correct
end-to-end, but **the deployment-side wiring is incomplete** in 2
critical ways:

1. **litellm Komodo redeploy blocker** — The litellm proxy at
   `http://litellm:4000/v1` (the workhorse endpoint for `qwen3-vl-8b`
   + the OpenAI-compatible layer for the entire VLM ensemble) is
   crash-looping because of a malformed `router_settings.fallbacks`
   in the deployed `~/.komodo-stacks/litellm/config/config.yaml`. The
   fix was applied to the repo source
   (`bonneagar/stacks/litellm/config/config.yaml:638-647`) by the
   `2026-08-08-lakehouse-extensive-hydration-v1` change but the
   deployed container is a Komodo-managed copy outside the worktree —
   per the lakehouse-hydration proposal (`proposal.md:93-95`): "the
   actually-deployed instance is a separate Komodo-managed stack
   outside this repo/worktree that needs a manual redeploy to pick up
   the fix."

2. **llama-swap missing GGUF weights** — The `llama-swap` container
   has no GGUF model weights locally; the path
   `stedding/huggingface/gguf/` doesn't exist on the local
   filesystem. The lakehouse-hydration change's D2a explicitly
   states "bringing it up would start an empty container with no
   models to serve." The 17 OCR models referenced by
   `meaisinfhoghlaim/models/llama_swap_config.yaml` are
   `unsloth/...-GGUF` Hub IDs that haven't been downloaded.

Without closing these 2 deployment-side blockers, every BAML
`ExtractSyllabusDiagram` call, every `biiep_ocr_ensemble` asset, and
every agent vision path is dark. Cloud fallbacks (Gemini, OpenCode
Go) work but cost $$$ and route to external APIs — defeating the
local-first inference architecture.

## What Changes

- **Add `scripts/download_gguf_weights.py`** — a 50-LOC script that
  downloads the 17 GGUF model files from HuggingFace Hub via the
  `hf` CLI into `stedding/huggingface/gguf/`. Priority order:
  `gemma-4-26B-A4B` (M4 default), `qwen3-vl-8b` (workhorse),
  `qwen3.6-27b-mtp` (text-only mark), then the 14 specialist /
  legacy models.
- **Add `scripts/verify_litellm_redeploy.sh`** — a 30-line shell
  script that runs the `km deploy stack litellm --force` against
  the bunchloch Komodo periphery, waits for the container to be
  healthy, and asserts that the new config is in effect
  (`docker exec litellm cat /app/config.yaml | grep -A 5
  router_settings` should now have a dict, not a bare list).
- **Run `scripts/run_biiep_ocr_ensemble.py` end-to-end** against the
  11 chemistry syllabus PDFs + the 139-document corpus, verifying
  RAGAS-voted canonical rows land in `md:cianfhoghlaim.ocr_results`.
- Add a new `infrastructure-stacks` spec requirement formalising the
  "litellm + llama-swap MUST be redeployed + GGUF-loaded before any
  BIEP v2 OCR asset can run" invariant.

## Dependencies

`Blocked by: none`. `Blocked by (soft):
2026-08-13-bonneagar-infra-remediation-v3` (Plan I-C — the working-tree
fixes need to be committed and pushed to the canonical repo before
the `km deploy stack litellm` can pick them up). `Affected repos:
cianfhoghlaim (single repo) + 1 Komodo-managed stack outside the
worktree (manual operator action for the redeploy)`.

## Impact

- Capabilities: MODIFIED `infrastructure-stacks` (1 ADDED Requirement).
- Code: new `scripts/download_gguf_weights.py` (~50 LOC) + new
  `scripts/verify_litellm_redeploy.sh` (~30 LOC) + 1 runbook entry.
- Risk: high — manual redeploy of a Komodo-managed container + 60-80
  GB of GGUF downloads; mitigated by the smoke test at the end of
  Phase E (gated on Plan V-B's un-stubbing work).

## Success criteria

1. `docker logs litellm` shows zero `Router.validate_fallbacks`
   errors after the redeploy.
2. `curl http://llama-swap:8080/v1/models` returns 17 model IDs
   matching the registry's `llama_swap_config.yaml`.
3. `python scripts/run_biiep_ocr_ensemble.py --pdf
   <chemistry_syllabus.pdf>` returns `ragas_score >= 0.70` and
   `voted_path in {baml, unstract, qwen3_vl, gemma4}`.
4. `SELECT COUNT(*) FROM md:cianfhoghlaim.ocr_results` returns ≥ 4
   rows per PDF (4 paths per PDF).
5. `openspec validate 2026-08-13-biep-v3-orchestration-activation-v1
   --strict` returns 0 errors.
