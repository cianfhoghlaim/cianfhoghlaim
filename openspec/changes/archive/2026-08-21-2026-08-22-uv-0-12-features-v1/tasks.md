# Tasks — 2026-08-22 uv 0.12 features

## Phase 0 — Baseline

- [x] `uv --version` → 0.11.21 (latest is 0.12.5)
- [x] `uv lock --help` → `--refresh` flag present in 0.11.21
- [x] `uv format --help` → works in 0.11.21
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `core:uv:lock:refresh` task (alias `uv:lock:refresh`)
- [ ] Add `core:uv:lock:upgrade` task (alias `uv:lock:upgrade`)
- [ ] Add `core:uv:lock:upgrade-package` task (alias `uv:lock:upgrade-package`)
- [ ] Add `core:uv:tree:json` task (alias `uv:tree:json`)
- [ ] Add `core:uv:format` task (alias `uv:format`)
- [ ] Verify all 5 new tasks exit 0

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 142 items
- [ ] Commit + push (user-initiated)
