# 2026-08-22 — mise fmt + mise generate (adopt the new mise subcommands)

## Why

Mise 2026.5+ shipped two new subcommands that we haven't used:

- **`mise fmt`** — formats `mise.toml` (sorts keys, cleans up whitespace). Would catch the manual TOML issues I hit in the previous refactors (escape conflicts, multi-line array issues).
- **`mise generate`** — generates files for various tools/services (bootstrap scripts, devcontainer configs, GitHub Actions, git pre-commit hooks).

## What changes

1. **`mise.toml`** — add 5 new tasks in the `core` namespace:

   - `core:mise:fmt` (alias `mise:fmt`) — `mise fmt` auto-formats `mise.toml`
   - `core:mise:fmt:check` (alias `mise:fmt:check`) — `mise fmt --check` (CI gate, exits 1 on diff)
   - `core:mise:fmt:all` (alias `mise:fmt:all`) — `mise fmt --all` (formats all subprojects)
   - `core:mise:generate:pre-commit` (alias `mise:generate:pre-commit`) — generate a git pre-commit hook
   - `core:mise:generate:devcontainer` (alias `mise:generate:devcontainer`) — generate a devcontainer config

2. **`.agents/skills/mise/SKILL.md`** — add a new section on `mise fmt` + `mise generate`

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-domain-driven-mise-task-catalog-v1` (extends the mise namespace)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run core:mise:fmt --check` exits 0 (no formatting needed)
2. `mise run core:mise:fmt:all` runs without error
3. `mise run core:mise:generate:pre-commit --help` shows the help
4. `mise run core:mise:generate:devcontainer --help` shows the help
5. `.agents/skills/mise/SKILL.md` documents `mise fmt` + `mise generate`
6. `openspec validate --all --strict` exits 0

## Out of scope

- Adding `mise generate github-action` task (separate change if needed)
- Adding the pre-commit hook (would require a follow-up change to `.githooks/`)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive.
