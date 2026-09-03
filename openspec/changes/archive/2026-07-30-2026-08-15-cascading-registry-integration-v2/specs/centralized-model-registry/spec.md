## ADDED Requirements

### Requirement: Registry drift watcher notebook

The system MUST publish a registry drift watcher notebook at
`notebooks/14_dev_env_tools_08_registry_drift_watch.py` that:

1. Invokes `scripts/registry_audit.py --json` and parses the
   structured findings (count + file list + matched string).
2. Renders a drift dashboard showing the total drift count + the
   list of offending files + the canonical `MODEL_REGISTRY` entry
   that should replace each finding (if a registry entry exists).
3. Re-runs the audit on every cell re-evaluation so the operator
   can edit a file and see the drift count drop in real time.
4. Includes a CI gate status block that displays whether
   `mise run lint:registry` will pass (drift = 0) or fail
   (drift > 0) and whether the `registry_drift_alert_sensor` will
   fire on the next tick.
5. References the canonical skill (`.agents/skills/centralized-registry/SKILL.md`)
   + the canonical Dagster sensor
   (`orchestration/defs/sync_assets.py:registry_drift_alert_sensor`)
   + the companion explorer notebook (`notebooks/14_dev_env_tools_07_model_registry.py`).

#### Scenario: Operator opens the drift watcher notebook

- **GIVEN** the v1 cascading change has wired the 8 canonical artifacts
- **WHEN** the operator runs `marimo edit notebooks/14_dev_env_tools_08_registry_drift_watch.py`
- **THEN** the notebook shows the current drift count (must be 0)
- **AND** the notebook shows the canonical `MODEL_REGISTRY` entries
  that should replace each finding (if any)
- **AND** the notebook shows the CI gate status (`✓ 0 drift — gate passes`)
- **AND** the notebook's docstring references the centralized-registry skill + the Dagster sensor + the MODEL_REGISTRY explorer