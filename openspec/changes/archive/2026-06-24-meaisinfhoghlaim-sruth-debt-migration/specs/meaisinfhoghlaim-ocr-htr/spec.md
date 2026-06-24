# Spec Delta: meaisinfhoghlaim-ocr-htr

## MODIFIED Requirements

### Requirement: 10-model 6-backend OCR registry

The system SHALL provide an OCR model registry at
`meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS` with
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
  `meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS`
- **WHEN** the registry is imported
- **THEN** the registry SHALL have 11 entries
- **AND** the openspec change `meaisinfhoghlaim-ocr-spec-clarify`
  SHALL be updated to bump the count to 11

## ADDED Requirements

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
  `meaisinfhoghlaim/ocr/model_registry.py:ModelBackend`
- **WHEN** the enum is imported
- **THEN** the enum SHALL have 7 entries
- **AND** the new `vllm` backend SHALL be available for the 10
  OCR models
