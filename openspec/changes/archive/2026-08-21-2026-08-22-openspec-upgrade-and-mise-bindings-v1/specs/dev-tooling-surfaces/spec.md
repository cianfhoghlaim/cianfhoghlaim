# dev-tooling-surfaces — openspec 1.10 upgrade + mise bindings (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of openspec 1.10.0 (the latest version) + a mise task that automates
the upgrade path.

## ADDED Requirements

### Requirement: openspec-1-10-upgrade

The dev environment SHALL expose a 1-command upgrade path for
openspec (currently installed globally via `bun add -g @fission-ai/openspec`).

#### Scenario: openspec upgrade task exists

- **WHEN** `mise run openspec:upgrade` runs
- **THEN** the command MUST print the install command
  (`bun add -g @fission-ai/openspec@latest`)
- **AND** exit 0 (the actual install is user-initiated)

#### Scenario: openspec is at 1.10+ after upgrade

- **WHEN** the user runs `bun add -g @fission-ai/openspec@1.10.0`
- **THEN** `openspec --version` MUST show `1.10.0` or later
- **AND** `openspec schemas` MUST list spec-driven + opsx + workspace-planning
- **AND** all existing pending + archived changes MUST still validate

#### Scenario: skill docs document 1.10 features

- **WHEN** `.agents/skills/openspec/SKILL.md` is read
- **THEN** the file MUST include a "New in 1.10" section
- **AND** document Stores Beta, /opsx:explore, /opsx:onboard
- **AND** document the upgrade task

## Cross-references

- https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md — 1.10 changelog
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/opsx.md — OPSX schema
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
