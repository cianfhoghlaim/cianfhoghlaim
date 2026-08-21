# Tasks — 2026-08-22 openspec 1.10 upgrade + mise bindings

## Phase 0 — Baseline

- [x] Latest openspec = 1.10.0 (we run 1.4.1)
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `openspec:upgrade` task to `mise.toml` (alias `openspec:version:upgrade`)
- [ ] Update `.agents/skills/openspec/SKILL.md` with 1.10 features section
- [ ] Document the `bun add -g @fission-ai/openspec@1.10.0` upgrade path
- [ ] Verify `mise run openspec:upgrade` prints the install command correctly

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 145 items
- [ ] Commit + push (user-initiated)

## Post-commit (user action)

- [ ] User runs `bun add -g @fission-ai/openspec@1.10.0` to actually upgrade
- [ ] User verifies `openspec --version` shows 1.10.0
- [ ] User verifies `openspec schemas` shows the new schemas
