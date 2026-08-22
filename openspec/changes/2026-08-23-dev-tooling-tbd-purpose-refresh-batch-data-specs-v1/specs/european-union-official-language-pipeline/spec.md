## MODIFIED Requirements

### Requirement: spec-purpose-european-union-official-language-pipeline (MODIFIED)

The Purpose field of this spec MUST be a non-TBD statement that summarizes the spec's topic, scope, and key invariants. Per the 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 change.

#### Scenario: EU-official-languages Purpose is non-TBD

- **WHEN** `grep "TBD" openspec/specs/european-union-official-language-pipeline/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
