# dev-tooling-surfaces — mise fmt + mise generate (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of the new mise subcommands: `mise fmt` (format mise.toml) and
`mise generate` (generate files for tools/services).

## ADDED Requirements

### Requirement: mise-fmt-and-generate-tasks

The dev environment SHALL provide 5 new mise-related tasks in the
`core` namespace, all reachable via `mise run` and reflecting the
new mise subcommands.

The mise fmt + generate tasks SHALL cover at minimum:

1. `core:mise:fmt` — `mise fmt` (auto-formats mise.toml)
2. `core:mise:fmt:check` — `mise fmt --check` (CI gate, exits 1 on diff)
3. `core:mise:fmt:all` — `mise fmt --all` (formats all subprojects)
4. `core:mise:generate:pre-commit` — generate a git pre-commit hook
5. `core:mise:generate:devcontainer` — generate a devcontainer config

#### Scenario: mise fmt formats mise.toml

- **WHEN** `mise run core:mise:fmt` runs
- **THEN** the command MUST invoke `mise fmt`
- **AND** sort keys + clean up whitespace in the mise.toml file
- **AND** exit 0

#### Scenario: mise fmt check is the CI gate

- **WHEN** `mise run core:mise:fmt:check` runs
- **THEN** the command MUST invoke `mise fmt --check`
- **AND** exit 0 if the file is formatted correctly
- **AND** exit 1 if the file needs formatting

#### Scenario: mise fmt all formats subprojects

- **WHEN** `mise run core:mise:fmt:all` runs
- **THEN** the command MUST invoke `mise fmt --all`
- **AND** format mise.toml in root + all subproject config_roots

#### Scenario: mise generate creates files

- **WHEN** `mise run core:mise:generate:pre-commit` runs
- **THEN** the command MUST invoke `mise generate git-pre-commit`
- **AND** print the path to the generated file

#### Scenario: mise generate devcontainer

- **WHEN** `mise run core:mise:generate:devcontainer` runs
- **THEN** the command MUST invoke `mise generate devcontainer`
- **AND** print the path to the generated devcontainer config

#### Scenario: skill docs document the new tasks

- **WHEN** `.agents/skills/mise/SKILL.md` is read
- **THEN** the file MUST include a "fmt + generate" section
- **AND** document the 5 new tasks

## Cross-references

- https://mise.jdx.dev/cli/fmt.html — `mise fmt` upstream docs
- https://mise.jdx.dev/cli/generate.html — `mise generate` upstream docs
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
