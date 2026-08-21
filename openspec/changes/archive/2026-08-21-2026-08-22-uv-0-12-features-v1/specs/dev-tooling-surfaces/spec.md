# dev-tooling-surfaces — uv 0.12 features (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of the uv 0.12+ features: `uv lock --refresh`, `uv tree --format=json`,
and `uv format` (the new Rust-managed Python formatter).

## ADDED Requirements

### Requirement: uv-0-12-features-tasks

The dev environment SHALL provide 5 new uv-related tasks in the `core`
namespace, all reachable via `mise run` and reflecting the uv 0.12+
surface.

The uv 0.12 features tasks SHALL cover at minimum:

1. `core:uv:lock:refresh` — `uv lock --refresh` (re-resolve from scratch)
2. `core:uv:lock:upgrade` — `uv lock --upgrade` (upgrade all packages)
3. `core:uv:lock:upgrade-package` — `uv lock --upgrade-package <name>`
4. `core:uv:tree:json` — `uv tree --format=json` (uv 0.12+)
5. `core:uv:format` — `uv format` (Python formatter, uv 0.12+)

#### Scenario: uv lock refresh updates the lockfile

- **WHEN** `mise run core:uv:lock:refresh` runs
- **THEN** the command MUST invoke `uv lock --refresh`
- **AND** exit 0

#### Scenario: uv lock upgrade upgrades all packages

- **WHEN** `mise run core:uv:lock:upgrade` runs
- **THEN** the command MUST invoke `uv lock --upgrade`
- **AND** exit 0 (or warn if no upgrades)

#### Scenario: uv tree JSON is the programmatic tree

- **WHEN** `mise run core:uv:tree:json` runs
- **THEN** the command MUST invoke `uv tree --format=json`
- **AND** emit a JSON dependency tree on stdout

#### Scenario: uv format is the canonical formatter

- **WHEN** `mise run core:uv:format` runs
- **THEN** the command MUST invoke `uv format`
- **AND** format the Python codebase

## Cross-references

- https://docs.astral.sh/uv/ — uv upstream docs
- `pyproject.toml` — the uv workspace config
- `uv.lock` — the lockfile that `uv lock` operates on
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
