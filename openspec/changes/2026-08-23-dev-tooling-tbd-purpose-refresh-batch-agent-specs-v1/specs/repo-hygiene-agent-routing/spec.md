## MODIFIED Requirements

### Requirement: spec-purpose-repo-hygiene-agent-routing (MODIFIED)

The `openspec/specs/repo-hygiene-agent-routing/spec.md` `## Purpose` section SHALL be filled in with a non-TBD statement that summarizes the repo-hygiene-agent-routing topic, scope, and key invariants. Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: repo-hygiene-agent-routing Purpose is non-TBD

- **WHEN** `grep "TBD - created by archiving" openspec/specs/repo-hygiene-agent-routing/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
