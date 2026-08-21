# Tasks — 2026-08-22 bun 1.4

## Phase 0 — Baseline

- [x] `bun --version` → 1.3.14 (latest stable = 1.4)
- [x] `bun outdated` works (already in 1.3+)
- [x] `bun prune` → "reserved for future use" (skip)
- [x] `bun audit --fix` → not available (skip)
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Update `package.json` — bump `packageManager` from `bun@1.3.0` to `bun@1.4`
- [ ] Add `core:bun:outdated` task to `mise.toml` (alias `bun:outdated`)
- [ ] Add `core:bun:upgrade` task to `mise.toml` (alias `bun:upgrade`)
- [ ] Verify `mise run core:bun:outdated` exits 0 (lists outdated deps)
- [ ] Verify `mise run core:bun:upgrade` exits 0 (or shows the upgrade command)
- [ ] Update `.agents/skills/mise/SKILL.md` with the new tasks

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 135 items
- [ ] Commit + push (user-initiated)
