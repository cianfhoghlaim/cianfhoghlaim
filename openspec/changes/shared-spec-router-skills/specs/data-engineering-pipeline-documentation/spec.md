## ADDED Requirements

### Requirement: Data engineering pipeline documentation router skill

The data engineering pipeline documentation capability MUST be discoverable via a single router skill at `.agents/skills/data-engineering-pipeline-documentation/SKILL.md`. The router SHALL list the 4 canonical docs (STATUS.md, REFACTORING.md, the quadrant README, the per-area READMEs), the 4 status columns in STATUS.md, the 5-stage Celtic asset generation pipeline, and the 4 kinds of "what changed" notes.

#### Scenario: Agent finds the documentation router

- **WHEN** an agent searches for "STATUS.md", "REFACTORING.md", "BAML × dlt × Dagster matrix", or "pipeline status"
- **THEN** the loader matches `.agents/skills/data-engineering-pipeline-documentation/SKILL.md`
- **AND** the skill points at the canonical docs without duplicating their content
