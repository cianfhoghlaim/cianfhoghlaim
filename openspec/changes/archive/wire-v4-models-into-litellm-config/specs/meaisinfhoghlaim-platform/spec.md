# Spec Delta: meaisinfhoghlaim-platform

## MODIFIED Requirements

### Requirement: litellm/config/config.yaml uses the v4 OCR/VLM registry

The system SHALL maintain `cianfhoghlaim/stacks/litellm/config/config.yaml` as a generated file. The config MUST include:

- 14+ v4 `local/vision/<model_key>` entries (one per VISION_MODELS entry with a llama-swap or transformers backend)
- 9+ v4 aliases (`vision`, `ocr`, `diagram`, `gaelic`, `irish`, `default`, `math`, `extract`, `embedding-bge-m3`) — each alias MUST declare an explicit `fallback_chain`
- The master `router_settings.fallbacks` list MUST use v4 primary keys (not v3)

The config MUST NOT include any of the v3 model names: `qwen2.5-vl`, `gemma-3-vision`, `deepseek-ocr`, `uccix-13b` (without the `-2` suffix or `mistral` suffix respectively).

The config MUST be regenerated whenever the v4 `VISION_MODELS` registry changes, via `python scripts/generate_litellm_config.py`.

#### Scenario: A developer adds a new Gemma 4 size

- **GIVEN** a new Gemma 4 size variant is added to
  `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **WHEN** `python scripts/generate_litellm_config.py` is run
- **THEN** the regenerated config has a new `local/vision/gemma-4-<size>` entry
- **AND** the validation script (`python scripts/validate_litellm_config.py`) passes
- **AND** the HF Hub liveness check (`python scripts/verify_hf_hub_audit.py --strict`) passes

#### Scenario: The litellm config has a v3 model name

- **GIVEN** a developer accidentally adds a v3 model name (e.g. `qwen2.5-vl-7b`) to the config
- **WHEN** `python scripts/validate_litellm_config.py` is run as a pre-commit hook
- **THEN** the validation script reports the v3 model name as an error
- **AND** the commit is blocked (exit code 1)
