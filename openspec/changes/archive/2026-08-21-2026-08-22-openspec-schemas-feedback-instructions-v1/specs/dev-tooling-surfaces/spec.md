# dev-tooling-surfaces — openspec new subcommands (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of 4 new openspec 1.4+ subcommands: `schemas`, `feedback`,
`instructions`, `templates`. These are the subcommands the upstream
new `/opsx:*` slash commands rely on.

## ADDED Requirements

### Requirement: openspec-new-subcommands-gates

The dev environment SHALL provide 5 openspec-related tasks in the
`openspec` namespace that surface the new 1.4+ subcommands:

1. `openspec:schemas` — list available workflow schemas (spec-driven, opsx, tdd)
2. `openspec:schemas:json` — same as `schemas` but JSON output
3. `openspec:feedback` — submit feedback to OpenSpec maintainers
4. `openspec:instructions` — emit enriched artifact templates
5. `openspec:templates` — show resolved template paths for a schema

#### Scenario: openspec schemas lists available schemas

- **WHEN** `mise run openspec:schemas` runs
- **THEN** the command MUST invoke `openspec schemas`
- **AND** exit 0 with a list of available workflow schemas
- **AND** each schema MUST include name, description, and artifacts

#### Scenario: openspec schemas JSON is programmatic

- **WHEN** `mise run openspec:schemas:json` runs
- **THEN** the command MUST invoke `openspec schemas --json`
- **AND** exit 0 with a JSON array on stdout

#### Scenario: openspec feedback is the feedback channel

- **WHEN** `mise run openspec:feedback --help` runs
- **THEN** the command MUST invoke `openspec feedback --help`
- **AND** show the usage for submitting feedback

#### Scenario: openspec instructions emits enriched templates

- **WHEN** `mise run openspec:instructions proposal` runs
- **THEN** the command MUST invoke `openspec instructions proposal`
- **AND** exit 0 with an enriched template for the proposal artifact

#### Scenario: openspec templates shows resolved paths

- **WHEN** `mise run openspec:templates` runs
- **THEN** the command MUST invoke `openspec templates`
- **AND** exit 0 with the resolved template paths for each artifact in the schema

#### Scenario: skill + agent docs reference the new subcommands

- **WHEN** `.agents/skills/openspec/SKILL.md` is read
- **THEN** the "Quick start" section MUST list all 5 new subcommands
- **AND** `.opencode/agents/proposal-author.md` MUST reference them in the agent prompt

## Cross-references

- `openspec/AGENTS.md` — the openspec routing table
- `.agents/skills/openspec/SKILL.md` — the openspec skill
- `.opencode/agents/proposal-author.md` — the proposal-author agent
- https://github.com/Fission-AI/OpenSpec — openspec upstream
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
