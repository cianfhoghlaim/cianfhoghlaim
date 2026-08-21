# Tasks — 2026-08-22 mise fmt + mise generate

## Phase 0 — Baseline

- [x] `mise fmt --help` → works (auto-formats mise.toml)
- [x] `mise generate --help` → works
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `core:mise:fmt` task (alias `mise:fmt`)
- [ ] Add `core:mise:fmt:check` task (alias `mise:fmt:check`)
- [ ] Add `core:mise:fmt:all` task (alias `mise:fmt:all`)
- [ ] Add `core:mise:generate:pre-commit` task (alias `mise:generate:pre-commit`)
- [ ] Add `core:mise:generate:devcontainer` task (alias `mise:generate:devcontainer`)
- [ ] Update `.agents/skills/mise/SKILL.md` with a new "fmt + generate" section
- [ ] Verify all 5 new tasks exit 0 (or print help)

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 141 items
- [ ] Commit + push (user-initiated)
