# cianfhoghlaim-baml-schemas

## ADDED Requirements

### Requirement: BAML ClientRegistry pattern for OCR ensemble fallback chain

The system SHALL use the BAML `ClientRegistry` pattern (per
`docs.boundaryml.com/guide/baml-advanced/llm-client-registry`)
for the BIEP v2 OCR ensemble, so each function declares its own
primary client + fallback chain rather than a single bare `client`
field.

The reason: per the `centralized-model-registry` spec, the 52
model entries in `MODEL_REGISTRY` cover 7 families. The current
OCR ensemble at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`
uses 4 independent `client<llm>` blocks (`BAML`, `Unstract`, `Qwen3VL`,
`Gemma4`); the BAML Path 1 should use a `ClientRegistry` like
`GptOpusFallback` so the chain GPT-4o → Claude Opus 4 is automatic.

#### Scenario: ExtractEn function declares a ClientRegistry

- **GIVEN** `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
  has `@function ExtractEn { client "ExtractEnPrimary" }`
- **WHEN** the primary client `ExtractEnPrimary` (minimax-m3 via
  LiteLLM) fails with a 429 rate-limit error
- **THEN** the BAML runtime MUST automatically retry with
  `ExtractEnFallback` (qwen3.7-plus via DashScope token plan) per
  the `ClientRegistry(name="extract_en", primary="ExtractEnPrimary", fallbacks=["ExtractEnFallback"])`
- **AND** the per-call `Collector` MUST record both attempts
  (the `collector.last.calls` list has 2 entries)

#### Scenario: All 6 LC subject extractors adopt ClientRegistry

- **WHEN** `mise run lint:baml:client-registry` runs
- **THEN** all 6 LC subject extractors (chemistry, mathematics,
  geography, english, gaeilge, computer_science) MUST declare
  their primary client + fallback chain via `ClientRegistry`
- **AND** the registry name MUST follow the pattern
  `<subject>_<language>_<extraction>_registry` (e.g.,
  `chemistry_en_extract_registry`, `gaeilge_ga_extract_registry`)