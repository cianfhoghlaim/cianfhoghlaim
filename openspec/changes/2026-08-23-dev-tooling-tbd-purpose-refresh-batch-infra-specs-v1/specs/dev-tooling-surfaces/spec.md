## MODIFIED Requirements

### Requirement: spec-purpose-dev-tooling-surfaces (MODIFIED)

The `openspec/specs/dev-tooling-surfaces/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-infra-specs-v1` change.

#### Scenario: dev-tooling-surfaces Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/dev-tooling-surfaces/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
