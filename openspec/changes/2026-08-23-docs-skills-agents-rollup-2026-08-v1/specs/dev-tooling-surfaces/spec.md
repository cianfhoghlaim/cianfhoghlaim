## ADDED Requirements

### Requirement: docs-count-claims-fresh

The `AGENTS.md` + `openspec/AGENTS.md` count claims SHALL be kept in
sync with ground truth. Per the
`2026-08-23-docs-skills-agents-rollup-2026-08-v1` change (Phase 5
final cleanup).

#### Scenario: AGENTS.md reflects the current stack count

- **WHEN** `AGENTS.md` is read
- **THEN** the stack count claim MUST match `ls -d bonneagar/stacks/*/ | wc -l`
- **AND** the skill count claim MUST match `find .agents/skills -maxdepth 2 -name SKILL.md | wc -l`

#### Scenario: openspec/AGENTS.md reflects the current openspec item count

- **WHEN** `openspec/AGENTS.md` is read
- **THEN** the item count claim MUST be within ±5 of the actual `openspec validate --all --strict` count