## ADDED Requirements

### Requirement: `local_vision_gemma4` generator

The system SHALL provide a `local_vision_gemma4` BAML generator in `cianfhoghlaim/baml/clients.baml` that routes through the llama-swap OpenAI-compatible endpoint with the `gemma-4-26B-A4B` model.

#### Scenario: side-by-side vision block exists

- **GIVEN** the new generator added in step 8.9 of `tasks.md`
- **WHEN** `grep -E "^generator local_vision_gemma4" cianfhoghlaim/baml/clients.baml` is run
- **THEN** the generator block matches the canonical v0.212+ shape: `provider "openai"`, `model "local/vision/gemma-4-26B-A4B"`, `retry_policy Exponential`, `timeout { total_ms 60000 }`, `options { base_url env.LITELLM_BASE_URL, api_key env.LITELLM_API_KEY }`
- **AND** the `baml-cli generate` codegen succeeds against `gemma-4-26B-A4B` schema references
- **AND** the side-by-side comparison with `qwen3-vl-8b` is wired via `local_vision_qwen3vl` (Phase C tutorial 3 — deferred to follow-up)

### Requirement: `local_vision_qwen3vl` generator

The system SHALL provide a `local_vision_qwen3vl` BAML generator in `cianfhoghlaim/baml/clients.baml` that routes through the llama-swap OpenAI-compatible endpoint with the `qwen3-vl-8b` model.

#### Scenario: side-by-side vision block exists

- **GIVEN** the new generator added in step 8.10 of `tasks.md`
- **WHEN** `grep -E "^generator local_vision_qwen3vl" cianfhoghlaim/baml/clients.baml` is run
- **THEN** the generator block matches the canonical v0.212+ shape: `provider "openai"`, `model "local/vision/qwen3-vl-8b"`, `retry_policy Exponential`, `timeout { total_ms 60000 }`, `options { base_url env.LITELLM_BASE_URL, api_key env.LITELLM_API_KEY }`
- **AND** the existing `local_vision_qwen` (which uses `qwen3-vl-8b` too) is preserved as the workhorse OCR client per the BIEP v1 canonical contract; the new `local_vision_qwen3vl` is a separable alias for the tutorial-3 side-by-side comparison
