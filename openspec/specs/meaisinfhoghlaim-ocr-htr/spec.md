# Meaisínfhoghlaim OCR & HTR Capability

## Purpose

`meaisinfhoghlaim-ocr-htr` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py`
(24 OCR/VLM models across 4 backends) and the new LC5 + Gemini
pipelines at `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
and `cianfhoghlaim/dlt/filesystem/gemini_corpus_source.py`.

This spec is the v4 home (post the 2026-07-03-infrastructure-foundation
change). The previous 10-model/6-backend schema is superseded.

## Background

The v4 OCR + HTR (handwritten text recognition) stack for Celtic-
language + general-purpose documents. The **24 OCR/VLM models across 4
backends** are:

- **LITELLM** (1 entry: legacy uccix-llama2-13b) — proxied via
  `litellm.cianfhoghlaim.ie:4000`
- **MLX** (4 entries: granite-docling-258M, dots-ocr, deepseek-ocr-2,
  gemma-4-E2B form) — Apple Silicon MLX, served by
  `mlx-omni.cianfhoghlaim.ie:10240`
- **TRANSFORMERS** (6 entries: deepseek-ocr-2 TRANSFORMERS form,
  olmocr-2-7b-1025, molmo2-4b, molmo2-8b, uccix-mistral-24b,
  uccix-llama-3.1-8b) — loaded inline via Python in the
  `dagster-local` image
- **LLAMASWAP** (13 entries: the Unsloth GGUF family) — served by
  `llama-swap` on `ghcr.io/mostlygeek/llama-swap:v166` at
  `:8080`. Each entry has an `--alias`, `--mmproj` (for VLMs), and
  env-substituted `LLAMA_ARG_NGL=99` + `LLAMA_ARG_CTX_SIZE=32768`.

The 4 backends are exposed via `ModelBackend` (in
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py`):
- `litellm`, `mlx`, `transformers`, `llama-swap`

The 9 `ModelCapability` enum values are:
- `DENSE_OCR`, `GROUNDING`, `TABLES`, `LATEX`, `REASONING`, `MATH`,
  `MULTILINGUAL`, `GAELIC`, `DIAGRAM` (DIAGRAM added 2026-06-29)

## Requirements

### Requirement: 24-model 4-backend v4 registry

The system SHALL provide an OCR/VLM model registry at
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py:VISION_MODELS`
with **24 entries**. Each entry SHALL have the 4-backend schema
(LITELLM / MLX / TRANSFORMERS / LLAMASWAP) and the Unsloth-first
fallback chain (`unsloth_id` → `mlx_id` → `upstream_id`).

The canonical 24 registry keys are:
`gemma-4-E2B, gemma-4-E4B, gemma-4-12B, gemma-4-26B-A4B, glm-4.6v-flash,
qwen3-vl-4b, qwen3-vl-8b, qwen3-vl-30b-a3b, qwen3.6-27b-mtp,
internvl3-8b, deepseek-ocr-2, olmocr-2-7b-1025, granite-docling-258M,
uccix-mistral-24b, uccix-llama-3.1-8b, uccix-llama2-13b, dots-ocr,
paddleocr-vl-1.6, molmo2-4b, molmo2-8b, llama-3.2-vision-11b, gemma-3-4b`
(22 unique; `gemma-4-E2B` appears twice — once in MLX and once in
LLAMASWAP).

#### Scenario: The default for M4 Max 48 GB is `gemma-4-26B-A4B`

- **GIVEN** `get_default_for_m4_max()` is called
- **WHEN** the function returns
- **THEN** the return value SHALL be `"gemma-4-26B-A4B"`

#### Scenario: `select_ocr_backend()` routes PDFs by filename pattern

- **GIVEN** a PDF whose filename contains "marking" or "scheme"
- **WHEN** `select_ocr_backend(pdf_path)` is called
- **THEN** the returned model SHALL be `molmo2-8b` (diagram-pointing specialist)
- **AND** a PDF named like an SEC exam paper SHALL be routed to `qwen3-vl-8b`
- **AND** a PDF whose name contains a year 1900-1922 SHALL be routed to `glm-4.6v-flash`

### Requirement: llama-swap serves 13 Unsloth GGUF entries

The system SHALL provide a `llama-swap` configuration at
`bonneagar/ocr/models/llama_swap_config.yaml` (symlinked from
`bonneagar/stacks/llama-swap/config.yaml`) serving **13 GGUF entries**
via the `ghcr.io/mostlygeek/llama-swap:v166` container on host port
`8080`. Each entry SHALL map an OpenAI-compatible model alias to a
`llama-server` command + args block.

The 13 entries SHALL be (verified against the v4 registry's
`unsloth_id` field for each `backend ∈ {LLAMASWAP, MLX}` entry):

1. `gemma-4-E2B` (MLX-preferred; GGUF fallback)
2. `gemma-4-E4B`
3. `gemma-4-12B`
4. `gemma-4-26B-A4B`
5. `qwen3-vl-4b`
6. `qwen3-vl-8b`
7. `qwen3-vl-30b-a3b`
8. `qwen3.6-27b-mtp`
9. `internvl3-8b`
10. `glm-4.6v-flash`
11. `paddleocr-vl-1.6`
12. `llama-3.2-vision-11b` (legacy)
13. `gemma-3-4b` (legacy)

#### Scenario: llama-swap serves 13 GGUF entries on :8080

- **WHEN** `curl -fsS http://localhost:8080/v1/models`
- **THEN** the JSON response SHALL contain 13 model entries with `id` values matching the 13 keys above

### Requirement: 6 TRANSFORMERS-backend models loaded inline

The system SHALL load the 6 TRANSFORMERS-backend models in Python via
the `dagster-local` image (the 12 Python packages installed by
`bonneagar/stacks/dagster/Dockerfile.dagster`). The 6 entries are:
`deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b, molmo2-8b,
uccix-mistral-24b, uccix-llama-3.1-8b`.

#### Scenario: The dagster image imports all 12 Python packages

- **WHEN** `docker run --rm dagster-local:latest python -c "import surya, rapidocr, easyocr, docling, paddleocr_vl, marker_pdf, mineru, llama_cpp, graphiti_core, cognee, letta, huggingface_hub"`
- **THEN** the command SHALL exit 0 with no ImportError

### Requirement: LC5 + Gemini pipelines use the v4 registry

The Leaving Certificate 5-subject pipeline (per
`openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/`)
and the Gemini 6-corpus pipeline (per
`openspec/changes/2026-07-03-gemini-6-corpus-pipeline/`) SHALL route
all PDF ingestion through `select_ocr_backend()` for the LC5 corpus
and through `qwen3-vl-8b` for the Gemini corpus.

#### Scenario: LC5 syllabus PDFs route through `gemma-4-26B-A4B`

- **GIVEN** a chemistry syllabus PDF named `SCSEC09_Chemistry_syllabus_Eng.pdf`
- **WHEN** the LC5 pipeline ingests it
- **THEN** `leaving_cert_source._classify_pdf()` SHALL return
  `("gemma-4-26B-A4B", "syllabus", ...)`
- **AND** downstream BAML extraction SHALL use the chosen model via llama-swap

#### Scenario: gaeilge PDFs route through `glm-4.6v-flash`

- **GIVEN** a gaeilge PDF at the gaeilge/ root (no en/ subdir)
- **WHEN** the LC5 pipeline ingests it
- **THEN** `_classify_pdf()` SHALL return `("glm-4.6v-flash", "syllabus", ...)`
  (because `language == 'ga'`)

## Cross-references

- [`cianfhoghlaim/meaisinfhoghlaim/models/registry.py`](../../cianfhoghlaim/meaisinfhoghlaim/models/registry.py) (865 lines, source of truth)
- [`bonneagar/ocr/models/llama_swap_config.yaml`](../../bonneagar/ocr/models/llama_swap_config.yaml) (13 GGUF entries)
- [`bonneagar/stacks/dagster/Dockerfile.dagster`](../../bonneagar/stacks/dagster/Dockerfile.dagster) (12 Python packages)
- [`openspec/specs/agent-memory-systems/spec.md`](./agent-memory-systems/spec.md) (the 3 memory backends: Cognee + Graphiti + Letta)
- [`.agents/skills/meaisinfhoghlaim-agent-frameworks/`](../../.agents/skills/meaisinfhoghlaim-agent-frameworks/SKILL.md)
- [`.agents/skills/document-intelligence/`](../../.agents/skills/document-intelligence/SKILL.md)
- [`.agents/skills/data-engineer/`](../../.agents/skills/data-engineer/SKILL.md)
- [`openspec/specs/meaisinfhoghlaim-platform/spec.md`](meaisinfhoghlaim-platform/spec.md) (the quadrant overview)
- [`openspec/specs/oideachais-pipeline/spec.md`](../oideachais-pipeline/spec.md) (LC5 + Gemini assets)
- [`openspec/specs/oideachais-leabharlann/spec.md`](../oideachais-leabharlann/spec.md) (the upstream leabharlann pipeline)
