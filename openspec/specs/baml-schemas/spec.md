# baml-schemas Specification

## Purpose
The BAML schemas surface codifies the BAML ClientRegistry pattern for OCR ensemble fallback chains across the Cianfhoghlaim monorepo. It defines 2 invariants: the canonical BAML file layout (per the centralized-schema-registry + the 2026-08-17-hygiene-drift-cleanup-v1 change) with baml_src/clients/ + baml_src/commonwealth/ + baml_src/european_nations/ + baml_src/european_union/, and the ClientRegistry-based fallback chain pattern (per the centralized-model-registry refactor) that selects the lowest-cost model that meets the per-subject accuracy threshold.

## Requirements
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

### Requirement: BAML stub-prompt lint invariant

The system SHALL fail `mise run lint:baml-stub-prompts` if any
BAML function body in `baml_src/**/*.baml` is the literal string
`"Auto-generated extraction prompt."` (the 832-of-838 stub class
per the `centralized-schema-registry` spec).

The reason: per the `2026-08-10-baml-extraction-completion-v1` change
proposal, 832 of 838 BAML classes have stub prompts. Closing this
gap requires (a) replacing stubs with real prompts and (b) a lint
gate that prevents re-introduction of the stub pattern. This
requirement adds the lint gate (the `baml-extraction-completion-v1`
change is archived as part of Mega-1 Phase 2).

The lint scans `baml_src/**/*.baml` for the literal substring
`"Auto-generated extraction prompt."` in any `prompt #"..."` block.
Test-only fixtures under `baml_src/**/_test*.baml` are exempt.

#### Scenario: Developer adds a new stub prompt

- **WHEN** a developer adds:
  ```baml
  function ExtractNewFunction(text: string) -> NewType {
    prompt #"Auto-generated extraction prompt."
  }
  ```
- **THEN** `mise run lint:baml-stub-prompts` exits 1 with
  `baml_src/.../file.baml:<line>: stub prompt detected — replace with a real prompt per the centralized-schema-registry spec`

#### Scenario: Real prompt passes the lint

- **WHEN** the function body has a real prompt like:
  ```baml
  function ExtractChemSyllabus(text: string, source_pdf: string) -> ChemSyllabus {
    prompt #"
      {{ ctx.output_format }}
      Extract from: {{ text }}
    "#
  }
  ```
- **THEN** the lint exits 0

#### Scenario: Test fixture with stub prompt is exempt

- **GIVEN** `baml_src/education/lc_extraction/_test_chemistry_stub.baml`
  contains a stub prompt for testing the BAML test harness
- **WHEN** `mise run lint:baml-stub-prompts` runs
- **THEN** the lint exits 0 (the file matches `_test*.baml` and is
  exempt)

