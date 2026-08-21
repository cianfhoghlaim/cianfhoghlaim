## MODIFIED Requirements

### Requirement: ModelRegistryEntry has the 7 canonical families

The system SHALL register model entries across these 7 families in `MODEL_REGISTRY`: `ocr_vision`, `text_llm`, `embedder`, `rerank`, `image_gen`, `voice`, `translation`. The system MUST resolve models via `MODEL_REGISTRY.filter(family=...)` or `model_for(family, role)`.

#### Scenario: 20 new unsloth-catalog entries

- **GIVEN** the unsloth-catalog-as-of-2026-08-15 (per Firecrawl MCP scrape of `https://unsloth.ai/docs/get-started/unsloth-model-catalog`)
- **WHEN** `meaisinfhoghlaim/models/model_registry.py` is updated with the 20 new entries (10 text_llm including Qwen3.8-27B + DeepSeek-V4-Pro/Flash + Kimi-K2.7-Code + Muse Glimmer + MiniMax-M2.5 + Magistral-Small + Nemotron-3.5-Lightning; 4 ocr_vision including Qwen3-VL-8B/32B Instruct + GLM-4.6V-Flash + DeepSeek-OCR-2; 2 image_gen including DiffusionGemma + Qwen-Image-2512; 2 embedder including Qwen3-Embedding-4B + EmbeddingGemma-300M; 2 voice including Orpheus-TTS-3B + Sesame-CSM-1B)
- **THEN** `MODEL_REGISTRY.filter(family="text_llm")` returns 14 entries (was 9)
- **AND** `MODEL_REGISTRY.filter(family="ocr_vision")` returns 26 entries (was 22)
- **AND** `MODEL_REGISTRY.filter(family="image_gen")` returns 7 entries (was 5)
- **AND** `MODEL_REGISTRY.filter(family="embedder")` returns 5 entries (was 3)
- **AND** `MODEL_REGISTRY.filter(family="voice")` returns 7 entries (was 5)
- **AND** `mise run lint:registry` exits 0 with no hardcoded model strings

### Requirement: ModelBackend enum has UNSLOTH

The `ModelBackend` enum SHALL include `UNSLOTH = "unsloth"` as a new backend value for models served via the Unsloth Studio OpenAI/Anthropic-compatible endpoint at `:8889`.

#### Scenario: New UNSLOTH backend is registered

- **WHEN** `meaisinfhoghlaim/models/registry.py:ModelBackend` is updated
- **THEN** `ModelBackend.UNSLOTH.value == "unsloth"`
- **AND** `MODEL_REGISTRY.filter(backend="unsloth")` returns exactly the 20 new entries
- **AND** `mise run cic:meaisin:litellm-regenerate` regenerates litellm/config.yaml with 20 new `local/unsloth/<key>` aliases
