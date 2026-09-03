# Spec delta: `indexing-and-cognition`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
OpenCode agent + skill + MCP registry to include the new
`centralized-registry` skill.

## ADDED Requirements

### Requirement: INDEXING_AND_COGNITION MUST surface the centralized-registry skill

The system SHALL update `.agents/skills/INDEXING_AND_COGNITION.md`
to include the new `centralized-registry` skill in the §8 skill
registry surface. The skill is the canonical operator-facing guide
for the 4 centralized-registry artifacts (MODEL_REGISTRY +
schema.py + 00_control_panel + deployment-choice.yaml).

#### Scenario: centralized-registry skill appears in the priority skill table

- **GIVEN** the new skill file at `.agents/skills/centralized-registry/SKILL.md`
- **WHEN** the operator reads `INDEXING_AND_COGNITION.md` priority skills
- **THEN** the `centralized-registry` skill is in the priority skills list
- **AND** the skill description references the 4 canonical artifacts

#### Scenario: INDEXING_AND_COGNITION §8.5 documents the centralized-registry surface

- **GIVEN** the `centralized-registry` skill is the primary operator guide
- **WHEN** the operator reads `INDEXING_AND_COGNITION.md` §8.5
- **THEN** the section lists the 4 artifacts + the 4 new mise tasks (`lint:registry`, `models:list`, `notebook:control-panel`, `models:count`)
- **AND** the OpenCode agent counts are updated from 7/9 → 14/12
