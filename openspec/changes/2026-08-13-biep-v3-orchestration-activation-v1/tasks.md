# Tasks: BIEP v3 orchestration activation

## Phase A — Add the deployment-side scripts (1 task, ~1 hour)

- [ ] A1 Create `scripts/download_gguf_weights.py` — a 50-LOC
  script that downloads the 17 GGUF model files from HuggingFace
  Hub via the `hf` CLI into `stedding/huggingface/gguf/`. Reads the
  priority order from `meaisinfhoghlaim/models/llama_swap_config.yaml`.

- [ ] A2 Create `scripts/verify_litellm_redeploy.sh` — a 30-line
  shell script that runs `km deploy stack litellm --force`, waits
  for healthy, and asserts the new config is in effect.

## Phase B — Download the GGUF weights (1 task, ~30 min active + ~60-80 GB transfer)

- [ ] B1 Verify `hf auth whoami` succeeds against the cianfhoghlaim
  account (per `huggingface_hub` auth context).
- [ ] B2 Run `python scripts/download_gguf_weights.py` (downloads
  17 GGUF files in priority order; resumable).
- [ ] B3 Verify `ls -lah stedding/huggingface/gguf/ | wc -l` returns
  17 + header row.

## Phase C — Redeploy litellm (1 task, ~30 minutes; operator action)

- [ ] C1 Confirm the canonical `litellm/config/config.yaml` matches
  the deployed `~/.komodo-stacks/litellm/config/config.yaml`
  (`diff <(curl -s komodo.cianfhoghlaim.ie/api/stacks/litellm/config)
  bonneagar/stacks/litellm/config/config.yaml`).
- [ ] C2 If different: `cp bonneagar/stacks/litellm/config/config.yaml
  ~/.komodo-stacks/litellm/config/config.yaml`.
- [ ] C3 Run `bash scripts/verify_litellm_redeploy.sh` (does
  `km deploy stack litellm --force` + waits for healthy).
- [ ] C4 Verify `docker logs litellm` shows zero
  `Router.validate_fallbacks` errors.

## Phase D — Bring up llama-swap (1 task, ~10 minutes)

- [ ] D1 `cd bonneagar/stacks/llama-swap && docker compose up -d`.
- [ ] D2 Verify `curl http://llama-swap:8080/v1/models` returns
  the 17 model IDs.

## Phase E — Run the 4-path ensemble end-to-end (1 task, ~15 minutes)

- [ ] E1 `python scripts/migrate_ocr_results_table.py` (creates
  `md:cianfhoghlaim.ocr_results`).
- [ ] E2 `python scripts/run_biiep_ocr_ensemble.py --pdf
  <chemistry_syllabus.pdf>` (real end-to-end, should produce ≥ 1
  RAGAS-voted canonical row with `ragas_score >= 0.70`).
- [ ] E3 `python scripts/run_biiep_ocr_ensemble.py --all-corpus`
  (runs against all 139 documents; writes 4 rows per document to
  `md:cianfhoghlaim.ocr_results`).

## Phase F — Validate (3 tasks, ~15 minutes)

- [ ] F1 `openspec validate
  2026-08-13-biep-v3-orchestration-activation-v1 --strict` returns
  0 errors.
- [ ] F2 `mise run lint:registry && mise run lint:skills`.
- [ ] F3 `mise run sync:all` passes.

## Out of scope (flagged for follow-up)

- The 4 additional Litellm-redeploy hazards documented in
  `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
  (Traefik missing routers + offline-site bindings) — covered by
  `2026-08-13-edge-routing-and-offline-site-remediation-v1` (Plan I-B).
- The litellm model alias reconciliation (committed in
  `2026-08-13-bonneagar-infra-remediation-v3` / Plan I-C; this change
  consumes the result).
