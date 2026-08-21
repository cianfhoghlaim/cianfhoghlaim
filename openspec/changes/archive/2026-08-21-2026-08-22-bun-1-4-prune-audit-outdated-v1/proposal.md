# 2026-08-22 — bun 1.4 (adopt latest + add outdated gate)

## Why

Bun v1.4 was released 2026-08-20 (8 hours ago at the time of this change). Our `package.json` pins `bun@1.3.0` (an old version) and the actual installed binary is `bun 1.3.14`. This is 14 minor versions behind within the 1.3 line, and 1 full major version behind.

The new `bun outdated` subcommand (already available in 1.3+, improved in 1.4) gives us a way to surface dependency freshness in our CI gates (we currently have NO bun check — only `bun audit` works for vulns, `bun outdated` for freshness).

Note: Earlier research suggested `bun prune` and `bun audit fix` were planned for 1.4, but on local verification:
- `bun prune` → "reserved for future use by Bun" (not in 1.4)
- `bun audit --fix` → not yet available

So the realistic 1.4 wins are:
1. Bump the `packageManager` pin from `bun@1.3.0` to `bun@1.4` (engines field already says `>=1.3.0`)
2. Add `core:bun:outdated` task — new freshness gate (analogous to `core:uv:audit`)
3. Add `core:bun:upgrade` task — one-command bun upgrade (uses the new `bun upgrade`)

## What changes

1. `package.json` — bump `packageManager` from `bun@1.3.0` to `bun@1.4`
2. `mise.toml` — add 2 new tasks in the `core` namespace:
   - `core:bun:outdated` — list outdated dependencies for each workspace
   - `core:bun:upgrade` — upgrade to latest bun (single command)
3. `.agents/skills/mise/SKILL.md` — note the new tasks

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-domain-driven-mise-task-catalog-v1` (extends the namespace)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `package.json` shows `packageManager: "bun@1.4"`
2. `mise run core:bun:outdated` exits 0 (reports current outdated deps)
3. `mise run core:bun:upgrade` exits 0 (or shows the upgrade command)
4. `bun --version` >= 1.4
5. `openspec validate --all --strict` exits 0

## Out of scope

- Adding `bun prune` (not yet shipped; the upstream command is reserved for future use)
- Adding `bun audit --fix` (not yet shipped; would require a separate change when available)
- Updating the bun lockfile (defer to a separate "bun lockfile refresh" change)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive (no existing tasks removed).
