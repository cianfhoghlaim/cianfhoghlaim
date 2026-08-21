# Tasks — 2026-08-22 mise monorepo mode + subproject split

## Phase 0 — Baseline

- [x] `mise --version` → 2026.5.6 (supports monorepo_root)
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `[settings] monorepo_root = true` + `[monorepo] config_roots = [...]` to root `mise.toml`
- [ ] Remove `iac:*` tasks from root `mise.toml` (they'll move to bonneagar)
- [ ] Remove `ml:agents:*` tasks from root `mise.toml` (they'll move to agents)
- [ ] Create `bonneagar/mise.toml` with the migrated devops tasks
- [ ] Create `agents/mise.toml` with the migrated ml:agents tasks
- [ ] Verify `mise tasks --all` shows both root + subproject tasks
- [ ] Verify `cd bonneagar && mise run devops:health` works
- [ ] Verify `cd agents && mise run ml:agents:smoke` works
- [ ] Verify back-compat aliases still work (e.g. `mise run devops:health` from root)

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 137 items
- [ ] Commit + push (user-initiated)
