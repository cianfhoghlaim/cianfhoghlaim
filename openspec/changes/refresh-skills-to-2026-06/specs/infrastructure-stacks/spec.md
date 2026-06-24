## ADDED Requirements

### Requirement: Skills are refreshed to the current package state

Every KCG-authoritative skill that documents a third-party package (CocoIndex, Dagster, Cognee, MotherDuck, Langfuse, etc.) MUST have a "2026-06 update" or equivalent date-stamped section that captures the latest package features. The section SHALL be appended at the end of the skill (after the "Pair this skill with" cross-references) and SHALL include a date stamp so agents can see the freshness of the content.

#### Scenario: Agent sees the 2026-06 feature set

- **WHEN** an agent reads a skill that documents a package with a major release after the skill was last updated
- **THEN** the skill contains a "## 2026-06 update" (or equivalent) section
- **AND** that section covers the major features released since the original skill was written

#### Scenario: Refresh is a single openspec change

- **WHEN** a batch of skills needs a 2026-06 update
- **THEN** the batch is captured in one openspec change (the `refresh-skills-to-2026-06` change)
- **AND** the change is archived after the commit
