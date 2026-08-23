## MODIFIED Requirements

### Requirement: spec-purpose-learn-to-earn-token-credential (MODIFIED)

The `openspec/specs/learn-to-earn-token-credential/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-infra-specs-v1` change.

#### Scenario: learn-to-earn-token-credential Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/learn-to-earn-token-credential/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
