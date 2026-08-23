## MODIFIED Requirements

### Requirement: spec-purpose-baml-quality-bulk-sweep (MODIFIED)

The `openspec/specs/baml-quality-bulk-sweep/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the baml-quality-bulk-sweep topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: baml-quality-bulk-sweep Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/baml-quality-bulk-sweep/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
