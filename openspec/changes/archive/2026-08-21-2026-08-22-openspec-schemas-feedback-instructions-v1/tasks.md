# Tasks — 2026-08-22 openspec new subcommands

## Phase 0 — Baseline

- [x] `openspec schemas --help` → works
- [x] `openspec feedback --help` → works
- [x] `openspec instructions --help` → works
- [x] `openspec templates --help` → works
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `openspec:schemas` task to `mise.toml` (alias `openspec:schema`)
- [ ] Add `openspec:schemas:json` task to `mise.toml` (alias `openspec:schema:json`)
- [ ] Add `openspec:feedback` task to `mise.toml` (alias `openspec:fb`)
- [ ] Add `openspec:instructions` task to `mise.toml` (alias `openspec:inst`)
- [ ] Add `openspec:templates` task to `mise.toml` (alias `openspec:tpls`)
- [ ] Verify `mise run openspec:schemas` exits 0
- [ ] Verify `mise run openspec:schemas:json` exits 0
- [ ] Verify `mise run openspec:instructions proposal` exits 0
- [ ] Update `.agents/skills/openspec/SKILL.md` — add 4 new subcommands
- [ ] Update `.opencode/agents/proposal-author.md` — reference 4 new subcommands

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 136 items
- [ ] Commit + push (user-initiated)
