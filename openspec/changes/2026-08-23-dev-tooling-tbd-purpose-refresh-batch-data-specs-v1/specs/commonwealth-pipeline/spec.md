## MODIFIED Requirements

### Requirement: spec-purpose-commonwealth-pipeline (MODIFIED)

The Purpose field of this spec MUST be a non-TBD statement that summarizes the spec's topic, scope, and key invariants. Per the 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 change.

#### Scenario: Commonwealth Purpose is non-TBD

- **WHEN** `grep "TBD" openspec/specs/commonwealth-pipeline/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
