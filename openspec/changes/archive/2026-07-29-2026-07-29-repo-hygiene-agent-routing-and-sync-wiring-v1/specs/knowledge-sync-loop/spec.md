# Spec delta: `knowledge-sync-loop`

This change adds 3 requirements to the existing `knowledge-sync-loop`
spec (the 5-layer pull-based sync architecture):

1. **Layer 6 — sync:dagster** (the gap surfaced by the
   `2026-08-15-retroactive-pre-v7-cleanup-v1` change — validates the
   ~833 Dagster assets in the 5-layer `defs/` tree)
2. **Daily sync_health cron** (the cron that the existing
   `sync_health` asset docstring in `orchestration/defs/sync_assets.py`
   already promises)
3. **Stale-skill alert** (the threshold `skill_pass_rate < 0.95` that
   the asset docstring documents but the spec does not yet require)

The 10 base requirements already in the spec (Layer 1-5 sync +
orchestrator + 3 feedback loops) are unchanged.

## ADDED Requirements

### Requirement: Layer 6 — sync:dagster (Dagster-defs validation)

The system SHALL provide a `mise run sync:dagster` task that validates
the ~833 Dagster assets in the 5-layer `defs/` tree
(`1_ingestion/`, `2_materials/`, `3_model_lifecycle/`,
`4_asset_generation/`, `5_agent_ops/`).

#### Scenario: sync:dagster runs cleanly

- **WHEN** `mise run sync:dagster` is invoked
- **THEN** the task SHALL walk the 5-layer `defs/` tree
- **AND** the task SHALL parse each `.py` file with `ast`
- **AND** the task SHALL validate that all `@asset` decorators have
  working imports + that all sensors reference existing jobs
- **AND** the task SHALL write a per-group report to
  `stedding/sync-reports/dagster-{date}.md`
- **AND** the task SHALL exit 0 if all assets parse + reference cleanly,
  exit 1 otherwise

#### Scenario: sync:dagster is part of sync:all

- **GIVEN** `mise run sync:all` runs the orchestrator
- **WHEN** the `sync:dagster` layer is appended to `scripts/sync/all.sh`
- **THEN** the unified report at `stedding/sync-reports/all-{date}.md`
  SHALL include the `Layer: sync:dagster` section
- **AND** the `sync_health` Dagster asset SHALL pick up the
  `dagster_defs_count` metadata

### Requirement: Daily sync_health cron

The system SHALL attach the `sync_health` Dagster asset to a
`0 */4 * * *` cron schedule via
`orchestration/automation/sync_schedules.py`.

#### Scenario: The cron is wired

- **GIVEN** the `sync_health` asset is defined in
  `orchestration/defs/sync_assets.py`
- **WHEN** `orchestration/automation/sync_schedules.py` is created
  with `@schedule(cron_schedule="0 */4 * * *", job=...)`
- **THEN** the cron SHALL materialize `sync_health` every 4 hours
- **AND** the cron SHALL emit the `paths_sync_time`, `ccc_chunk_count`,
  `cognee_cluster_count`, `skill_pass_rate`, `mcp_server_count_healthy`
  metadata each tick
- **AND** the cron SHALL be discoverable via the Dagster UI on
  `http://localhost:3000/schedules`

#### Scenario: A sync layer is failing

- **GIVEN** the cron just fired
- **WHEN** any of the 6 layers reports `fail` in the unified report
- **THEN** the `sync_health` asset SHALL emit a `failure` materialization
  event in Dagster
- **AND** the asset's metadata SHALL include the failing layer name
- **AND** a downstream Dagster sensor SHALL trigger a Slack notification
  (per the existing `sync:all operator egress notification` requirement)

### Requirement: Stale-skill alert when skill_pass_rate < 0.95

The system SHALL trigger a downstream Dagster job when the
`skill_pass_rate` metric (emitted by `sync_health`) drops below 0.95.

#### Scenario: A skill fails lint

- **GIVEN** `mise run lint:skills` reports 148 of 155 skills pass
  (skill_pass_rate = 0.955)
- **WHEN** the `sync_health` asset materializes
- **THEN** no alert is triggered (above the 0.95 threshold)

#### Scenario: A skill fails lint below the threshold

- **GIVEN** `mise run lint:skills` reports 145 of 155 skills pass
  (skill_pass_rate = 0.935)
- **WHEN** the `sync_health` asset materializes
- **THEN** the `stale_skill_alert` asset SHALL trigger a downstream job
- **AND** the downstream job SHALL emit a Slack notification with
  the failing skill names + the `mise run lint:skills` output
- **AND** the threshold (`0.95`) SHALL be configurable via the
  `sync_health_alert_threshold` Dagster job config

## Cross-references

- `orchestration/defs/sync_assets.py` — the existing `sync_health` asset
- `orchestration/automation/sync_schedules.py` — the new cron wiring
- `scripts/sync/dagster.sh` — Layer 6 script (Phase 3 deliverable)
- `scripts/sync/all.sh` — the orchestrator that wires all 7 layers
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1` —
  sibling change that surfaces the `sync:dagster` gap
