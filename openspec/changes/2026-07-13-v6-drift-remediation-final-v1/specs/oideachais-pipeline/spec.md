# Spec Delta: oideachais-pipeline

## MODIFIED Requirements

### Requirement: LC5-subject + Gemini 6-corpus pipelines

The system SHALL keep the `LC5-subject + Gemini 6-corpus pipelines` requirement inside the main `## Requirements` section of `openspec/specs/oideachais-pipeline/spec.md` so OpenSpec strict validation, listing, and archive workflows can see it.

The system SHALL provide two new pipelines under the `oideachais-pipeline` capability:

1. **LC5-subject pipeline**: chemistry, computer_science, gaeilge, geography, and mathematics DAGs with VLM/OCR, DuckLake, LanceDB, Cognee, Graphiti, and FalkorDB stages.
2. **Gemini 6-corpus pipeline**: law, medical, politics, culture, technology, and other corpora with the same pipeline stages.

#### Scenario: Requirement is parsed by strict validation

- **GIVEN** `openspec/specs/oideachais-pipeline/spec.md`
- **WHEN** `openspec validate oideachais-pipeline --strict` runs
- **THEN** the spec is valid
- **AND** the `LC5-subject + Gemini 6-corpus pipelines` requirement is inside the main `## Requirements` section rather than under a delta-style `## ADDED Requirements` section

#### Scenario: Both pipelines share the v4 OCR/VLM registry

- **GIVEN** both the LC5 and Gemini pipelines
- **WHEN** a PDF is ingested by either pipeline
- **THEN** `select_ocr_backend(pdf_path)` SHALL return a v4 registry model key
- **AND** it SHALL NOT use the legacy 10-model `OCR_MODELS` dictionary

### Requirement: All Python imports inside cianfhoghlaim use the canonical namespace

The system SHALL have zero actual code-import examples using `from oideachais.*` inside active OpenSpec specs. Actual Python import examples SHALL use the v4 package root `from cianfhoghlaim...`.

The spec MAY keep bare `oideachais.*` documentation shorthand for MotherDuck/DuckLake schemas, capability names, and logical quadrant references when the text is not a Python import statement.

#### Scenario: Actual import examples use cianfhoghlaim

- **GIVEN** an active spec includes a Python import example for an oideachais module
- **WHEN** the example is a code path rather than documentation shorthand
- **THEN** it uses `from cianfhoghlaim.<module> import <symbol>`
- **AND** `grep -rE "from oideachais\." openspec/specs/ --include='*.md'` returns 0 matches

#### Scenario: Documentation shorthand is preserved

- **GIVEN** a spec refers to the MotherDuck schema `oideachais.education.ie.leaving_cert`
- **WHEN** the bare `oideachais.*` drift check runs
- **THEN** the schema reference is preserved as documentation shorthand
- **AND** it is not treated as a Python import path
