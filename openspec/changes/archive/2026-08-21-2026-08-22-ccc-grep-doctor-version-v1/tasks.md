# Tasks — 2026-08-22 ccc grep + ccc doctor + ccc version

## Phase 0 — Baseline

- [x] `ccc --version` → 0.2.41 (already installed)
- [x] `ccc grep --help` → works (structural search)
- [x] `ccc doctor --help` → works (system health)
- [x] `ccc version` → prints `0.2.41`
- [x] `ccc search --json "test"` → emits JSON on stdout
- [x] `mkdir -p openspec/changes/.../specs/dev-tooling-surfaces/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write `specs/dev-tooling-surfaces/spec.md` delta (1 ADDED Requirement)
- [ ] `openspec validate ... --strict` → pass

## Phase 1 — Implement

- [ ] Add `core:ccc:grep` task to `mise.toml` (alias `ccc:grep`)
- [ ] Add `core:ccc:doctor` task to `mise.toml` (alias `ccc:doctor`)
- [ ] Add `core:ccc:version` task to `mise.toml` (alias `ccc:version`)
- [ ] Add `core:ccc:search:json` task to `mise.toml` (alias `ccc:search:json`)
- [ ] Verify `mise run core:ccc:grep "def run"` returns matches
- [ ] Verify `mise run core:ccc:doctor` exits 0
- [ ] Verify `mise run core:ccc:version` prints `0.2.41`
- [ ] Update 9 domain agent `.md` files (add `ccc grep` to direct references)
- [ ] Verify `ccc grep` reference in `.opencode/agents/data-platform.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/infrastructure.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/agent-platform.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/frontend-apps.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/notebooks.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/baml.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/dagster.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/mise.md`
- [ ] Verify `ccc grep` reference in `.opencode/agents/proposal-author.md`

## Phase 2 — Archive

- [ ] `openspec validate ... --strict` → exits 0
- [ ] `openspec archive ... --yes` → archives the change
- [ ] Verify `openspec validate --all --strict` exits 0 with 134 items
- [ ] Commit + push (user-initiated)
