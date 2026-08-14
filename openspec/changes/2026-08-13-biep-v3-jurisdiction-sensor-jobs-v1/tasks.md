# Tasks: BIEP v3 jurisdiction sensor jobs

## Phase A — Code-only wiring (no live services required)

- [ ] A1 Create `orchestration/sensors/jobs.py` with 8
  `define_asset_job` instances:
  - `ncca_registry_change_job` selecting `["ireland_documents_ingested"]`
  - `sqa_registry_change_job` selecting `["scotland_documents_ingested"]`
  - `ccea_registry_change_job` selecting
    `["northern_ireland_documents_ingested"]`
  - `wjec_registry_change_job` selecting `["wales_documents_ingested"]`
  - `jcq_registry_change_job` selecting `["england_documents_ingested"]`
  - `isle_of_man_registry_change_job` selecting
    `["isle_of_man_documents_ingested"]`
  - `jersey_registry_change_job` selecting `["jersey_documents_ingested"]`
  - `guernsey_registry_change_job` selecting
    `["guernsey_documents_ingested"]`

- [ ] A2 Update `orchestration/sensors/__init__.py` to re-export all 8
  new job instances alongside the existing `garage_pdf_arrival_job`.

- [ ] A3 Verify each sensor's `job_name=` matches the new job by
  grepping `orchestration/sensors/<sensor>.py` against the names in
  `jobs.py`. All 8 should match.

## Phase B — Verification (no live services required)

- [ ] B1 `python -c "from orchestration.sensors import jobs"` imports
  cleanly (asserts no Dagster job-config typos).
- [ ] B2 `python -c "from orchestration.sensors.jobs import *; assert
  all(callable(v) or hasattr(v, 'name') for v in
  [ncca_registry_change_job, sqa_registry_change_job,
  ccea_registry_change_job, wjec_registry_change_job,
  jcq_registry_change_job, isle_of_man_registry_change_job,
  jersey_registry_change_job, guernsey_registry_change_job])"`.
- [ ] B3 `mise run lint:registry && mise run sync:dagster` both pass
  without new errors.
- [ ] B4 `openspec validate 2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1
  --strict` returns 0 errors.

## Phase C — Dagster launchpad live verification (requires live infra)

- [ ] C1 `dagster job list | grep -E "registry_change_job"` returns 8
  lines (the 8 new jobs).
- [ ] C2 `dagster sensor list | grep registry` returns 11 lines (8
  wired + 3 existing real).
- [ ] C3 Reset each sensor's cursor; verify the emitted `RunRequest`
  resolves to a valid job and the corresponding asset materialises
  without `JobNotFoundError` in the Dagster logs.

## Out of scope (flagged for follow-up)

- The `garage_pdf_arrival_job` already follows this pattern correctly
  (per the lakehouse-hydration change); no change needed.
- The `ocr_completion_sensor`, `upstream_breaking_change_sensor`, and
  `meaisin_education_ops_sensor` use their own jobs (defined inline);
  no change needed.
- **Discovered during implementation** (separate scope): the existing
  `meaisin_education_ops_sensor.py:134` and
  `ocr_completion_sensor.py:130` pass `default_status=None`, which the
  Dagster 1.13+ `@sensor` decorator rejects with
  `ParameterCheckError: Param "default_status" is not a
  DefaultSensorStatus. Got None`. Both should be
  `DefaultSensorStatus.STOPPED` (or `.RUNNING` for the
  `upstream_breaking_change_sensor` precedent at line 175). Flagged
  for `2026-08-14-dagster-sensor-default-status-v1` — not fixed here
  because (a) it's pre-existing and unrelated to the sensor-job wiring
  pattern this change addresses and (b) fixing it here would expand
  scope beyond the declared change boundaries.
