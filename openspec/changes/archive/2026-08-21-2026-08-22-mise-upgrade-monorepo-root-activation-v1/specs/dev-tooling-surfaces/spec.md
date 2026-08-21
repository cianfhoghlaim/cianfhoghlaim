# dev-tooling-surfaces — mise upgrade + monorepo_root activation (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical activation
of mise 2026.8+ monorepo mode (was declared but ignored in 2026.5.6).

## ADDED Requirements

### Requirement: mise-upgrade-and-monorepo-activation

The dev environment SHALL pin mise >= 2026.8 in `[tools]` so that:

1. The `[settings] monorepo_root = true` setting is recognized (not silently ignored)
2. The `[monorepo] config_roots = [...]` setting is processed
3. Root-level aliases for the devops/ml:agents tasks (that moved to subprojects in the previous refactor) resolve via monorepo path syntax
4. The new `core:mise:upgrade` task works

#### Scenario: mise is upgraded to 2026.8+

- **WHEN** the user runs `mise install`
- **THEN** mise SHALL be installed at version 2026.8.10 or later
- **AND** the `settings.monorepo_root` warning SHALL NOT appear

#### Scenario: monorepo_root is recognized

- **WHEN** `mise tasks --all` runs from the repo root
- **THEN** the output SHALL include subproject tasks (with `//` prefix per the monorepo path syntax)
- **AND** the output SHALL NOT include the `unknown field in settings: monorepo_root` warning

#### Scenario: root aliases resolve to subproject tasks

- **WHEN** `mise run devops:health` runs from the repo root
- **THEN** the command SHALL resolve to the subproject task (via the root alias)
- **AND** exit 0 (after the subproject task completes)

#### Scenario: subproject task works directly

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command SHALL invoke `bun run iac:health` from inside the bonneagar subproject
- **AND** exit 0

#### Scenario: core:mise:upgrade works

- **WHEN** `mise run core:mise:upgrade` runs
- **THEN** the command SHALL invoke `mise upgrade`
- **AND** upgrade mise to the latest version

## Cross-references

- https://mise.jdx.dev/tasks/monorepo.html — monorepo mode docs
- https://mise.jdx.dev/ — mise upstream docs
- `bonneagar/mise.toml` — the IaC subproject
- `agents/mise.toml` — the agent-fleet subproject
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
