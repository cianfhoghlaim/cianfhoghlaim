# Tasks — 2026-08-22 mise upgrade + monorepo_root activation

## Phase 0 — Baseline

- [x] Latest mise = 2026.8.10 (we run 2026.5.6)
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `mise = "2026.8.10"` to the [tools] block in root `mise.toml`
- [ ] Add `core:mise:upgrade` task to root `mise.toml`
- [ ] Uncomment + activate `[settings] monorepo_root = true` + `[monorepo] config_roots`
- [ ] Add root-level aliases for the devops tasks moved to bonneagar/:
  - `devops:health` (alias of `//devops:health`)
  - `devops:plan` (alias of `//devops:plan`)
  - `devops:bootstrap` (alias of `//devops:bootstrap`)
  - `devops:bootstrap-pangolin-client` (alias)
  - `devops:deploy`
  - `devops:teardown`
- [ ] Add root-level aliases for the ml:agents tasks moved to agents/:
  - `ml:agents:smoke`
  - `ml:agents:audit`
  - `ml:agents:reproduce`
- [ ] Verify `mise tasks --all` shows subproject tasks
- [ ] Verify `cd bonneagar && mise run devops:health` works
- [ ] Verify from root: `mise run devops:health` resolves via the new alias

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 144 items
- [ ] Commit + push (user-initiated)
