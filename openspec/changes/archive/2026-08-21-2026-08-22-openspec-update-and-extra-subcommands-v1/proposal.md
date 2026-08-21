# 2026-08-22 — openspec update + the missing 7 subcommands

## Why

The previous refactor (`2026-08-22-openspec-schemas-feedback-instructions-v1`)
added 5 new openspec subcommands (schemas, feedback, instructions,
templates, schemas:json). But we missed 7 more subcommands that are
useful in our workflow.

This change adopts the remaining 7 subcommands to round out our
openspec coverage.

## What changes

1. **`mise.toml`** — add 7 new tasks in the `openspec` namespace:

   - `openspec:update` (alias `openspec:refresh`) — `openspec update` (re-emit instruction files)
   - `openspec:change` (alias `openspec:change:cmd`) — `openspec change` (the interactive subcommand)
   - `openspec:spec` (alias `openspec:spec:cmd`) — `openspec spec` (the interactive subcommand)
   - `openspec:config` (alias `openspec:cfg`) — `openspec config` (global config viewer)
   - `openspec:workspace` (alias `openspec:ws`) — `openspec workspace` (subcommand)
   - `openspec:context-store` (alias `openspec:ctx`) — `openspec context-store` (subcommand)
   - `openspec:initiative` (alias `openspec:init`) — `openspec initiative` (subcommand)

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-22-openspec-schemas-feedback-instructions-v1` (extends the openspec namespace)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 7 new tasks exit 0 (or print help)
2. `openspec validate --all --strict` exits 0

## Out of scope

- Upgrading openspec to 1.10.0 (separate change: `openspec-upgrade-and-mise-bindings-v1`)
- Adopting OPSX schema (separate change: `opsx-schema-migration-plan-v1`)
- Adding openspec:completion (the shell completion manager; rarely needed)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive.
