## MODIFIED Requirements

### Requirement: spec-purpose-drift-remediation (MODIFIED)

The `openspec/specs/drift-remediation/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the drift-remediation topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: drift-remediation Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/drift-remediation/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
