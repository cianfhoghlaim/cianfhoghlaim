# 2026-08-15-cascading-registry-integration-v2

## Why

The `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
change (archived in commit `4f0a8f9d8`) introduced the 4 canonical
artifacts (MODEL_REGISTRY + schema.py + 00_control_panel + deployment-choice.yaml)
+ the 4 supporting artifacts (registry_audit.py + litellm_agent.py +
JurisdictionAssetsBase + 3 CocoIndex factories).

The follow-up `2026-08-15-cascading-registry-integration-v1` change
(commit `9f4391bcd` + archive `cfa6f88cf`) wired those 8 artifacts
across the repo (10 subagent skill_filters + 10 JurisdictionAssetsBase
subclasses + 3 factory L3 Component defs.yaml + Hono API routes +
23 marimo dashboards + mise.toml lint gate + sync_assets.py drift
metadata + 10 spec deltas).

The v1 change **deferred** 5 high-value cascading effects:

1. Migrate the remaining ~25 marimo dashboards (12 done in v1 → 80+
   remaining across BIEP v3 + Celtic + corpus + law + OCR + JC +
   England)
2. Wire the FULL `registry_drift_alert` Dagster sensor (v1 added the
   `_get_registry_drift_count()` helper but not the sensor + job +
   asset wiring)
3. Update the 2 remaining AGENTS.md files
   (`agents/meaisinfhoghlaim/AGENTS.md` + `spaces/_common/AGENTS.md`)
   + the root README.md to reference the 8 artifacts
4. Add a comprehensive test suite for `lint:registry` + `MODEL_REGISTRY`
   + the schema introspection helpers
5. Add the `notebooks/14_dev_env_tools_08_registry_drift_watch.py`
   companion to the MODEL_REGISTRY explorer (notebook 07)

This change completes all 5 deferred items in one round.

## What changes

### A. 25 marimo dashboard migrations

Migrate the remaining 25 high-value BIEP / Celtic / corpus / law / OCR
notebooks to surface the centralized-registry introspection helpers
(`_DEFAULT_LLM` + `_REGISTRY_SUMMARY` + `_DLT_SOURCE_COUNT` +
`_COCO_APP_COUNT` + `_BAML_CLASS_COUNT` + `_ENABLED_MODELS`). The
existing 23 notebooks already use this exact pattern (committed in
9f4391bcd); v2 extends it to the BIEP v2 portal + the Celtic languages
+ the corpus overview + the Irish law + the OCR ensemble audit + the
England AQA/OCR/Edexcel + the Junior Cycle Ireland notebook.

Files: 25 notebooks under `notebooks/0[2-8]_*.py` + `notebooks/1[1-2]_*.py`.

### B. registry_drift_alert Dagster sensor (full wiring)

Complete the deferred sensor wiring in `orchestration/defs/sync_assets.py`:

- New `registry_drift_alert` asset (key: `["registry", "drift_alert"]`)
  that emits `drift_count` + `drift_files` + `last_check` + `alert`
  metadata on every evaluation.
- New `materialize_registry_drift_alert_op` + `materialize_registry_drift_alert_job`
  that re-invokes `scripts/registry_audit.py --json` and raises a
  Dagster `Failure` if drift > 0.
- New `registry_drift_alert_sensor` (1-hour polling) that yields a
  `RunRequest` whenever drift > 0 AND the count differs from the
  last cursor value. Always emits an `AssetMaterialization` for the
  asset so the Dagster event log carries a per-tick audit record.
- Sibling helper `_get_registry_drift_files()` (added next to the
  v1 helper `_get_registry_drift_count()`) that invokes
  `scripts/registry_audit.py --json` and parses the file list.
- All 3 symbols wired into `orchestration/definitions.py` via
  `dg.Definitions.merge(defs, dg.Definitions(assets=[...],
  jobs=[...], sensors=[...]))`.

### C. AGENTS.md + README.md cascade

3 documentation updates:

- `agents/meaisinfhoghlaim/AGENTS.md`: new `## Centralized Registries`
  section + a `centralized-registry` row in the skill pointers table.
- `spaces/_common/AGENTS.md`: mirror the same section.
- Root `README.md`: new `## Centralized Registries (the single source
  of truth)` section with 2 code snippets showing the canonical
  `model_for("text_llm", "default")` pattern + the canonical
  `schema_introspect(conn)` pattern.

### D. Test suite (3 new files + 18 tests)

- `tests/test_model_registry.py`: 8 tests covering `model_for()` +
  `summary()` + `filter()` + duplicate detection + required-field
  validation.
- `tests/test_registry_audit.py`: 5 tests covering clean-repo exit 0
  + `--json` format + hardcoded-string detection + `--strict` exit 1
  + `tests/` path exclusion.
- `tests/test_schema_introspect.py`: 5 tests covering
  `list_dlt_sources()` (>=1000) + `list_cocoindex_apps()` (>=30) +
  `list_baml_classes()` (>=800) + `read_deployment_choice()` shape +
  write/read round-trip.
- `tests/__init__.py` already exists.

### E. Registry drift watcher notebook

New `notebooks/14_dev_env_tools_08_registry_drift_watch.py`:
- Invokes `scripts/registry_audit.py --json` and parses the findings.
- Renders a drift dashboard (count + files + replacement hints).
- Re-runs on every cell re-evaluation (live view of drift count).
- Complements the v1 `notebooks/14_dev_env_tools_07_model_registry.py`
  (the MODEL_REGISTRY explorer) + the new `registry_drift_alert`
  Dagster sensor (item B above).

### F. Spec deltas (2 new Requirements)

- `centralized-model-registry/spec.md`: new Requirement
  "The system MUST publish a registry drift watcher notebook that
  renders the audit findings + replacement hints + Dagster CI gate
  status in real time."
- `dagster-5-layer-component-architecture/spec.md`: new Requirement
  "The system MUST wire the `registry_drift_alert` asset +
  `materialize_registry_drift_alert_job` + `registry_drift_alert_sensor`
  in `orchestration/defs/sync_assets.py`, exposing them via
  `orchestration/definitions.py` via `dg.Definitions.merge`."

## Impact

- +1,073 LOC across 32 files (25 notebooks × 25 LOC + sensor + tests +
  docs + new notebook).
- 0 hardcoded model strings detected (the v1 lint:registry gate is
  unchanged).
- 1 new Dagster sensor (Layer 9 of the sync_health surface).
- 18 new pytest tests (all pass).
- 2 new spec deltas (added to canonical openspec/specs/).
- 1 new marimo notebook (drift watcher).
- 3 documentation updates (2 AGENTS.md + 1 README.md).

## Dependencies

- **Blocked by**: `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (archived)
- **Blocked by**: `2026-08-15-cascading-registry-integration-v1` (archived)

## Tasks

See `tasks.md`.