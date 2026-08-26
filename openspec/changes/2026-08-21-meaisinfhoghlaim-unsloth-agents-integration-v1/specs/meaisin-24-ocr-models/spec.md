## MODIFIED Requirements

### Requirement: 24-model registry supports UNSLOTH_STUDIO as a 4th backend

The 24 OCR/VLM models in the v4 registry (`meaisinfhoghlaim/models/registry.py:VISION_MODELS`) SHALL now support 4 backends (was 3): LITELLM + LLAMASWAP + UNSLOTH_STUDIO + TRANSFORMERS. Unsloth Studio runs at `host.docker.internal:8888` and serves Unsloth GGUF models natively.

#### Scenario: 24-model registry has 4 backends

- **WHEN** the operator runs `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(set(m.backend.value for m in VISION_MODELS.values()))"`
- **THEN** the output contains `'unsloth_studio'` (alongside `'litellm'`, `'llama_swap'`, `'transformers'`)

#### Scenario: Unsloth-first fallback chain

- **GIVEN** a Unsloth GGUF model (e.g., `gemma-4-26B-A4B`)
- **WHEN** the OCR-Router invokes it
- **THEN** it tries UNSLOTH_STUDIO first
- **AND** on failure falls back to LLAMASWAP
- **AND** on failure falls back to TRANSFORMERS (or MLX on Apple Silicon)
- **AND** the fallback chain is logged to Langfuse

### Requirement: Per-model BAML Extract functions emit 5-rung provenance

The canonical per-model BAML `Extract*` function contract (per the existing spec) SHALL now emit the 5-rung provenance ladder (Document -> Location -> Extraction -> Evaluation -> Anchor) via Langfuse traces.

#### Scenario: Per-model BAML Extract emits 5-rung provenance

- **WHEN** the operator runs `python3 -c "from baml_client import b; print(b.ExtractQwen3VLPdf(file_path='/path/to/paper.pdf'))"`
- **THEN** the function returns a valid Pydantic type AND emits 5 Langfuse spans (one per rung) to the trace tree
