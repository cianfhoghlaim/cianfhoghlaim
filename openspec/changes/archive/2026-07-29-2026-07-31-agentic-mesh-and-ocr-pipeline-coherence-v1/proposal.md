# 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1

## Why

The 3 agent surfaces (openchamber, openclaw, hermes) and the 6 OCR /
VLM-model backends (paddleocr, dots-ocr, olmocr, docling-serve, mlx-omni,
llama-swap) are individually healthy but **the cross-surface wiring is
absent**. Concrete gaps surfaced from the 2026-07-29 full-tree audit:

1. **No agent-to-agent context handoff.** The 3 surfaces share a Docker
   network but no protocol exists for one surface to hand a context
   envelope to another. A request that lands in openclaw (channel
   fanout) cannot route to hermes (mature agent runtime) or openchamber
   (IDE/CLI) beyond a static URL.
2. **litellm has 7 dead model routes.** `config.yaml.full.bak` enumerates
   28 models but only 3 are active (in `config.dev.yaml`). The remaining
   25 split into:
   - 7 routes pointing at `http://transformers:5000/v1` — a service that
     does NOT exist. Affected models: `deepseek-ocr-2`,
     `olmocr-2-7b-1025`, `uccix-mistral-24b`, `uccix-llama-3.1-8b`,
     `molmo2-4b`, `molmo2-8b` (+1 more).
   - 8 `fallback_chain` schema mismatches (litellm 1.x wants dicts, the
     .bak file has strings).
3. **2 OCR stacks have disconnected Pangolin routes.** `paddleocr` and
   `dots-ocr` both declare `blueprint.yaml` private resources but their
   `pangolin.yaml` files are `noop: true`. The routes are unreachable.
4. **No OCR completion webhook.** Every OCR backend is synchronous
   `POST → result`. There is no convention for OCR completion to push
   to downstream pipelines (Dagster sensors cannot subscribe).
5. **llama-swap config.yaml symlink is broken.** Points at
   `../../ocr/models/llama_swap_config.yaml` but `bonneagar/ocr/` does
   not exist. The real config lives at
   `meaisinfhoghlaim/models/llama_swap_config.yaml`. llama-swap will not
   start in production.

This change ships the wiring that the agent + OCR story depends on.
It depends on Change 1 (`2026-07-30-env-contract-and-observability-fanout-v1`)
already landing — the URI grammar is now unified, so the new env vars
land in the canonical form.

## What changes

This is a single openspec change with 6 sub-areas.

### Sub-area A — Cross-agent context handoff protocol

- **NEW**: `agents/contracts/context-envelope.py` — Pydantic v2 model
  (`agent_run_id`, `parent_trace_id`, `context_payload`, `mtls_subject`,
  `created_at`, `expires_at`) + canonical handoff signatures
- **NEW**: 3 handler modules (one per surface: `openchamber_handler.py`,
  `openclaw_handler.py`, `hermes_handler.py`)

### Sub-area B — ocr-router stack

- **NEW**: `bonneagar/stacks/ocr-router/` with 6 GOLD files hosting a
  single FastAPI service that maps `requested capability` → best-fit
  backend (paddleocr for forms, dots.ocr / mlx-omni for layout, olmocr
  for tables+latex, docling-serve for DocTags, llama-swap for Ga/EN
  vision)

### Sub-area C — litellm config repair

- **MODIFIED**: `bonneagar/stacks/litellm/config/config.yaml.full.bak` —
  fix the 8 `fallback_chain` schema mismatches (litellm 1.x wants
  dicts, not strings)
- **MODIFIED**: `bonneagar/stacks/litellm/config/config.yaml.full.bak` —
  rewrite the 7 dead `transformers` routes to existing real services:
  - `deepseek-ocr-2` → `http://docling-serve:5001/v1`
  - `olmocr-2-7b-1025` → `http://olmocr:8003/v1`
  - `uccix-mistral-24b` → `http://mlx-omni:10240/v1` (confidence=low rule)
  - `uccix-llama-3.1-8b` → `http://mlx-omni:10240/v1` (confidence=low)
  - `molmo2-4b` → `http://docling-serve:5001/v1`
  - `molmo2-8b` → `http://docling-serve:5001/v1`
  - (7th route: see change rationale)
- **MODIFIED**: promote `config.yaml.full.bak` → `config.yaml` (the 12-
  line stub currently in `config.yaml` becomes the .bak)
- **MODIFIED**: `bonneagar/stacks/litellm/config/config.dev.yaml` —
  remove the now-dead `transformers` references

### Sub-area D — OCR Pangolin fixes + symlink fix

- **MODIFIED**: `bonneagar/stacks/paddleocr/pangolin.yaml` — replace
  `noop: true` with a real Traefik overlay routing
  `paddleocr.cianfhoghlaim.ie` → `paddleocr:8000` (TinyAuth +
  secure-headers middleware)
- **MODIFIED**: `bonneagar/stacks/dots-ocr/pangolin.yaml` — same fix
  for `dotsocr.cianfhoghlaim.ie` → `dots-ocr:8001`
- **MODIFIED**: `bonneabar/stacks/llama-swap/config.yaml` —
  re-point the broken symlink from
  `../../ocr/models/llama_swap_config.yaml` (target doesn't exist) to
  `../../meaisinfhoghlaim/models/llama_swap_config.yaml`

### Sub-area E — OCR webhook convention + dagster sensor

- **MODIFIED**: `bonneagar/stacks/ocr-router/compose.yaml` — emit
  `OCR_WEBHOOK_URL` on every `POST /ocr` completion
- **NEW**: `orchestration/sensors/ocr_completion_sensor.py` — Dagster
  sensor that consumes the webhook, materialises a per-document OCR
  completion asset, and triggers downstream pipeline assets

### Sub-area F — Cross-agent URL wiring

- **MODIFIED**: `openclaw/.env.example` — add
  `OPENCLAW_OPENCHAMBER_URL`, `OPENCLAW_HERMES_URL`,
  `OPENCLAW_HERMES_BRIDGE_TOKEN`
- **MODIFIED**: `openchamber/.env.example` — add
  `OPENCHAMBER_OPENCLAW_URL`, `OPENCHAMBER_HERMES_URL`,
  `OPENCHAMBER_HERMES_BRIDGE_TOKEN`
- **MODIFIED**: `hermes/.env.example` — add
  `HERMES_OPENCLAW_URL`, `HERMES_OPENCHAMBER_URL`,
  `HERMES_OPENCHAMBER_BRIDGE_TOKEN`

## Definition of done

- [ ] All 6 sub-areas above land
- [ ] `openspec validate 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 --strict` passes
- [ ] `mise run stack-doctor:strict` reports zero grammar regressions in the modified stacks
- [ ] `docker compose -f ocr-router/compose.yaml -f ocr-router/sidecar.yaml config --quiet` passes
- [ ] `python -m py_compile agents/contracts/context-envelope.py` succeeds
- [ ] 1 commit lands on the working branch with the spec delta + 2 spec files
- [ ] Push succeeds

## Dependencies

- **Blocked by**: `2026-07-30-env-contract-and-observability-fanout-v1` (URI
  grammar must be unified before any new env vars land; otherwise they
  land in the wrong form)
- **Blocks**: `2026-08-01-lakehouse-and-reproducible-deploy-v1` (the
  `deploy:full` orchestrator depends on the agentic mesh being coherent)

## Why a single change (not 6)?

Sub-areas A–F are co-dependent:

- (B) requires (A) — the ocr-router stack needs the context-envelope
  for request routing
- (C) requires (E) — the OCR webhook must be live for the litellm
  dead-route fixes to be observable
- (D) requires (B) — the disconnected routes are downstream of the
  ocr-router
- (F) is the connective tissue between (A) and the 3 surfaces

Splitting into 6 PRs would require 6 rebases against this same change.
One PR, ~22 file diffs, lands cleanly.

## Cross-repo sync

This change touches only this repo (cianfhoghlaim). No `cross-repo-sync.md`
needed. The `leabharlann` corpus repo is unaffected.