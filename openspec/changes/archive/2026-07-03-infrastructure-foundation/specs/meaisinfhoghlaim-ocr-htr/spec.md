## MODIFIED Requirements

### Requirement: 24-model 4-backend OCR/VLM registry (v4)

The system SHALL provide an OCR/VLM model registry at
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py:VISION_MODELS`
with **24 entries** (was 10 in the legacy OCR_MODELS + 6 in
VLM_MODELS). The 24 entries SHALL have:

- `unsloth_id: str | None` — preferred Unsloth GGUF or bnb-4bit HF ID
- `mlx_id: str | None` — Apple-Silicon MLX HF ID
- `upstream_id: str` — canonical upstream org HF ID
- `backend: ModelBackend` (one of `LITELLM`, `MLX`, `TRANSFORMERS`, `LLAMASWAP`)
- `capabilities: list[ModelCapability]` (subset of 9 values: `DENSE_OCR`, `GROUNDING`, `TABLES`, `LATEX`, `REASONING`, `MATH`, `MULTILINGUAL`, `GAELIC`, `DIAGRAM` — `DIAGRAM` added 2026-06-29)
- `unsloth_features: list[str]` (subset of `["dynamic_2_0_gguf", "mtp_speculative", "moe_12x", "imatrix", "fast_inference"]`)
- `role: Literal["tier1_heavy", "tier2_medium", "tier3_light", "specialist", "legacy"]`
- `m4_max_48gb_fit: bool` — True if the model fits in 48 GB unified memory
- `arm1_oci_required: bool` — True if the model only runs on arm1-oci

The 4 backends SHALL be: `litellm`, `mlx`, `transformers`, `llama-swap`
(NOT `openai`, `anthropic`, `ollama` — all cloud-API backends were
dropped in v4 per user request).

#### Scenario: The 25th model is added by a developer

- **GIVEN** a developer adds `pixtral-13b` to
  `cianfhoghlaim/meaisinfhoghlaim/models/registry.py:VISION_MODELS`
- **WHEN** the registry is imported + `dg list components` runs
- **THEN** the registry SHALL have 25 entries
- **AND** the `select_ocr_backend()` heuristic tree SHALL continue to
  return a valid `(model, reason)` pair for any PDF (fallthrough to
  `gemma-4-E2B` for unknown types)

#### Scenario: The default for M4 Max 48 GB is `gemma-4-26B-A4B`

- **GIVEN** `get_default_for_m4_max()` is called
- **WHEN** the function returns
- **THEN** the return value SHALL be `"gemma-4-26B-A4B"` (the 26.5B
  MoE / 4B active sweet-spot model for M4 Max 48 GB unified memory)

### Requirement: llama-swap serves 13 Unsloth GGUF entries

The system SHALL provide a `llama-swap` configuration at
`bonneagar/ocr/models/llama_swap_config.yaml` (symlinked from
`bonneagar/stacks/llama-swap/config.yaml`) serving **13 GGUF entries**
via the `ghcr.io/mostlygeek/llama-swap:v166` container on host port
`8080`. Each entry SHALL map an OpenAI-compatible model alias to a
`llama-server` command + args block.

The 13 entries SHALL be (11 with `backend = LLAMASWAP` in the v4
registry + 2 with `backend = MLX` but a Unsloth GGUF as fallback
per the registry's `get_optimal_for_m4_id()` priority unsloth >
mlx > upstream):

1. `gemma-4-E2B` (MLX-preferred; GGUF fallback)
2. `gemma-4-E4B`
3. `gemma-4-12B`
4. `gemma-4-26B-A4B` (M4 default)
5. `qwen3-vl-4b`
6. `qwen3-vl-8b` (workhorse)
7. `qwen3-vl-30b-a3b`
8. `qwen3.6-27b-mtp`
9. `internvl3-8b`
10. `glm-4.6v-flash` (MLX-preferred; GGUF fallback)
11. `paddleocr-vl-1.6`
12. `llama-3.2-vision-11b` (legacy)
13. `gemma-3-4b` (legacy)

The 6 v4 registry entries with `backend = TRANSFORMERS`
(deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b, molmo2-8b,
uccix-mistral-24b, uccix-llama-3.1-8b) are NOT served by llama-swap
and load via Python (see the next Requirement).

The 4 MLX-only entries (granite-docling-258M, dots-ocr,
deepseek-ocr-2, the MLX form of gemma-4-E2B) are served by `mlx-omni`
on port 10240 (NOT by llama-swap).

Each VLM entry SHALL include a `--mmproj` flag pointing to the matching
f16 mmproj file. Each entry SHALL use `-ngl 99` (all layers to GPU) and
`-c 32768` (32k context) by default.

#### Scenario: llama-swap serves 13 GGUF entries on :8080

- **WHEN** `docker compose -f bonneagar/stacks/llama-swap/compose.yaml up -d && sleep 5 && curl -fsS http://localhost:8080/v1/models | python -m json.tool`
- **THEN** the JSON response SHALL contain 13 model entries with `id` values matching the 13 keys above
- **AND** no entry SHALL be missing or duplicated

#### Scenario: The symlink resolves

- **WHEN** `file bonneagar/stacks/llama-swap/config.yaml` runs
- **THEN** the output SHALL NOT contain the phrase "broken symbolic link"
- **AND** the output SHALL be "Unicode text, UTF-8 text"

Each VLM entry SHALL include a `--mmproj` flag pointing to the matching
f16 mmproj file. Each entry SHALL use `-ngl 99` (all layers to GPU) and
`-c 32768` (32k context) by default.

#### Scenario: llama-swap serves 14 GGUF entries on :8080

- **WHEN** `docker compose -f bonneagar/stacks/llama-swap/compose.yaml up -d && sleep 5 && curl -fsS http://localhost:8080/v1/models | python -m json.tool`
- **THEN** the JSON response SHALL contain 14 model entries with `id` values matching the 14 keys above
- **AND** no entry SHALL be missing or duplicated

#### Scenario: The symlink resolves

- **WHEN** `file bonneagar/stacks/llama-swap/config.yaml` runs
- **THEN** the output SHALL NOT contain the phrase "broken symbolic link"
- **AND** the output SHALL be "Unicode text, UTF-8 text"

### Requirement: GGUF cache populated from v4 registry

The system SHALL provide a GGUF cache at `stedding/huggingface/gguf/`
with the 13 v4 GGUF entries. The cache SHALL be populated by:

```bash
mise run llama-swap:download-models   # downloads 13 Unsloth GGUFs
```

The script `scripts/download_unsloth_models.py` SHALL loop the v4
registry's `VISION_MODELS` dict, use `unsloth_id` as the HF repo, and
download with `--include '*q4_k_m*'` and `--include '*mmproj*'`
patterns. The default cache directory SHALL resolve to
`<repo_root>/stedding/huggingface/gguf/` (overridable via
`LLAMA_SWAP_CACHE_DIR` env var).

#### Scenario: A dry-run lists 13 entries without downloading

- **WHEN** `mise run llama-swap:download-models:dry-run`
- **THEN** the output SHALL print 13 model IDs (one per line) and exit 0
- **AND** no files SHALL be downloaded

#### Scenario: MLX-only models download to the MLX cache

- **WHEN** `mise run llama-swap:download-mlx`
- **THEN** the output SHALL print 4 model IDs (one per MLX-only entry
  in the v4 registry) and the cache SHALL be populated at
  `stedding/huggingface/mlx-community/`
- **AND** no files SHALL be downloaded to `stedding/huggingface/gguf/`
  (MLX-only entries are served by `mlx-omni`, not by llama-swap)

### Requirement: TRANSFORMERS-backend models load via Python

The `dagster-local` Docker image SHALL install 12 Python packages
in `Dockerfile.dagster` so the 6 v4 registry entries with
`backend = TRANSFORMERS` (deepseek-ocr-2, olmocr-2-7b-1025,
molmo2-4b, molmo2-8b, uccix-mistral-24b, uccix-llama-3.1-8b) are
loadable from Python:

- OCR: `surya-ocr`, `rapidocr`, `pytesseract`, `easyocr`
- VLM: `docling[mlx-vlm]`, `paddleocr-vl`
- Doc→MD: `marker-pdf`, `mineru`
- GGUF runtime: `llama-cpp-python`
- Memory: `graphiti-core[falkordb]`, `cognee-sdk`, `letta`

Plus `huggingface-hub` for model downloads.

#### Scenario: The dagster image imports all 12 packages

- **WHEN** `docker run --rm dagster-local:latest python -c "import surya, rapidocr, easyocr, docling, paddleocr_vl, marker_pdf, mineru, llama_cpp, graphiti_core, cognee, letta, huggingface_hub"`
- **THEN** the command SHALL exit 0 with no ImportError
