## ADDED Requirements

The `oideachais-baml-schemas` capability is consolidated from the old
`assessment-extraction`, `bilingual-content`, and
`author-archive-baml-extraction` specs. The full Requirements +
Scenarios are in the canonical spec at
`openspec/specs/oideachais-baml-schemas/spec.md`.

### Requirement: 9 BAML files

The system SHALL maintain 9 BAML files at `baml_src/`:
`aistear.baml`, `primary.baml`, `junior_cycle.baml`,
`senior_cycle.baml`, `tertiary.baml`, `curriculum_extraction.baml`,
`author_archive.baml`, `ui_components.baml`, `image_generation.baml`.

#### Scenario: BAML client compiles

- **WHEN** `baml-cli generate` runs
- **THEN** the `baml_client/` Python client is regenerated
- **AND** all 9 BAML files are included in the generated client

### Requirement: 3 BAML extraction clients

The system SHALL provide 3 BAML extraction clients in
`baml_src/clients.baml`: `ExtractEn` (English-only, BGE-large-en-v1.5
backbone), `ExtractEnStrong` (higher-accuracy English variant), and
`LocalVision` (vision model for OCR + UI extraction).

#### Scenario: ExtractEn client available

- **WHEN** `from baml_client import b` is imported
- **THEN** the `b.ExtractPrimaryFramework`, `b.ExtractJCSpec`,
  `b.ExtractSeniorCycleSubject`, `b.ExtractGeminiReport`,
  `b.ExtractUoGArtifact`, `b.ExtractZoteroMetadata`,
  `b.ExtractHandwrittenEquations`, `b.ExtractUIComponent`,
  `b.GenerateImage` functions are all available
