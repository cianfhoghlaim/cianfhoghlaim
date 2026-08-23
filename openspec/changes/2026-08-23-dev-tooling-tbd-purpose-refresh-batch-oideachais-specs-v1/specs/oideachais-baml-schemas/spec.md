## MODIFIED Requirements

### Requirement: spec-purpose-oideachais-baml-schemas (MODIFIED)

The `openspec/specs/oideachais-baml-schemas/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-oideachais-specs-v1` change.

#### Scenario: oideachais-baml-schemas Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/oideachais-baml-schemas/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
