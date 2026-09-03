## ADDED Requirements

### Requirement: registry_drift_alert Dagster sensor

The system MUST wire the `registry_drift_alert` asset +
`materialize_registry_drift_alert_job` + `registry_drift_alert_sensor`
in `orchestration/defs/sync_assets.py` so that:

1. The `registry_drift_alert` asset (key: `["registry", "drift_alert"]`,
   group `3_model_lifecycle/sync_health`) emits `drift_count` +
   `drift_files` + `last_check` + `alert` metadata on every evaluation.
2. The `materialize_registry_drift_alert_job` runs the
   `materialize_registry_drift_alert_op` which:
   - Re-invokes `scripts/registry_audit.py --json`
   - Emits a Dagster `AssetMaterialization` for the
     `registry/drift_alert` asset
   - Raises a Dagster `Failure` if drift > 0 (so the job fails loudly)
3. The `registry_drift_alert_sensor`:
   - Polls every hour (`minimum_interval_seconds=3600`)
   - Yields a `RunRequest` for `materialize_registry_drift_alert_job`
     when drift > 0 AND the count differs from the cursor value
     (cursor key: `registry_drift_count`)
   - Always emits a `SensorResult` with an `AssetMaterialization` for
     the `registry/drift_alert` asset (per-tick audit record)
4. All 3 symbols are wired into `orchestration/definitions.py` via
   `dg.Definitions.merge(defs, dg.Definitions(assets=[...],
   jobs=[...], sensors=[...]))`.
5. A sibling helper `_get_registry_drift_files()` is added next to
   the v1 helper `_get_registry_drift_count()` in
   `orchestration/defs/sync_assets.py` for the file list (the v1
   helper only returns the count).

#### Scenario: Sensor detects drift and fires the job

- **GIVEN** the v2 cascading change has added the 3 new symbols
- **AND** `scripts/registry_audit.py` reports `count: 1` (drift detected)
- **WHEN** the `registry_drift_alert_sensor` evaluates
- **THEN** it yields a `RunRequest` for `materialize_registry_drift_alert_job`
- **AND** it emits a `SensorResult` with an `AssetMaterialization`
  for `registry/drift_alert` with metadata `drift_count=1, drift_files=['<file>']`
- **AND** the cursor is updated to `{"registry_drift_count": 1}`

#### Scenario: Sensor dedupes consecutive identical drift counts

- **GIVEN** the cursor is `{"registry_drift_count": 1}` (last reported)
- **AND** `scripts/registry_audit.py` still reports `count: 1`
- **WHEN** the sensor evaluates again
- **THEN** it does NOT yield a `RunRequest` (dedup)
- **AND** it still emits a `SensorResult` with an `AssetMaterialization`
  (per-tick audit record)
- **AND** the cursor remains `{"registry_drift_count": 1}`

#### Scenario: Sensor fires when drift count increases

- **GIVEN** the cursor is `{"registry_drift_count": 1}`
- **AND** `scripts/registry_audit.py` now reports `count: 3` (new drift)
- **WHEN** the sensor evaluates
- **THEN** it yields a `RunRequest` (count changed from 1 → 3)
- **AND** the cursor updates to `{"registry_drift_count": 3}`

#### Scenario: definitions.py loads the 3 new symbols

- **GIVEN** the 3 new symbols are defined in `orchestration/defs/sync_assets.py`
- **WHEN** `dagster dev` loads `orchestration/definitions.py`
- **THEN** the asset `registry/drift_alert` appears in the Dagster UI
- **AND** the job `materialize_registry_drift_alert` is launchable
- **AND** the sensor `registry_drift_alert_sensor` is active