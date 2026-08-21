# Tasks — 2026-08-22 uv audit + uv check

## Phase 0 — Baseline

- [x] `uv --version` → 0.11.21 (✓ supports both)
- [x] `uv audit --help` → works
- [x] `uv check --help` → works
- [x] `mkdir -p openspec/changes/.../specs/dev-tool-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md` (this file)
- [ ] Write `specs/dev-tool-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `core:uv:audit` task to `mise.toml` (alias `uv:audit`)
- [ ] Add `core:uv:audit:strict` task to `mise.toml` (alias `uv:audit:strict`)
- [ ] Add `core:uv:check` task to `mise.toml` (alias `uv:check`)
- [ ] Add `core:uv:audit-malware` task to `mise.toml`
- [ ] Wire `core:uv:audit:strict` + `core:uv:check` into `core:lint` aggregate
- [ ] Validate: `mise run core:uv:audit:strict` exits 0
- [ ] Validate: `mise run core:uv:check` exits 0
- [ ] Validate: `mise run core:lint` exits 0

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 133 items
- [ ] Commit + push (user-initiated)
