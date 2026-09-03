# Spec delta: `indexing-and-cognition`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the new `OPENCODE_REGISTRY` consumed by the central
registry dashboard, replacing the partial 53-skill claim in
`INDEXING_AND_COGNITION.md`.

## ADDED Requirements

### Requirement: OPENCODE_REGISTRY consumed by the central registry dashboard

The system SHALL register the new `OPENCODE_REGISTRY` (derived from
`opencode.json`'s `agent` + `mcp` + `provider` blocks) in
`.agents/skills/INDEXING_AND_COGNITION.md` §8, replacing the partial
53-skill claim. The 14 OpenCode agents + 12 MCP servers + 2 providers
+ 1 canonical model registry SHALL be the authoritative inventory.

#### Scenario: INDEXING_AND_COGNITION.md §8 is updated

- **GIVEN** the central registry dashboard at
  `notebooks/00_control_panel.py` Tab 5 "Registry"
- **WHEN** the operator opens the notebook
- **THEN** Tab 5 displays the OPENCODE_REGISTRY inventory
  (14 agents + 12 MCPs + 2 providers + 70 models)
- **AND** the drift count from `mise run lint:registry` is shown

#### Scenario: Skill count drift is reconciled

- **GIVEN** the existing drift between the documented skill count
  (53 in `AGENTS.md`, 123 in `openspec/AGENTS.md`, 153 actual
  `SKILL.md` files)
- **WHEN** the operator opens the control panel Tab 5
- **THEN** the panel shows the actual `SKILL.md` count from
  filesystem walk (`os.walk(".agents/skills/")`)
- **AND** the documented count is reconciled to match