# Spec Delta — cianfhoghlaim-baml-schemas

This delta adds one new requirement to the existing `cianfhoghlaim-baml-schemas` capability. Existing requirements are preserved unchanged.

## ADDED Requirements

### Requirement: Active single minimax-m3 text generator

The `cianfhoghlaim-baml-schemas` capability SHALL define a single active text-extraction generator in `baml/clients.baml`: `generator default`, routed to the `minimax-m3` model through the OpenAI-compatible coding-plan API using `MINIMAX_BASE_URL` and `MINIMAX_API_KEY`.

The historical 8-generator layout (`default`, `local_vision_qwen`, `local_vision_glm`, `local_vision_moondream`, `gemini_2_flash`, `gemini_1_5_pro`, `gemini_pro`, `gemini_2_5_flash`) SHALL be preserved as a comment block for future reactivation when provider credentials become available. The two local vision generators `local_vision_gemma4` and `local_vision_qwen3vl` SHALL remain active.

#### Scenario: only supported active generators remain

- **GIVEN** the 2026-07-13 minimax cleanup has landed
- **WHEN** active generator declarations are enumerated from `baml/clients.baml`
- **THEN** the active generator names are exactly `default`, `local_vision_gemma4`, and `local_vision_qwen3vl`
- **AND** `generator default` includes `provider "openai-generic"`, `model "minimax-m3"`, `base_url env.MINIMAX_BASE_URL`, and `api_key env.MINIMAX_API_KEY`
- **AND** the historical 8-generator setup remains available only as line comments

#### Scenario: Minimax-M3 environment placeholders exist

- **GIVEN** a developer is configuring the BAML runtime locally
- **WHEN** they inspect `.env.example`
- **THEN** it documents `MINIMAX_BASE_URL` and `MINIMAX_API_KEY` placeholders for the M3 coding-plan API path
