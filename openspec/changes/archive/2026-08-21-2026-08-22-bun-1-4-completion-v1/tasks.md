# Tasks — 2026-08-22 bun 1.4 completion

## Phase 0 — Baseline

- [x] `bun --version` → 1.4.0
- [x] `bun prune --help` → works (was incorrectly deferred in previous refactor)
- [x] `bun audit fix --help` → works
- [x] `bun dedupe --help` → works
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `core:bun:prune` task (alias `bun:prune`)
- [ ] Add `core:bun:audit:fix` task (alias `bun:audit:fix`)
- [ ] Add `core:bun:audit:fix:dry-run` task (alias `bun:audit:fix:dry-run`)
- [ ] Add `core:bun:dedupe` task (alias `bun:dedupe`)
- [ ] Add `core:bun:format` task (alias `bun:format`)
- [ ] Add `core:bun:parallel` task (alias `bun:parallel`)
- [ ] Add `web:test:parallel` task (alias `web:test:parallel`)
- [ ] Update `.opencode/agents/mise.md` with 4 Bun API mentions (Bun.cron, Bun.markdown, Bun.Image, Bun.serve)
- [ ] Verify all 6 new core tasks exit 0
- [ ] Verify `web:test:parallel` runs in parallel

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 140 items
- [ ] Commit + push (user-initiated)
