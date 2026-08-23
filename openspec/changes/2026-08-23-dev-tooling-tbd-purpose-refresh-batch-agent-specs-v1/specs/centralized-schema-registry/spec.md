## MODIFIED Requirements

### Requirement: spec-purpose-centralized-schema-registry (MODIFIED)

The `openspec/specs/centralized-schema-registry/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the centralized-schema-registry topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: centralized-schema-registry Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/centralized-schema-registry/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
