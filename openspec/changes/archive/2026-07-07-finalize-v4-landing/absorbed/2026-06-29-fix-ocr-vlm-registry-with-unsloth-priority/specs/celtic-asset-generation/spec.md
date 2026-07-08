# Spec Delta: celtic-asset-generation

## ADDED Requirements

### Requirement: Unsloth-first Celtic OCR stack

The system SHALL use the following Unsloth-backed models as the canonical Celtic-language OCR stack for asset generation:

- **Gemma 4 E2B** (`unsloth/gemma-4-E2B-it-GGUF`, 3 GB) — edge / mobile, supports 6 Celtic languages
- **Gemma 4 E4B** (`unsloth/gemma-4-E4B-it-GGUF`, 5 GB) — browser-side, supports 6 Celtic languages
- **Gemma 4 12B Unified** (`unsloth/gemma-4-12b-it-GGUF`, 7 GB) — `gemma4_unified` arch
- **Gemma 4 26B-A4B MoE** (`unsloth/gemma-4-26B-A4B-it-GGUF`, 14 GB) — MoE, 4B-active, the M4 Max default
- **GLM-4.6V Flash** (`unsloth/GLM-4.6V-Flash-GGUF`, 6 GB) — fast / low-cost 10.3B VLM
- **Qwen 3VL 8B** (`unsloth/Qwen3-VL-8B-Instruct-GGUF`, 5 GB) — 119-language support (Irish explicit)
- **Qwen 3VL 30B-A3B MoE** (`unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF`, 18 GB) — Modal A100 burst
- **UCCIX-Mistral-24B** (`ReliableAI/UCCIX-Mistral-24B`, 24.1B, Nov 2025) — modern Irish-language path
- **Dots-OCR** (`mlx-community/dots.ocr-4bit`, 3.0B) — layout specialist for Celtic typography
- **Granite-Docling 258M** (`ibm-granite/granite-docling-258M-mlx`) — tiny doc-structure specialist

The system MUST NOT use the deprecated `ReliableAI/UCCIX-Llama2-13B-Instruct` (Llama 2, gated, Sep 2024) for new work.

#### Scenario: A Celtic-language asset is generated

- **GIVEN** a Welsh (`cy`) or Irish (`ga`) document needs OCR
- **WHEN** the Celtic asset generator dispatches an OCR call
- **THEN** it MUST prefer an Unsloth-backed model (per the 3-tier ladder in `meaisinfhoghlaim-ocr-htr`)
- **AND** it MUST NOT use a deprecated model (e.g. `ReliableAI/UCCIX-Llama2-13B-Instruct` on Llama 2)
- **AND** for layout-heavy Celtic typography, it MUST prefer `dots-ocr` or `granite-docling-258M`
