# dev-tool-surfaces — uv audit + uv check (delta)

## Purpose

This delta extends `dev-tool-surfaces` with the canonical usage
of the uv 0.11+ `uv audit` + `uv check` preview subcommands as
CI gates. The current dev-tool surface uses `uv sync` + `uv run`
but has no security audit or type-check gate.

## MODIFIED Requirements

### Requirement: mise-task-canonical-shape

The `mise.toml` task catalogue SHALL be organized by **domain** into
exactly 6 namespaces (core, openspec, devops, data, ml, web), plus
the modern mise features (task_templates, monorepo_root, etc.) and
the new tool-specific gates (uv audit, ccc grep, bun prune, etc.).

The `core:lint` aggregate gate SHALL include the 4 new tool-specific
audit/check gates so downstream CI catches regressions automatically.

#### Scenario: core:lint includes the uv audit + check gates

- **WHEN** `mise run core:lint` runs
- **THEN** the depends DAG MUST include: `lint:skills`, `lint:registry`,
  `core:typecheck`, `core:uv:audit:strict`, `core:uv:check`
- **AND** all 5 gates MUST pass before `core:lint` exits 0

## ADDED Requirements

### Requirement: uv-audit-and-check-gates

The dev environment SHALL provide 4 uv-audit-related gate tasks in
the `core` namespace, all opt-in via `mise run` and wired into the
aggregate `core:lint` gate where appropriate.

The uv audit gates SHALL cover at minimum:

1. `core:uv:audit` — the relaxed audit (informational; default uv audit)
2. `core:uv:audit:strict` — the CI gate (exits 1 on any known vuln)
3. `core:uv:check` — the `ty` type checker (uv 0.11.18+ preview)
4. `core:uv:audit-malware` — malware scan via `UV_MALWARE_CHECK=1`

#### Scenario: uv audit strict is the CI gate

- **WHEN** `mise run core:uv:audit:strict` runs
- **THEN** the command MUST invoke `uv audit --strict`
- **AND** exit 1 if `uv.lock` contains any known OSV vulnerability
- **AND** exit 0 if the lock is clean

#### Scenario: uv check runs ty

- **WHEN** `mise run core:uv:check` runs
- **THEN** the command MUST invoke `uv check`
- **AND** exit 1 if Astral's `ty` reports any type error
- **AND** exit 0 if the codebase is type-clean

#### Scenario: uv audit malware is opt-in

- **WHEN** `mise run core:uv:audit-malware` runs
- **THEN** the command MUST invoke `UV_MALWARE_CHECK=1 uv sync --dry-run`
- **AND** exit 1 if any package in the dependency graph is flagged by
  the malware database
- **AND** exit 0 if the graph is clean or the check is not available

## Cross-references

- `pyproject.toml` — the uv workspace config (uv 0.11.21)
- `uv.lock` — the lockfile that the audit gates scan
- https://docs.astral.sh/uv/commands/audit/ — `uv audit` upstream docs
- https://docs.astral.sh/uv/commands/check/ — `uv check` upstream docs
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
