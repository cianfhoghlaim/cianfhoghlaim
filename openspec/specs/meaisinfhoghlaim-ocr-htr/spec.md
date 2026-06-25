# Meaisínfhoghlaim OCR & HTR Capability

## Purpose

`meaisinfhoghlaim-ocr-htr` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at `sruth/meaisinfhoghlaim/ocr/`
(10 OCR models across 6 backends) and `sruth/oideachais/ocr/` (the
application-layer OCR for the leabharlann handwritten_pages resource).
See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md`
for the project identity.

This spec was created by the `openspec-consolidation-and-readme-refresh`
change and supersedes the old `agent-frameworks` spec's "OCR
backends" section (which is now in `sruth/oideachais/ocr/`) plus the
sruth/meaisinfhoghlaim/ocr/ Python module.

## Background

The OCR + HTR (handwritten text recognition) stack for Celtic-language
documents. The 10 OCR models across 6 backends are:

- **Pylaia** — open-source HTR via CTC + Connectionist Temporal
  Classification (best for historical manuscripts)
- **TrOCR** — Microsoft's transformer-based OCR (best for printed
  English text)
- **PaddleOCR** — Baidu's multi-language OCR (best for CJK + Latin
  scripts)
- **Tesseract** — the Apache-licensed OCR (best for clean printed
  text)
- **dots.ocr** — the small multilingual OCR (best for low-resource
  languages)
- **VLM-based OCR** — vision-language model OCR (best for
  handwriting + Irish mathematical equations; uses the
  `sruth/meaisinfhoghlaim/pipelines/vlm_bridge.py` VLM adapter)

The 6 backends are exposed via `sruth/meaisinfhoghlaim/ocr/adapters.py` and
the model registry at `sruth/meaisinfhoghlaim/ocr/model_registry.py`. The
Irish HTR dataset is at
`sruth/meaisinfhoghlaim/ocr/irish_htr_dataset.py`.

The application-layer `sruth/oideachais/ocr/` (the `author_archive_ocr.py` and
`pylaia_comparison.py` modules) wraps these for the leabharlann
handwritten_pages resource and the leabharlann handwritten equations
pipeline.
## Requirements
### Requirement: 10-model 6-backend OCR registry

The system SHALL provide an OCR model registry at
`sruth/meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS` with
**10 models** (not 9). The 10 models are:

1. `olmocr-7b` (transformers, Apache 2.0)
2. `qwen2.5-vl-7b` (transformers + mlx, Apache 2.0)
3. `qwen2.5-vl-7b-mlx` (mlx, Apache 2.0)
4. `deepseek-ocr` (transformers, MIT)
5. `granite-docling` (transformers, Apache 2.0)
6. `gpt-4o` (openai, Proprietary)
7. `claude-3.5-sonnet` (anthropic, Proprietary)
8. `llama-3.2-vision-11b` (transformers + litellm, Llama community)
9. `uccix-13b` (transformers, CC-BY-NC-4.0)
10. `gemma-3-vision` (transformers, gemma-terms) — the 10th
    model added in this round

The 6 backends SHALL be: `litellm`, `mlx`, `transformers`,
`ollama`, `openai`, `anthropic` (NOT Pylaia, TrOCR, PaddleOCR,
Tesseract, dots.ocr, VLM, which are OCR engines, not model-serving
backends).

#### Scenario: A developer adds the 11th OCR model

- **GIVEN** a developer adds `pixtral-12b` to
  `sruth/meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS`
- **WHEN** the registry is imported
- **THEN** the registry SHALL have 11 entries
- **AND** the openspec change `meaisinfhoghlaim-ocr-spec-clarify`
  SHALL be updated to bump the count to 11

### Requirement: Irish HTR dataset

The system SHALL provide an Irish HTR dataset at
`sruth/meaisinfhoghlaim/ocr/irish_htr_dataset.py` for fine-tuning the Pylaia
HTR model on Irish manuscripts.

#### Scenario: Dataset loads

- **GIVEN** the Irish HTR dataset module
- **WHEN** the dataset is loaded
- **THEN** the dataset returns (image, label) pairs in batches
- **AND** the labels are Unicode-normalised (NFC) Irish text

### Requirement: VLM bridge for handwriting + math equations

The system SHALL provide a VLM bridge at
`sruth/meaisinfhoghlaim/pipelines/vlm_bridge.py` for handwriting + Irish
mathematical equation OCR.

#### Scenario: Handwriting OCR

- **GIVEN** a scanned page of handwritten Irish text
- **WHEN** the VLM bridge is invoked with the page image
- **THEN** the VLM returns the recognised text in Irish
- **AND** the response includes a confidence score

#### Scenario: Math equation OCR

- **GIVEN** a scanned page with Irish mathematical equations
- **WHEN** the VLM bridge is invoked
- **THEN** the VLM returns the equations in LaTeX

### Requirement: Line segmentation

The system SHALL provide line segmentation at
`sruth/meaisinfhoghlaim/ocr/line_segmentation.py` for splitting scanned
pages into individual text lines before OCR.

#### Scenario: Page splits into lines

- **GIVEN** a scanned page of text
- **WHEN** the line segmentation module is invoked
- **THEN** the module returns a list of (y_min, y_max, image) tuples
  for each text line

### Requirement: Application-layer OCR for leabharlann

The system SHALL provide the application-layer `sruth/oideachais/ocr/` wrapper
that the leabharlann handwritten_pages resource uses.

#### Scenario: leabharlann handwritten_pages OCR

- **GIVEN** a UoG artefact with handwritten mathematical equations
- **WHEN** the `sruth/oideachais/ocr/author_archive_ocr.py` wrapper is
  invoked
- **THEN** the wrapper calls the Pylaia HTR or VLM bridge
- **AND** the recognised text is indexed in the LanceDB
  `author_archive_equations` table

### Requirement: OCR evaluation

The system SHALL provide OCR evaluation at
`sruth/meaisinfhoghlaim/ocr/comparison_runner.py` and
`sruth/meaisinfhoghlaim/ocr/gaelic_metrics.py`.

#### Scenario: CER / WER computed

- **GIVEN** a recognised text + the ground truth
- **WHEN** the comparison runner is invoked
- **THEN** the runner returns the Character Error Rate (CER) and
  Word Error Rate (WER)
- **AND** the gaelic metrics module returns the diacritic-preservation
  rate + the Irish-specific normalisation accuracy

### Requirement: OCR backend taxonomy

The system SHALL document the 6 OCR backends as the canonical
taxonomy:

- `litellm` — The LiteLLM proxy at
  `litellm.cianfhoghlaim.ie:4000` (production default)
- `mlx` — Apple Silicon MLX inference (the `mlx-omni` server at
  port 10240) for fast local inference on the M4 MacBook
- `transformers` — Direct HuggingFace transformers (local dev +
  on-prem OCI)
- `ollama` — The Ollama server at `ollama.cianfhoghlaim.ie:11434`
  for local-only models
- `openai` — The OpenAI API at `api.openai.com` (the gpt-4o
  fallback)
- `anthropic` — The Anthropic API at `api.anthropic.com` (the
  claude-3.5-sonnet fallback)

The 6 backends are NOT a misnomer for the 6 OCR engines
(Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) which
live in the application layer.

#### Scenario: A developer adds a new backend

- **GIVEN** a developer adds `vllm` to
  `sruth/meaisinfhoghlaim/ocr/model_registry.py:ModelBackend`
- **WHEN** the enum is imported
- **THEN** the enum SHALL have 7 entries
- **AND** the new `vllm` backend SHALL be available for the 10
  OCR models

## Cross-references

- [`sruth/meaisinfhoghlaim/ocr/`](../../sruth/meaisinfhoghlaim/ocr/) (the 10 OCR models)
- [`sruth/oideachais/ocr/`](../../sruth/oideachais/ocr/) (the application-layer wrapper)
- [`.agents/skills/document-intelligence/SKILL.md`](../../.agents/skills/document-intelligence/SKILL.md)
- [`.agents/skills/data-engineer/SKILL.md`](../../.agents/skills/data-engineer/SKILL.md)
- [`openspec/specs/meaisinfhoghlaim-platform/spec.md`](meaisinfhoghlaim-platform/spec.md) (the quadrant overview)
- [`openspec/specs/oideachais-leabharlann/spec.md`](../oideachais-leabharlann/spec.md) (the upstream leabharlann pipeline)
