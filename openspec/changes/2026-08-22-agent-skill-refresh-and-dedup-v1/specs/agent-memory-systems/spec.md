## ADDED Requirements

### Requirement: skill-deprecation-cleanup

DEPRECATED skill files in `.agents/skills/` MUST be redirect-only
stubs (≤ 10 lines, frontmatter + 4-line body pointing to the
canonical replacement). DEPRECATED skills MUST NOT contain stale
content from the previous library version.

#### Scenario: DEPRECATED skill file is a redirect-only stub

- **WHEN** a skill file in `.agents/skills/*/SKILL.md` is marked
  DEPRECATED in its frontmatter description
- **THEN** the file MUST be ≤ 10 lines (frontmatter + 4-line body)
- **AND** the body MUST contain a `Use the canonical replacement:`
  line pointing to the canonical skill

#### Scenario: lint-skill:deprecated-cleanup fails on stale DEPRECATED files

- **WHEN** `mise run lint-skill:deprecated-cleanup` runs
- **AND** any DEPRECATED skill file is > 50 lines
- **THEN** the command MUST exit 1
- **AND** the output MUST list each offending file with its line count

#### Scenario: canonical skills unchanged after redirect

- **WHEN** a DEPRECATED skill is replaced with a redirect stub
- **THEN** the canonical replacement skill (`graphiti`, `dlt`,
  `secrets-management`, etc.) MUST be unchanged
- **AND** `mise run lint:skills` MUST still exit 0
