# 2026-08-22 — bun 1.4 completion (adopt previously-deferred features + missed helpers)

## Why

The previous refactor (`2026-08-22-bun-1-4-prune-audit-outdated-v1`) bumped `packageManager` to `bun@1.4` and added `core:bun:outdated` + `core:bun:upgrade`. But the previous change **incorrectly deferred** `bun prune` + `bun audit --fix` claiming they were "reserved for future use". On local verification, both commands are GA in bun 1.4.0 (we run 1.4.0 locally).

This change adopts the 3 previously-deferred bun 1.4 features + 3 missed helpers from the 1.4 release notes (the blog at https://bun.com/blog/bun-v1.4).

## What changes

1. **`mise.toml`** — add 6 new tasks in the `core` namespace:

   - `core:bun:prune` (alias `bun:prune`) — remove packages from `node_modules` not in `bun.lock`
   - `core:bun:audit:fix` (alias `bun:audit:fix`) — `bun audit fix` upgrades vulnerable packages to the lowest safe version
   - `core:bun:dedupe` (alias `bun:dedupe`) — `bun dedupe` removes duplicate versions from `bun.lock`
   - `core:bun:format` (alias `bun:format`) — `bunx prettier --write .` (the missed formatter)
   - `core:bun:parallel` (alias `bun:parallel`) — `bun run --parallel` (the missed parallel runner)
   - `core:bun:audit:fix:dry-run` (alias `bun:audit:fix:dry-run`) — dry-run variant

2. **`web` namespace** — add 1 new task:

   - `web:test:parallel` (alias `web:test:parallel`) — `bunx turbo run test --parallel` (parallel test runner)

3. **`.opencode/agents/mise.md`** — add `Bun.cron()`, `Bun.markdown`, `Bun.Image`, `Bun.serve` mentions to the Direct references section (the Bun API surface a future agent could use).

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-22-bun-1-4-prune-audit-outdated-v1` (extends the bun domain)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run core:bun:prune` exits 0 (or reports nothing to prune)
2. `mise run core:bun:audit:fix:dry-run` exits 0 (or reports no fixes)
3. `mise run core:bun:dedupe` exits 0
4. `mise run core:bun:format` exits 0
5. `mise run core:bun:parallel --bun-run="echo 1; echo 2"` runs in parallel
6. `mise run web:test:parallel` runs in parallel
7. `.opencode/agents/mise.md` references the 4 new Bun API mentions
8. `openspec validate --all --strict` exits 0

## Out of scope

- Upgrading bun to 1.5+ (not yet released)
- Bun.Install offline cache (still in 1.4+ but requires additional config)
- Bun.test improvements (`--parallel` already covered)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive.
