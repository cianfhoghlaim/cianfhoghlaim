# Tasks — 2026-08-15-cascading-registry-integration-v3

## Phase 1 — Pre-commit hook

- [ ] Create `.pre-commit-config.yaml` with the `lint-registry` hook
- [ ] Add `[tasks.pre-commit-install]` to `mise.toml`
- [ ] Add `[tasks.pre-commit-run]` to `mise.toml`
- [ ] Add `## Pre-commit hook` subsection to `.agents/skills/centralized-registry/SKILL.md`

## Phase 2 — 2 more DevEnv notebooks

- [ ] Create `notebooks/14_dev_env_tools_09_registry_drift_history.py` (5 cells, ~360 lines)
- [ ] Create `notebooks/14_dev_env_tools_10_deployment_choice_editor.py` (7 cells + 1 helper, ~333 lines)

## Phase 3 — Integration tests

- [ ] Create `tests/test_registry_end_to_end.py` (12 tests)
- [ ] Create `tests/test_sensor_end_to_end.py` (6 tests)
- [ ] Verify all 18 integration tests pass via pytest

## Phase 4 — Spec deltas + validation

- [ ] Add spec delta to `openspec/changes/2026-08-15-cascading-registry-integration-v3/specs/centralized-model-registry/spec.md`
- [ ] Add spec delta to `openspec/changes/2026-08-15-cascading-registry-integration-v3/specs/deployment-control-panel/spec.md`
- [ ] Run `openspec validate 2026-08-15-cascading-registry-integration-v3 --strict`

## Phase 5 — Archive + commit

- [ ] Archive: `openspec archive 2026-08-15-cascading-registry-integration-v3 --yes`
- [ ] Commit the staged changes
- [ ] Push to origin/main
- [ ] Verify with the 13 quality gates