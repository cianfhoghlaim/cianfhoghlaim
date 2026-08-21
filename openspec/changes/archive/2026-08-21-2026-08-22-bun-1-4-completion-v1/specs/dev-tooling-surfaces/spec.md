# dev-tooling-surfaces — bun 1.4 completion (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the bun 1.4 features
that were either incorrectly deferred (prune, audit fix) or missed
in the previous bun refactor (dedupe, format, parallel).

## ADDED Requirements

### Requirement: bun-1-4-completion-tasks

The dev environment SHALL provide 6 new bun-related tasks in the
`core` namespace + 1 new task in the `web` namespace, all reachable
via `mise run` and reflecting the canonical bun 1.4+ surface.

The bun 1.4 completion tasks SHALL cover at minimum:

1. `core:bun:prune` — `bun prune` (remove unused packages from node_modules)
2. `core:bun:audit:fix` — `bun audit fix` (auto-upgrade vulnerable packages)
3. `core:bun:audit:fix:dry-run` — dry-run variant of the above
4. `core:bun:dedupe` — `bun dedupe` (remove duplicate versions from bun.lock)
5. `core:bun:format` — `bunx prettier --write .` (the missing formatter)
6. `core:bun:parallel` — `bun run --parallel` (parallel script runner)
7. `web:test:parallel` — `bunx turbo run test --parallel` (parallel test runner)

#### Scenario: bun prune is the unused-deps gate

- **WHEN** `mise run core:bun:prune` runs
- **THEN** the command MUST invoke `bun prune`
- **AND** exit 0 with a list of removed packages
- **AND** exit 0 (no-op) if no packages to prune

#### Scenario: bun audit fix is the auto-remediation gate

- **WHEN** `mise run core:bun:audit:fix:dry-run` runs
- **THEN** the command MUST invoke `bun audit fix --dry-run`
- **AND** exit 0 if no fixes needed
- **AND** exit 0 (with a list of planned changes) if fixes are possible

#### Scenario: bun dedupe deduplicates the lockfile

- **WHEN** `mise run core:bun:dedupe` runs
- **THEN** the command MUST invoke `bun dedupe`
- **AND** exit 0 with the lockfile deduplicated

#### Scenario: bun format is the formatter

- **WHEN** `mise run core:bun:format` runs
- **THEN** the command MUST invoke `bunx prettier --write .`
- **AND** exit 0

#### Scenario: bun parallel is the parallel runner

- **WHEN** `mise run core:bun:parallel --bun-run="echo 1; echo 2"` runs
- **THEN** the command MUST invoke `bun run --parallel` with the rest of the args
- **AND** execute the scripts in parallel

#### Scenario: agent docs reference the Bun API surface

- **WHEN** `.opencode/agents/mise.md` is read
- **THEN** the "Direct references" section MUST mention at least 4 of the
  Bun 1.4+ API surface (Bun.cron, Bun.markdown, Bun.Image, Bun.serve)

## Cross-references

- `package.json` — `packageManager: "bun@1.4"` (set in previous refactor)
- https://bun.com/blog/bun-v1.4 — the bun 1.4 release post
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
