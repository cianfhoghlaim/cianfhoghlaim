## MODIFIED Requirements

### Requirement: spec-purpose-baml-schemas (MODIFIED)

The `openspec/specs/baml-schemas/spec.md` `## Purpose` section SHALL
be filled in with a non-TBD statement that summarizes the BAML
ClientRegistry OCR ensemble fallback chain pattern (per the
centralized-model-registry refactor). Per the
`2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1`
change.

#### Scenario: BAML schemas Purpose is non-TBD

- **WHEN** `grep "TBD" openspec/specs/baml-schemas/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
