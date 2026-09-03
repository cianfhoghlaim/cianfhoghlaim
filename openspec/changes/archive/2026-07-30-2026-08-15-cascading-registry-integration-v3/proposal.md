# 2026-08-15-cascading-registry-integration-v3

## Why

The `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
change (archived in commit `4f0a8f9d8`) introduced the 8 canonical
+ supporting artifacts.

The `2026-08-15-cascading-registry-integration-v1` change
(commit `9f4391bcd`) wired those 8 artifacts across the repo
(23 marimo dashboards + 10 subagents + 10 jurisdiction assets +
3 factory L3 components + Hono API routes + 10 spec deltas).

The `2026-08-15-cascading-registry-integration-v2` change
(commit `2b8273085`) completed 5 deferred items from v1 (25 more
notebooks + the full sensor wiring + AGENTS.md cascade + 18 unit
tests + the drift watcher notebook + 14 spec deltas).

The v2 change **deferred** 3 final cascade items:

1. Add a pre-commit hook that blocks commits that introduce
   hardcoded model strings (the missing enforcement layer that
   would have caught v1 + v2 regressions at commit time)
2. Add 2 more DevEnv marimo notebooks to complete the operator
   toolkit (drift history + deployment-choice editor)
3. Add integration tests that validate the end-to-end flow

This change completes all 3 deferred items in one round.

## What changes

### A. Pre-commit hook (the missing enforcement layer)

Create `.pre-commit-config.yaml` + 2 new mise tasks
(`pre-commit-install` + `pre-commit-run`) that install + run a
pre-commit hook which blocks commits if `mise run lint:registry`
detects hardcoded model strings. Update the
`.agents/skills/centralized-registry/SKILL.md` skill to document
the new hook.

### B. 2 more DevEnv marimo notebooks

- `notebooks/14_dev_env_tools_09_registry_drift_history.py`: shows
  the drift count over time by parsing `stedding/sync-reports/*.json`
  + the optional Dagster event log for `registry/drift_alert`
  materializations.
- `notebooks/14_dev_env_tools_10_deployment_choice_editor.py`: a
  visual editor for `deployment-choice.yaml` with `mo.ui.switch`
  toggles per entry + a save button that calls
  `write_deployment_choice()` (dry-run by default, real write when
  `DEPLOYMENT_CHOICE_EDIT=write`).

### C. Integration tests (18 new tests across 2 files)

- `tests/test_registry_end_to_end.py` (12 tests): validates the
  full round-trip from MODEL_REGISTRY → schema introspection →
  deployment-choice.yaml + verifies all 8 canonical + supporting
  artifacts exist on disk.
- `tests/test_sensor_end_to_end.py` (6 tests): validates the
  registry_drift_alert sensor + job + asset end-to-end.

### D. Spec deltas (2 new Requirements)

- `centralized-model-registry/spec.md`: new Requirement "The
  system MUST publish a pre-commit hook that blocks commits
  introducing hardcoded model strings (the missing enforcement
  layer)."
- `deployment-control-panel/spec.md`: new Requirement "The system
  MUST publish a deployment-choice editor notebook that provides
  a visual interface for toggling enabled_models +
  enabled_pipelines + enabled_stacks."

## Impact

- +1,400 LOC across 7 files (2 mise tasks + 1 pre-commit YAML +
  2 notebooks + 2 integration test files + 1 SKILL.md update).
- 18 new integration tests pass (12 + 6).
- 1 new pre-commit hook blocks future drift regressions at commit
  time.
- 2 new marimo notebooks complete the operator toolkit.
- 2 new spec deltas (added to canonical `openspec/specs/`).

## Dependencies

- **Blocked by**: `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (archived)
- **Blocked by**: `2026-08-15-cascading-registry-integration-v1` (archived)
- **Blocked by**: `2026-08-15-cascading-registry-integration-v2` (archived)

## Tasks

See `tasks.md`.