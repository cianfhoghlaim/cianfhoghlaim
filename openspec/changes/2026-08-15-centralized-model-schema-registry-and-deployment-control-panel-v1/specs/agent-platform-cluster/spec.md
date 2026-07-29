# Spec delta: `agent-platform-cluster`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the new `MODEL_REGISTRY` as the LiteLLM config source
and removes the legacy hardcoded LiteLLM aliases.

## ADDED Requirements

### Requirement: LiteLLM config is regenerated from MODEL_REGISTRY

The system SHALL regenerate
`bonneagar/stacks/litellm/config/config.yaml` from `MODEL_REGISTRY`
on every `mise run cic:meaisin:litellm-regenerate`. The 5 M3
chokepoint aliases (`kimi/k2`, `glm/5.1`, `minimax/m2.5`, `mimo/2.5`,
`deepseek/flash`) + the 24 `local/vision/*` entries SHALL all be
derived from `MODEL_REGISTRY`.

#### Scenario: LiteLLM config is generated from MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs
  `mise run cic:meaisin:litellm-regenerate`
- **THEN** `bonneagar/stacks/litellm/config/config.yaml` is regenerated
  from `MODEL_REGISTRY`
- **AND** the file contains no hand-edited model_list entries
- **AND** the 5 ghost-model references (`qwen3-vl-235b-a22b`,
  `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`, `gemma-4-31B`,
  `gemma-3-27b-it`) are removed

### Requirement: Deployment control panel consumes sync reports

The system SHALL provide a marimo notebook
`notebooks/24_deployment_control_panel.py` that reads the latest
sync report from `stedding/sync-reports/all-{date}.md` and surfaces
the per-layer status + the model registry + the MCP server health.

This requirement was added in the
`2026-08-15-knowledge-sync-loop-v1` change (Change B — the
model-registry change consumes the sync reports as the canonical
"operator's eye" on the repo's knowledge state).

#### Scenario: Deployment control panel shows 5 layer statuses

- **GIVEN** the latest `stedding/sync-reports/all-{date}.md` exists
- **WHEN** a user opens `notebooks/24_deployment_control_panel.py` in marimo
- **THEN** the notebook SHALL display the 5 sync layer statuses
  (paths / ccc / cognee / skills / mcp) at the top with
  pass/fail/info indicators
- **AND** the notebook SHALL list the 14 MCP servers (from
  `opencode.json`)
- **AND** the notebook SHALL list the 54+ agent skills
- **AND** the notebook SHALL have an expander that shows the full
  sync report

### Requirement: sync_health Dagster asset emits sync metadata

The system SHALL provide a Dagster asset `sync_health` at
`orchestration/defs/sync_assets.py` that reads the latest
`stedding/sync-reports/all-{date}.md` and emits metadata for the
5 sync layers.

This requirement was added in the
`2026-08-15-knowledge-sync-loop-v1` change (Change B — the sync
metadata is consumed by the deployment control panel + the
`stale_skill_alert` Dagster job).

#### Scenario: sync_health materializes on cron

- **GIVEN** the `0 */4 * * *` cron fires (every 4 hours)
- **WHEN** the `sync_health` asset materializes
- **THEN** it SHALL emit the following Dagster metadata:
  `paths_sync_time`, `ccc_chunk_count`, `cognee_cluster_count`,
  `skill_pass_rate`, `mcp_server_count_healthy`,
  `layer_statuses` (per-layer pass/fail), `path_pattern_counts`
  (per-pattern count from the paths report)
- **AND** it SHALL trigger a downstream Dagster job
  `stale_skill_alert` if `skill_pass_rate < 0.95`

### Requirement: sync_report_sensor fires on new reports

The system SHALL provide a Dagster sensor `sync_report_sensor` that
fires when a new `stedding/sync-reports/all-{date}.md` file is
created (i.e. after `mise run sync:all`).

#### Scenario: sync_report_sensor fires on new file

- **GIVEN** the sensor is running with `minimum_interval_seconds=3600`
- **WHEN** a new `stedding/sync-reports/all-{date}.md` file is created
  (e.g. after `mise run sync:all`)
- **THEN** the sensor SHALL enqueue a `RunRequest` for the
  `sync_health` asset
- **AND** the `sync_health` asset SHALL re-materialize
- **AND** the `sync_health_refresh` job SHALL complete within 60 seconds