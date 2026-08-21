# dev-tooling-surfaces — mise monorepo mode + subproject split (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of mise monorepo mode (`monorepo_root = true` + `[monorepo] config_roots`)
and the first two subproject mise.toml files (`bonneagar/mise.toml`
and `agents/mise.toml`).

## ADDED Requirements

### Requirement: mise-monorepo-mode-and-subprojects

The monorepo SHALL enable `monorepo_root = true` + `[monorepo] config_roots`
to get first-class subproject task support, with at least 2 subprojects
owning their own `mise.toml`:

1. `bonneagar/` — IaC subproject (89 Docker stacks + Komodo + Pangolin + Locket + Infisical)
2. `agents/` — Agent-fleet subproject (12-agent fleet + 8 NCCA subjects + 3 educational agents)

#### Scenario: monorepo_root is enabled

- **WHEN** the root `mise.toml` is read
- **THEN** `[settings]` MUST contain `monorepo_root = true`
- **AND** `[monorepo] config_roots` MUST include `bonneagar` and `agents`

#### Scenario: subproject tasks inherit from root

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command MUST invoke `bun run --cwd bonneagar iac:health`
- **AND** the subproject MUST inherit tools + env from the root
- **AND** the subproject MUST inherit `[task_templates]` from the root

#### Scenario: subproject tasks are addressable from root

- **WHEN** `mise tasks --all` runs from the repo root
- **THEN** the output MUST include both root tasks AND subproject tasks
- **AND** subproject tasks MUST be prefixed with `//devops:` or `//ml:agents:` per the mise monorepo path syntax

#### Scenario: back-compat aliases preserve old names

- **WHEN** `mise run devops:health` runs from the repo root
- **THEN** the command MUST resolve to the same execution as the pre-monorepo version
- **AND** every migrated task MUST retain its old name as an alias for 1 release cycle

#### Scenario: subproject tasks can also live under their domain namespace

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command MUST invoke the bonneagar-specific task
- **AND** the command MUST be equivalent to `mise run //devops:health` from the repo root

## Cross-references

- https://mise.jdx.dev/tasks/monorepo.html — mise monorepo docs
- `bonneagar/AGENTS.md` — the IaC subproject
- `agents/AGENTS.md` — the agent-fleet subproject
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
