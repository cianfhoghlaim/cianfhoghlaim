# Tasks: 2026-07-12-british-isles-endpoint-recovery-v1

## 1. Create the shared helper

- [ ] 1.1 Create `dlt/common/endpoint_recovery.py` with:
  - `RecoveredPage` dataclass (`status`, `backend_used`,
    `content_hash`, `content`, `language`, `wayback_snapshot_url`,
    `firecrawl_metadata`)
  - `EndpointRecoveryStrategy` enum (`auto | stealth | wayback`)
  - `endpoint_recovery.fetch(url, strategy="auto", wait_for=8s) -> RecoveredPage`
  - `endpoint_recovery.probe_all_39() -> dict[str, int]` returning the
    status code for every canonical British Isles endpoint
  - `endpoint_recovery.PROBE_LIST` — the canonical 39 endpoints
    (matches the audit doc table)
  - Structlog `endpoint_status{status, backend_used}` event

## 2. Fix the 11 broken sources

- [ ] 2.1 Edit `dlt/british_isles/ireland/education/ncca.py`
- [ ] 2.2 Edit `dlt/british_isles/ireland/education/curriculumonline_syllabi.py`
- [ ] 2.3 Edit `dlt/british_isles/scotland/education/sqa/syllabus_source.py`
- [ ] 2.4 Edit `dlt/british_isles/england/education/aqa/syllabus_source.py`
- [ ] 2.5 Edit `dlt/british_isles/england/education/pearson/syllabus_source.py`
- [ ] 2.6 Edit `dlt/british_isles/wales/education/wjec/syllabus_source.py`
- [ ] 2.7 Edit `dlt/british_isles/northern_ireland/education/ccea/syllabus_source.py`
- [ ] 2.8 Edit `dlt/british_isles/ireland/law/courts_ie.py` — fix the
  judgements URL to `/search/judgements`
- [ ] 2.9 Edit `dlt/british_isles/england/medicine/gmc.py`
- [ ] 2.10 Edit `dlt/british_isles/isle_of_man/medicine/health_social_care.py`
- [ ] 2.11 Edit `dlt/british_isles/isle_of_man/education/isle_of_man.py`

## 3. Dagster L2 assets

- [ ] 3.1 Create
  `orchestration/defs/2_materials/endpoint_health/sink.py` with
  `endpoint_health_sink` (cron `0 */6 * * *`)
- [ ] 3.2 Create
  `orchestration/defs/2_materials/endpoint_health/alerts.py` with
  `endpoint_health_alerts` (cron `0 */6 * * *`, depends on `sink`)
- [ ] 3.3 Create
  `orchestration/defs/2_materials/endpoint_health/defs.yaml`
- [ ] 3.4 Each fixed source gains an `@asset_check` named
  `<source_slug>_endpoint_alive` (declared in the new
  `endpoint_recovery.py` helper as `endpoint_recovery.declare_asset_check`)

## 4. Audit doc

- [ ] 4.1 Create
  `docs/agents/british_isles_endpoint_health_audit.md` with:
  - The 39-endpoint probe table (snapshot from the plan)
  - The 11 broken entries + their fix
  - The 28 healthy entries (for completeness)
  - A "How to re-run the audit" section pointing at
    `endpoint_recovery.probe_all_39()`

## 5. Spec deltas

- [ ] 5.1 ADDED Requirement on
  `british-isles-education-pipeline/spec.md` for the
  `endpoint_health_sink` + `endpoint_health_alerts` assets
- [ ] 5.2 MODIFIED delta on `oideachais-pipeline/spec.md` adding a
  cross-reference to the new `endpoint_recovery` helper

## 6. Validate

- [ ] 6.1 `openspec validate 2026-07-12-british-isles-endpoint-recovery-v1 --strict` passes
- [ ] 6.2 `endpoint_recovery.probe_all_39()` returns 200 for all 39 endpoints
- [ ] 6.3 All 11 fixed source files AST-parse
- [ ] 6.4 `dg check yaml` passes on the new endpoint_health defs
- [ ] 6.5 `mise run lint:skills` still passes (53/53)

## 7. Commit + push

- [ ] 7.1 Single commit with message
  `fix(biep): recover the 11 broken British-Isles endpoints (NCCA / SQA / AQA / CCEA / GMC / IoM + courts.ie/judgements URL)`
- [ ] 7.2 `git push origin main`
