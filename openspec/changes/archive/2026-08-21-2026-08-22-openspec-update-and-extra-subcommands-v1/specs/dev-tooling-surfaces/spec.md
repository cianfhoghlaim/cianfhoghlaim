# dev-tooling-surfaces — openspec update + extra subcommands (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of 7 more openspec subcommands that were missed in the previous
openspec refactor (which added 5 of 29 total subcommands).

## ADDED Requirements

### Requirement: openspec-extra-subcommands-tasks

The dev environment SHALL provide 7 new openspec-related tasks in
the `openspec` namespace, all reachable via `mise run` and reflecting
the canonical openspec 1.4+ subcommands we missed in the previous
refactor.

The 7 new subcommands SHALL cover:

1. `openspec:update` — `openspec update` (re-emit instruction files)
2. `openspec:change` — `openspec change` (interactive subcommand)
3. `openspec:spec` — `openspec spec` (interactive subcommand)
4. `openspec:config` — `openspec config` (global config viewer)
5. `openspec:workspace` — `openspec workspace` (subcommand)
6. `openspec:context-store` — `openspec context-store` (subcommand)
7. `openspec:initiative` — `openspec initiative` (subcommand)

#### Scenario: openspec update re-emits instruction files

- **WHEN** `mise run openspec:update` runs
- **THEN** the command MUST invoke `openspec update`
- **AND** exit 0 (or print help)

#### Scenario: openspec change is the interactive manager

- **WHEN** `mise run openspec:change --help` runs
- **THEN** the command MUST invoke `openspec change --help`
- **AND** print the usage for managing change proposals

#### Scenario: openspec spec is the interactive spec manager

- **WHEN** `mise run openspec:spec --help` runs
- **THEN** the command MUST invoke `openspec spec --help`
- **AND** print the usage for managing specs

#### Scenario: openspec config views global config

- **WHEN** `mise run openspec:config` runs
- **THEN** the command MUST invoke `openspec config`
- **AND** print the global openspec config

#### Scenario: openspec workspace + context-store + initiative

- **WHEN** `mise run openspec:workspace` or `openspec:context-store` or `openspec:initiative` runs
- **THEN** the command MUST invoke the corresponding openspec subcommand
- **AND** exit 0 (or print help)

## Cross-references

- `openspec --help` — the full subcommand list
- `openspec/specs/openspec-1-4-subcommands/SKILL.md` — (to be created in the docs roll-up)
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
