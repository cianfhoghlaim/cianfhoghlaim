# 2026-07-24-biep-v2-gov-uk-change-detection-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1 + 2 + 3 + 4 merged on `origin/main`
- [ ] Verify the ChangeDetection.io stack is running:
  `docker compose -f bonneagar/stacks/changedetection/compose.yaml -f sidecar.yaml up -d`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — ChangeDetection.io monitors

- [ ] Create `bonneagar/stacks/changedetection/monitors/aqa_monitor.yaml` —
  AQA spec pages monitor (108 watched pages: 9 subjects × 2 levels × 6 selectors)
- [ ] Create `bonneagar/stacks/changedetection/monitors/ocr_monitor.yaml`
- [ ] Create `bonneagar/stacks/changedetection/monitors/edexcel_monitor.yaml`
- [ ] Each monitor MUST:
  - Use `web_scraping` mode + CSS selector
  - Watch spec version + PDF link
  - Trigger a webhook to `http://dagster-webhook:8080/webhooks/england_change_detection`
- [ ] Upload all 3 monitors to the dev ChangeDetection.io vault via the
  ChangeDetection.io REST API (`curl -X POST .../api/v1/watch`)
- [ ] Verify the monitors appear in the ChangeDetection.io UI

## Stage 2 — Dagster sensor

- [ ] Create `orchestration/defs/sensors/__init__.py` if not exists
- [ ] Create `orchestration/defs/sensors/england_change_detection_sensor.py`:
  - `@asset_sensor(asset_key=AssetKey("eng_aqa_mathematics_ingested"),
                   job=england_england_re_extraction_job)`
  - Resolves the board + subject + level from the webhook payload
  - Triggers the re-extraction job
  - Emits a Langfuse trace event
- [ ] Add the sensor to the existing Dagster root definition
- [ ] Run `dg check yaml` to validate

## Stage 3 — DuckLake audit table

- [ ] Create the DuckLake migration script at
  `dlt/common/migrations/2026-07-24-biiep-v2-england-changes.sql`:
  - `CREATE TABLE oideachais.education.british_isles.england.changes`
    with the 11 columns from the proposal
- [ ] Run `mise run ducklake:migrate` to apply the migration
- [ ] Verify the table is queryable: `duckdb ... "SELECT 1 FROM oideachais.education.british_isles.england.changes LIMIT 0"`

## Stage 4 — Slack/email webhook alerts

- [ ] Add a Langfuse prompt + webhook config for the
  `kcg-biep-v2-changes` Slack channel
- [ ] Add an email-notification hook to `kcg-curriculum@cianfhoghlaim.ie`
- [ ] Verify the alerting path with a test event

## Stage 5 — End-to-end test

- [ ] Run `mise run py:test_integration england_change_detection_sensor`
  with a synthetic ChangeDetection.io webhook payload:
  - Posts to the sensor's webhook endpoint
  - Verifies the sensor fires the re-extraction job
  - Verifies the DuckLake `changes` table receives the audit row
  - Verifies the Slack/email alerts fire

## Stage 6 — Spec delta commits + validation

- [ ] Run `openspec validate 2026-07-24-biep-v2-gov-uk-change-detection-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-24-biep-v2-gov-uk-change-detection-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-24-biep-v2-gov-uk-change-detection-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/research/biep_v2_change_detection_status.md` with the
  now-green status
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
