## MODIFIED Requirements

### Requirement: spec-purpose-dual-search-architecture (MODIFIED)

The `openspec/specs/dual-search-architecture/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the dual-search-architecture topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: dual-search-architecture Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/dual-search-architecture/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
