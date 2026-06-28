# Spec Delta — meaisinfhoghlaim-platform

## ADDED Requirements

### Requirement: OCR Model Registry Location (v4)

The system SHALL expose the OCR model registry at `cianfhoghlaim/ocr/models/registry.py`. The registry SHALL list 11 vision models (Gemma-4×4 + Qwen3.6×4 + GLM-4.6V-Flash) and 3 image generation models (Qwen-Image-2512 + Z-Image-Turbo + FLUX.2-klein-9B). The legacy 9×6 model registry at `sruth/meaisinfhoghlaim/ocr/model_registry.py` is REPLACED (gpt_4o, claude_3_5_sonnet, llama_3_2_vision, uccix_13b are removed; classical OCR stacks stay separate as Docker compose).

#### Scenario: Vision model dispatch

- **WHEN** Dagster materialises an Ireland Leaving Cert exam paper asset
- **THEN** the OCR dispatch picks a vision model from `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **AND** the model runs on `litellm` (gateway), `llama-swap` (GGUF), or `mlx-omni` (MLX) backend per `cianfhoghlaim/ocr/backends/`

### Requirement: OCR Evaluation Harness (v4 NEW)

The system SHALL expose an OCR evaluation harness at `cianfhoghlaim/ocr/evaluation/compare.py` that compares vision models (Gemma-4 + Qwen3.6 + GLM-4.6V) against classical OCR Docker stacks (dots-ocr + docling-serve + olmocr + paddleocr) on the same documents.

#### Scenario: CER/WER comparison

- **WHEN** a developer runs `python -m cianfhoghlaim.ocr.evaluation.compare --corpus ireland_syllabus --backends vision,classical`
- **THEN** the harness reports CER, WER, fada-consistency, tironian-detection, and punctum-delens metrics per model/backend pair
- **AND** writes the report to `motherduck://oideachais.ocr.evaluation.results`