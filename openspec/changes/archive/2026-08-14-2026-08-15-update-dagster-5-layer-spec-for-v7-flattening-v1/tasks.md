# Tasks: Update dagster-5-layer-component spec for v7 flattening

This is a spec-only change — zero code edits. One PR.

## Phase A — Spec text update (this PR)

- [ ] **A.1** Update the spec's `pyproject.toml:[tool.dg].registry_modules` example from `["cianfhoghlaim.dagster.components"]` to `["orchestration.components"]` with a footnote about the post-v7 flattening
- [ ] **A.2** Add 1 new Requirement: "After the v7 flattening, registry_modules uses the repo-root path" with 3 Scenarios
- [ ] **A.3** Run `openspec validate 2026-08-15-update-dagster-5-layer-spec-for-v7-flattening-v1 --strict` and confirm exit 0
- [ ] **A.4** Commit + push
- [ ] **A.5** Run `openspec archive 2026-08-15-update-dagster-5-layer-spec-for-v7-flattening-v1 --yes` (after merge)
