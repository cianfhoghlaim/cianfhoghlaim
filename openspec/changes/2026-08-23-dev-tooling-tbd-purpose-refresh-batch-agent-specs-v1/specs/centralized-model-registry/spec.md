## MODIFIED Requirements

### Requirement: spec-purpose-centralized-model-registry (MODIFIED)

The `openspec/specs/centralized-model-registry/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the centralized-model-registry topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: centralized-model-registry Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/centralized-model-registry/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
