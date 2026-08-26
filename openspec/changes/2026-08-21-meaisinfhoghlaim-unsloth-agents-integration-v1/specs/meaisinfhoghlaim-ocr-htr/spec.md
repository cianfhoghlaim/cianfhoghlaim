## MODIFIED Requirements

### Requirement: Unsloth Studio is the primary backend for the 8 Unsloth GGUF models

The system SHALL include Unsloth Studio as a primary backend for the 8 Unsloth GGUF models in the meaisinfhoghlaim VISION_MODELS registry. Unsloth Studio runs directly on the bunchloch host (M4 Max) at 127.0.0.1:8888, accessible from Docker via http://host.docker.internal:8888/v1. The canonical fallback chain is **Unsloth Studio -> llama-swap -> mlx -> transformers** when Unsloth Studio is unavailable.

The 8 Unsloth GGUF models are:

- `gemma-3-4b-it` (Unsloth GGUF, served via llama-swap currently)
- `gemma-4-E2B-it` (Unsloth GGUF, MLX twin)
- `gemma-4-E4B-it` (Unsloth GGUF, llama-swap)
- `gemma-4-12B-it` (Unsloth GGUF, llama-swap)
- `gemma-4-26B-A4B-it` (Unsloth GGUF, llama-swap)
- `qwen3-vl-4b-instruct` (Unsloth GGUF, llama-swap)
- `qwen3-vl-8b-instruct` (Unsloth GGUF, llama-swap)
- `qwen3-vl-30b-a3b-instruct` (Unsloth GGUF, llama-swap)

#### Scenario: OCR-Router picks Unsloth Studio first

- **GIVEN** a PDF file path
- **WHEN** the OCR-Router agent is invoked
- **THEN** it calls `ocr_qwen3_vl_8b` (via Unsloth Studio at host.docker.internal:8888) FIRST
- **AND** if Unsloth Studio returns an error, it falls back to `ocr_gemma4_26b` (via llama-swap)
- **AND** the dispatch is logged to Langfuse with `backend=unsloth_studio` tag

#### Scenario: Unsloth Studio unreachable falls back to llama-swap

- **GIVEN** Unsloth Studio is not running (container stopped or host.docker.internal:8888 unreachable)
- **WHEN** the OCR-Router agent is invoked
- **THEN** it skips `ocr_qwen3_vl_8b` (after a 2-second timeout)
- **AND** falls back to `ocr_gemma4_26b` (via llama-swap)
- **AND** the dispatch is logged to Langfuse with `backend=llama_swap` tag

### Requirement: 4-path OCR ensemble uses Unsloth Studio as one of the paths

The system SHALL provide a 4-path OCR ensemble (Docling + dots-ocr + OlmOCR + PaddleOCR + the Unsloth Studio VLM as a 5th path) per the existing federated OCR module.

#### Scenario: 5-path ensemble produces best-vote output

- **GIVEN** a PDF file path
- **WHEN** the `ocr_ensemble_4path` tool is invoked
- **THEN** it calls all 5 paths in parallel
- **AND** votes per character position
- **AND** the output includes per-path CER + the final voted text
- **AND** the dispatch is logged to Langfuse with `tool=ocr_ensemble_4path` tag
