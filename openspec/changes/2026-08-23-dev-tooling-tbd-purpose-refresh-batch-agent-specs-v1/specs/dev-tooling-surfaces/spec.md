## MODIFIED Requirements

### Requirement: spec-purpose-agent-specs-batch (MODIFIED)

The 10 agent specs listed below MUST have non-TBD Purpose sections.
Per the `2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1` change.

#### Scenario: all 10 agent specs have non-TBD Purpose

- **WHEN** `grep "TBD - created by archiving" openspec/specs/<X>/spec.md` runs for each of the 10 agent specs
- **THEN** it MUST NOT return any match in the `## Purpose` section
- **AND** the Purpose MUST be 2-3 sentences following the canonical template
