# Unsloth v5 Integration — Hermes + OpenClaw + OpenCode + Qwen3.8 + Marimo 10-Way Comparison

## Why

The cianfhoghlaim stack has **two parallel inference surfaces** that don't know about each other:

1. **The M3 chokepoint** — 5 LiteLLM-routed upstream models (Kimi-K2.6, GLM-5.1, MiniMax-M2.5, Mimo-V2.5, DeepSeek-V4-Flash) consumed via OpenCode-Go. Token-metered on the MiniMax M3 plan.
2. **The local OCR/VLM roster** — 14 GGUF entries on llama-swap :8080 served by the v4 vision registry. Free, but stale (no Qwen3.8, DeepSeek-V4, Kimi-K2.7-Code).

Unsloth 2026-08 added a **3rd surface** that the cianfhoghlaim stack has not wired up:

3. **Unsloth Studio + `unsloth start <agent>`** — a single OpenAI/Anthropic-compatible endpoint on `:8888` that auto-configures Claude Code, OpenAI Codex, Hermes, OpenClaw, OpenCode, and Pi Coding Agent against a local model. Ships tool calling, code execution, web search, and self-healing tool calls. Free, local, offline.

The 5 Unsloth agent integrations (`opencode`, `openclaw`, `hermes-agent`, `claude-code`, `codex`) all converge on the same pattern:

```
unsloth start <agent> --model unsloth/<model>:UD-Q4_K_XL
```

This is the missing piece. It unifies the 5 agent runtimes (Hermes, OpenClaw, OpenChamber = OpenCode UI, plus the agent fleet in `agents/meaisinfhoghlaim/`) against a single local-model serving surface, with zero token cost.

The 2nd motivation is **model staleness**: the current `MODEL_REGISTRY` has 52 entries; the Unsloth catalog has 80+ GGUF/Dynamic 3.0/BnB-4bit/NVFP4 entries since 2026-08 across 7 families (vision, text, embedder, image, voice, translation, diffusion). The 20 most important new ones are listed in §Layers below.

The 3rd motivation is **operational**: with the M3 token plan, users hit quota mid-day. The current fallback is to switch to a different LiteLLM upstream — but every upstream is metered. The Unsloth-served local fallback is **free + offline**.

## What changes

### New Bonneagar stack: `unsloth-serve` (dual-host)

A new GOLD_STANDARD 6-file Docker Compose stack at `bonneagar/stacks/unsloth-serve/` with **two host-specific override files**:

- **`compose.arm1-oci.yaml`** — GPU variant (`-ngl 99`, 12 GB limit, public via Pangolin `unsloth-api.cianfhoghlaim.ie`). Production serving for hermes/openclaw/webchat.
- **`compose.bunchloch.yaml`** — CPU/MPS variant (`-ngl 0`, 8 GB limit, `127.0.0.1:8889` only). Dev-mode + the marimo comparison notebook + the Studio UI.

The base compose file is shared; the two override files differ only in `image`, `LLAMA_ARG_NGL`, `deploy.resources.limits.memory`, and the Pangolin `expose` block.

The container runs:

```bash
unsloth run \
  --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL \
  --host 0.0.0.0 --port 8889 \
  --temp 0.7 --top-p 0.95 --top-k 20 \
  --chat-template-kwargs '{"reasoning_effort":"medium"}' \
  --disable-tools
```

### 20 new MODEL_REGISTRY entries

Extends `meaisinfhoghlaim/models/model_registry.py` with 20 new Unsloth catalog entries spanning all 7 families:

- **10 text_llm**: Qwen3.8-27B + Qwen3.8-2.4T-A95B (MoE), DeepSeek-V4-Pro-0813, DeepSeek-V4-Flash-0731, Kimi-K2.7-Code, Kimi-K3, NVIDIA Nemotron-3.5-Lightning-30B-A3B, Muse Glimmer-30B, MiniMax-M2.5, Magistral-Small-2509
- **4 ocr_vision**: Qwen3-VL-8B-Instruct, Qwen3-VL-32B-Instruct, GLM-4.6V-Flash, DeepSeek-OCR-2
- **2 image_gen**: DiffusionGemma-26B-A4B, Qwen-Image-2512
- **2 embedder**: Qwen3-Embedding-4B, EmbeddingGemma-300M
- **2 voice**: Orpheus-TTS-3B, Sesame-CSM-1B

All entries have `backend="unsloth"` (new enum value), `available=True` (verified live on HF per the 2026-08-15 audit), and `litellm_alias="local/unsloth/<key>"`.

### 20 new LiteLLM route entries

Extends `bonneagar/stacks/litellm/config/config.yaml` with 20 new model entries (one per registry entry) all routing to `http://unsloth:8889/v1` with `api_key=os.environ/UNSLOTH_API_KEY`. The `vision`, `text`, and `coding` aliases flip their primary to the unsloth-served backend, with the existing llama-swap + cloud Gemini fallback chains preserved.

### Single shared secret

One new Infisical secret: `infisical://dev-baile/unsloth/api-key` (single shared, not per-agent). All 5 agent stacks (hermes, openclaw, openclaw-arm1-oci, openchamber, openchamber-arm1-oci, cianfhoghlaim's coding agents) read the same key via the Locket sidecar.

### Hermes + OpenClaw + OpenCode provider wiring

- **Hermes** (`bonneagar/stacks/hermes/config/hermes.yaml`): add a 2nd provider block pointing at `http://unsloth:8889/v1` with 3 model aliases (Qwen3.8 + DeepSeek-V4-Pro + Magistral-Small). Container entrypoint branches on `UNSLOTH_PROVIDER` env var (`true` → `unsloth start hermes`, `false` → existing Hermes CLI).
- **OpenClaw** (`bonneagar/stacks/openclaw/config/openclaw.json`): add a 2nd provider block pointing at `http://unsloth:8889` (Anthropic Messages API) with 3 model aliases (Qwen3.8 + DeepSeek-V4-Pro + Kimi-K2.7-Code). Existing 6 channels (telegram/slack/discord/whatsapp/webchat/ms-teams) preserved.
- **OpenCode** (`opencode.json`): add a new `unsloth-studio` custom provider of `type: "openai-compatible"` pointing at `http://unsloth:8889/v1/` with 4 model aliases. The agent dispatch table gets a new fallback rule: if the M3 plan returns `429 rate_limit_exceeded`, the orchestrator retries against `unsloth-studio` with the same prompt.

### Marimo 10-way comparison notebook (NOT a Dagster asset)

New `notebooks/30_unsloth_vision_compare.py` (300 LOC, marimo reactive) that:

- Imports `MODEL_REGISTRY.filter(family="ocr_vision")` + `MODEL_REGISTRY.filter(family="text_llm")` (no hardcoded model strings)
- Renders a `mo.ui.multiselect` for 10 backends (6 Unsloth VLMs + 4 classical OCRs: Docling, dots-ocr, OlmOCR, PaddleOCR)
- Renders a `mo.ui.multiselect` for PDFs from `stedding/ingest_queue/` (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
- Reactive loop that routes every (backend, PDF) pair through `http://ocr-router:8090/v1/ocr` (the existing ocr-router stack handles the fanout)
- Side-by-side `mo.hstack` of response text + latency + tokens (VLMs) / regions (classical) + KL-divergence or CER/WER notes
- Tag filter by `ModelCapability`
- Export to `stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json`
- **Human-driven only** — no Dagster asset wiring, no sensor, no schedule (per Q3)

### finetune_irish.py update

- Pin `unsloth==2026.8.0` (stable PyPI) instead of the git ref
- Update default `base_model` to `unsloth/Qwen3.8-27B-GGUF` (the new flagship)
- New sibling `finetune_unsloth_local.py` for M4 Max 48 GB QLoRA r=8

### ccc guide + firecrawl_monitor

New `unsloth-integration` guide in `.cocoindex_code/guides.yml` pointing at the 8 canonical Unsloth pages. New `firecrawl_monitor` for the 5 integration doc URLs with 7-day interval + `changeTracking: markdown`.

## Impact

### Affected specs (4 deltas, 0 new specs)

- **MODIFIED `centralized-model-registry`** — 20 new entries across 7 families; new `ModelBackend.UNSLOTH` enum value; new `unsloth_id` resolution path.
- **MODIFIED `agent-platform-cluster`** — Hermes + OpenClaw + OpenCode each gain a 2nd provider (unsloth-serve). The 5 LiteLLM-routed M3 chokepoint aliases get a 429-retry-fallback to unsloth-studio.
- **MODIFIED `british-isles-education-pipeline`** — The 6 BIEP LC subjects gain a new notebook `30_unsloth_vision_compare.py` that compares 10 backends (6 Unsloth VLMs + 4 classical OCRs) per the 10-way comparison.
- **MODIFIED `infrastructure-stacks`** — 1 new GOLD_STANDARD stack (`unsloth-serve`), bringing the catalog from 94 to 95 stacks.

### Non-spec changes

- `opencode.json` — new `unsloth-studio` custom provider (4 models)
- `meaisinfhoghlaim/training/modal_finetune/finetune_irish.py` (modified — pin unsloth==2026.8.0)
- `meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py` (NEW — M4 Max QLoRA r=8)
- 1 new marimo notebook at `notebooks/30_unsloth_vision_compare.py` (10-way comparison: 6 VLMs + 4 classical OCRs)
- 2 new Bonneagar compose files: `bonneagar/stacks/unsloth-serve/compose.{arm1-oci,bunchloch}.yaml` + the 6 GOLD_STANDARD base files
- 1 new Komodo procedure at `bonneagar/komodo/procedures/unsloth-serve-deploy.toml`
- 2 Komodo resource-sync patches (arm1-oci.toml + bunchloch.toml — add unsloth-serve)
- 1 new Infisical secret: `infisical://dev-baile/unsloth/api-key` (single shared, not per-agent)
- 1 new ccc guide at `.cocoindex_code/guides.yml`

### Cross-host deployment

- **arm1-oci**: GPU-backed (`-ngl 99`), 12 GB, public via Pangolin (`unsloth-api.cianfhoghlaim.ie`). Production serving for hermes/openclaw/webchat.
- **bunchloch**: CPU/MPS (`-ngl 0`), 8 GB, `127.0.0.1:8889` only. Dev-mode + the marimo comparison notebook + the Studio UI.

### Marimo notebook scope (NOT a Dagster asset)

- Human-driven surface only; no `definitions.py` asset, no sensor, no schedule.
- Outputs flow into `stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json` for future BIEP v2 ingestion.

## Dependencies

`Blocked by: none` (the unsloth-serve stack is independent; the ModelRegistry + litellm + Hermes/OpenClaw/OpenCode + marimo changes are all downstream)

`Blocked by (soft): 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (already archived; the new entries inherit the existing `ModelRegistryEntry` dataclass)

`Affected repos: cianfhoghlaim` (single-repo; the `Bonneagar` IaC is a subdirectory of this repo per the v7 flattening)

## Cost

- **Compute:** 0 — Unsloth-serve runs on the existing `bunchloch` M4 Max 48 GB (the new flagship Qwen3.8-27B at UD-Q4_K_XL fits in ~16 GB resident + 6 GB KV cache). On `arm1-oci` the same model fits in ~12 GB with full GPU offload.
- **API tokens:** Saves up to ~80% of M3 plan spend during heavy agent sessions (the `unsloth start` fallback is free + offline).
- **Storage:** ~50 GB on the GGUF cache for 5 commonly-used quants (Qwen3.8-27B, Qwen3-VL-8B, DeepSeek-V4-Pro, Kimi-K2.7-Code, Muse Glimmer-30B) at UD-Q4_K_XL.
- **Infisical:** 1 new secret (`unsloth/api-key`); 0 new projects.
