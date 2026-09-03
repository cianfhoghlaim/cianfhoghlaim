# Change: 2026-07-03-infrastructure-foundation

## Why

The Cianfhoghlaim platform's v4 OCR/VLM stack has 3 blockers that
prevent the upcoming Leaving Cert 5-subject pipeline (Change B) and
the Gemini 6-corpus pipeline (Change C) from running end-to-end:

1. **Broken llama-swap symlink.** The symlink at
   `bonneagar/stacks/llama-swap/config.yaml` (line 25 of the README)
   resolves to `../../ocr/models/llama_swap_config.yaml` — but neither
   the `bonneagar/ocr/` directory nor `llama_swap_config.yaml` exists.
   The container starts but has no model aliases defined.

2. **Empty GGUF cache.** The 3 mount points referenced by
   `bonneagar/stacks/llama-swap/compose.yaml` (lines 19-21 —
   `stedding/huggingface/gguf`, `stedding/huggingface/unsloth`,
   `stedding/huggingface/mlx-community`) do not exist. The HF Hub cache
   at `stedding/huggingface/` only has `hub/`, `stored_tokens/`,
   `token/`, `xet/` subdirs from previous one-off downloads.

3. **No local Python OCR/VLM/memory packages.** The `dagster-local`
   image (per `bonneagar/stacks/dagster/Dockerfile.dagster`, Change 7
   of 2026-07-02) installs dagster + baml-py + duckdb + lancedb +
   pyarrow + 9 others, but NO `surya-ocr`, `rapidocr`, `pytesseract`,
   `easyocr`, `docling[mlx-vlm]`, `paddleocr-vl`, `marker-pdf`,
   `mineru`, `llama-cpp-python`, `graphiti-core[falkordb]`,
   `cognee-sdk`, `letta`. The TRANSFORMERS-backend models in the v4
   OCR/VLM registry (deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b,
   molmo2-8b, uccix-mistral-24b, uccix-llama-3.1-8b — 6 of the 24
   entries) cannot run without these.

Per the user direction "we should be using the typical public
images/packages" — and to enable the 5 LC subjects + 6 Gemini corpora
pipelines + 25 new dev notebooks.

## What changes

This omnibus bundles 4 classes of changes (all ops-side; no
cianfhoghlaim code logic changes):

### 1 — llama-swap config + GGUF cache (3 files + 3 dirs created)

| File | Action |
|:--|:--|
| `bonneagar/ocr/models/llama_swap_config.yaml` | **CREATE** — 13 GGUF entries from v4 registry's `VISION_MODELS` dict (gemma-4-E2B, gemma-4-E4B, gemma-4-12B, gemma-4-26B-A4B, qwen3-vl-4b/8b/30b-a3b, qwen3.6-27b-mtp, internvl3-8b, glm-4.6v-flash, paddleocr-vl-1.6, llama-3.2-vision-11b, gemma-3-4b). Each entry uses the llama-swap v166 schema (cmd + args + env-substituted LLAMA_ARG_*). |
| `stedding/huggingface/gguf/README.md` | **CREATE** — documents the cache directory + the `mise run llama-swap:download-models` invocation |
| `stedding/huggingface/unsloth/README.md` | **CREATE** — Unsloth raw HF checkpoints for back-compat |
| `stedding/huggingface/mlx-community/README.md` | **CREATE** — mlx-community MLX checkpoints for `mlx-omni` |
| 3 directories: `gguf/`, `unsloth/`, `mlx-community/` | **CREATE** with `.gitkeep` |

The symlink at `bonneagar/stacks/llama-swap/config.yaml` already exists;
no symlink change needed. After this change, `file
bonneagar/stacks/llama-swap/config.yaml` returns "Unicode text, UTF-8
text" (not "broken symbolic link").

### 2 — Model download scripts (1 created + 1 fixed)

| File | Action |
|:--|:--|
| `scripts/download_mlx_models.py` | **CREATE** — loops the v4 registry's `mlx_id` field; default cache dir is `stedding/huggingface/mlx-community/` (overridable via `MLX_COMMUNITY_CACHE_DIR` env var) |
| `scripts/download_unsloth_models.py` | **EDIT** — change `DEFAULT_CACHE_DIR` from `/models/unsloth` to `<repo_root>/stedding/huggingface/gguf` (the host-path mount target) |

### 3 — dagster image extension + pyproject (2 files edited)

| File | Action |
|:--|:--|
| `bonneagar/stacks/dagster/Dockerfile.dagster` | **EDIT** — add 12 Python packages to the existing `RUN uv pip install --system` block (9 OCR/VLM/doc→md + 3 memory); add 5 system apt packages to both builder + runtime stages (`tesseract-ocr`, `libtesseract-dev`, `poppler-utils`, `libgl1`, `libglib2.0-0`); add `huggingface-hub` to the existing block |
| `cianfhoghlaim/pyproject.toml` | **EDIT** — extend the `memory` extra (graphiti-core[falkordb] + cognee-sdk + letta); add a new `ocr-vision-full` extra (9 packages); add a `dev-with-vision` composite extra; update the `all` union |

### 4 — mise tasks + openspec changes (3 file edits + 5 files created)

| File | Action |
|:--|:--|
| `mise.toml` | **EDIT** — fix 2 `llama-swap:up`/`down` compose paths from `cianfhoghlaim/stacks/...` to `bonneagar/stacks/...`; update `llama-swap:download-models` description; add 2 new tasks: `llama-swap:download-mlx` and `llama-swap:download-models:dry-run` |
| `openspec/changes/2026-07-03-infrastructure-foundation/proposal.md` | **CREATE** (this file) |
| `openspec/changes/2026-07-03-infrastructure-foundation/tasks.md` | **CREATE** (3 phases: 1. file authoring, 2. validate, 3. llms-serve) |
| `openspec/changes/2026-07-03-infrastructure-foundation/specs/meaisinfhoghlaim-ocr-htr/spec.md` | **CREATE delta** — `## MODIFIED Requirements` for the 24-model/4-backend schema |
| `openspec/changes/2026-07-03-infrastructure-foundation/specs/dagster-5-layer-component-architecture/spec.md` | **CREATE delta** — `## ADDED Requirements` for the dagster-image OCR/VLM/memory deps |

## Impact

- **Affected specs:** `meaisinfhoghlaim-ocr-htr`, `dagster-5-layer-component-architecture` (2 spec deltas)
- **Affected code:** 1 Dockerfile.dagster edit + 1 pyproject.toml edit + 1 download_unsloth_models.py fix + 1 mise.toml edit + 1 download_mlx_models.py create + 1 llama_swap_config.yaml create + 3 README.md creates + 3 dir creates
- **Affected hosts:** `bunchloch` only
- **Risk:** low — all changes are additive; existing llama-swap container will need `down && up` to pick up the new config
- **Audit gates:** `openspec validate --strict` + `bun run validate-stacks` (no stack-image changes; should still pass) + `mise run lint:skills`

## Non-goals

- **Not building or pushing the `dagster-local` image.** The image
  change lands in `Dockerfile.dagster`; the actual `docker build` is
  deferred until Wave 3 (InvokeAI + Convex + RisingWave) or until the
  next stack-update cycle. The 11 new Python packages will be
  auto-installed on the next `up -d`.
- **Not deleting the `graphiti/` stack.** It's broken (no Dockerfile)
  but it's tracked in Session 7's HEALTH_REPORT as a known issue.
  The `graphiti-core[falkordb]` Python package covers the use case for
  dev; the Compose stack deletion is deferred to Change D (spec
  cleanup) or a follow-up.
- **Not changing the v4 registry file.** `VISION_MODELS` is already
  correct (24 entries, Unsloth-first); this change just gives those
  entries an actual runtime.

## Open follow-up issues

| Issue | Tracking |
|:--|:--|
| `graphiti/` Docker Compose stack deletion | `2026-07-XX-delete-graphiti-stack` |
| `dagster-local` image build + push to local registry | `2026-07-XX-build-dagster-local-image` |
| Wave 3 deploy (InvokeAI + Convex + RisingWave) | `2026-07-03-wave-3-ui-streams-deploy` |
| Wire marimo notebooks to live data (5 LC + 7 law) | `2026-07-XX-wire-marimo-to-live-data` |
