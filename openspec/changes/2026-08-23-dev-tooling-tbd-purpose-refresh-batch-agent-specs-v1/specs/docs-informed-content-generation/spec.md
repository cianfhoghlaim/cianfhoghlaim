## MODIFIED Requirements

### Requirement: spec-purpose-docs-informed-content-generation (MODIFIED)

The `openspec/specs/docs-informed-content-generation/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the docs-informed-content-generation topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: docs-informed-content-generation Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/docs-informed-content-generation/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
