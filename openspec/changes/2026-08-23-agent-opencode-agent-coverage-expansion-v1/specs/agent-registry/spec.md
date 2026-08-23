## ADDED Requirements

### Requirement: opencode-agent-dispatch-matrix

`AGENTS.md` SHALL document the 15 agents under `.opencode/agents/*.md`
organized by tier (primary / functional subagent / domain subagent)
+ the dispatch rules for each tier. Per the
`2026-08-23-agent-opencode-agent-coverage-expansion-v1` change.

#### Scenario: AGENTS.md includes the 3-tier dispatch matrix

- **WHEN** `AGENTS.md` is read by a new agent
- **THEN** it MUST contain a section documenting all 15 agents
  organized by tier
- **AND** it MUST explain when to use `build` vs a functional subagent
  vs a domain subagent
- **AND** it MUST note that `research` is read-only

#### Scenario: lint:drift-docs still passes after the addition

- **WHEN** the dispatch matrix section is added to AGENTS.md
- **THEN** `mise run lint:drift-docs` MUST still exit 0 (no claim drift)
