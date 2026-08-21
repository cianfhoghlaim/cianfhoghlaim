# Tasks — 2026-08-22 openspec update + extra subcommands

## Phase 0 — Baseline

- [x] `openspec update --help` → works
- [x] `openspec change --help` → works
- [x] `openspec spec --help` → works
- [x] `openspec config --help` → works
- [x] `openspec workspace --help` → works
- [x] `openspec context-store --help` → works
- [x] `openspec initiative --help` → works
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `openspec:update` task (alias `openspec:refresh`)
- [ ] Add `openspec:change` task (alias `openspec:change:cmd`)
- [ ] Add `openspec:spec` task (alias `openspec:spec:cmd`)
- [ ] Add `openspec:config` task (alias `openspec:cfg`)
- [ ] Add `openspec:workspace` task (alias `openspec:ws`)
- [ ] Add `openspec:context-store` task (alias `openspec:ctx`)
- [ ] Add `openspec:initiative` task (alias `openspec:init`)
- [ ] Verify all 7 new tasks exit 0 (or print help)

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 143 items
- [ ] Commit + push (user-initiated)
