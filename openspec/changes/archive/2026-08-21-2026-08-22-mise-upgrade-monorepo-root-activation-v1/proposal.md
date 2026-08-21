# 2026-08-22 — mise upgrade + monorepo_root activation

## Why

The previous refactor (`2026-08-22-mise-monorepo-mode-and-subprojects-v1`)
created `bonneagar/mise.toml` + `agents/mise.toml` (subprojects) and
declared `[settings] monorepo_root = true` + `[monorepo] config_roots` in
root `mise.toml`. But mise 2026.5.6 (our installed version) silently
ignored those fields — monorepo mode was introduced in mise 2026.7.17+.

We now have mise 2026.5.6 and need 2026.8.10 (latest) for:
- `monorepo_root` field recognition
- `MISE_MONOREPO_ROOT` env var
- `[monorepo.task_defaults.<name>]` (root task defaults)
- The various monorepo fixes from 2026.6+ through 2026.8+

## What changes

1. **`mise.toml`** — add `mise = "2026.8.10"` to the `[tools]` block (currently only uv/bun/dagger are listed)
2. **`mise.toml`** — uncomment + activate the `monorepo_root = true` and `[monorepo] config_roots` block (was commented out in the previous refactor)
3. **`mise.toml`** — add new tasks in the `core` namespace:
   - `core:mise:upgrade` (alias `mise:upgrade`) — `mise upgrade` (when installed via standalone installer)
4. **`mise.toml`** — add **root-level aliases** for the devops/ml:agents tasks that moved to subprojects. Now that monorepo_root is active, the alias resolution will work properly.
5. **`bonneagar/mise.toml` + `agents/mise.toml`** — verify monorepo mode now discovers them

## Dependencies

- **Blocked by:** `2026-08-22-mise-monorepo-mode-and-subprojects-v1` (this change activates what that change set up)
- **Blocked by (soft):** none
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. After running `mise install` (with the new pin), `mise --version` shows 2026.8.10+
2. The `settings.monorepo_root` warning is gone
3. `mise tasks --all` shows subproject tasks (e.g. `//devops:health` if monorepo path syntax is used)
4. `cd bonneagar && mise run devops:health` works (subproject task)
5. From root: `mise run devops:health` resolves via the root alias to the subproject task
6. `openspec validate --all --strict` exits 0

## Out of scope

- Migrating `web/`, `orchestration/`, `data/`, `ml/`, etc. as additional subprojects
- Adding `[monorepo.task_defaults.<name>]` (deferred to follow-up; not required for the basic fix)

## Rollback plan

Single commit. Revert via `git revert` if mise 2026.8.10 has any breaking change. The pin can be downgraded back to "latest" if needed.
