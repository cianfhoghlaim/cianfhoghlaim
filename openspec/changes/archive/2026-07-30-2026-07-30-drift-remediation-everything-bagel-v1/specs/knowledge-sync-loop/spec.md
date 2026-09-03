# Spec delta: `knowledge-sync-loop`

This change adds 1 requirement to the existing `knowledge-sync-loop`
spec: the `Daily sync_health cron` requirement SHALL be guaranteed
resilient to file truncation commits (a regression that was introduced
in commit `91b85c1c1`).

## ADDED Requirements

### Requirement: sync_health_job + dagster_sync_health_job are pinned in sync_assets.py

The system SHALL ensure that `sync_health_job` and
`dagster_sync_health_job` are always defined in
`orchestration/defs/sync_assets.py` so that
`orchestration/automation/sync_schedules.py` can import them.

#### Scenario: A commit truncates sync_assets.py

- **GIVEN** `orchestration/automation/sync_schedules.py:17-18` imports
  `sync_health_job` + `dagster_sync_health_job`
- **WHEN** a commit removes those definitions from `sync_assets.py`
- **THEN** the cron registration fails silently
  (`sync_schedules_load_failed: cannot import name 'sync_health_job'`)
- **AND** the `Daily sync_health cron` requirement is violated

#### Scenario: The drift-remediation change restores the jobs

- **GIVEN** the regression above
- **WHEN** the `drift-remediation` change appends the 4 deleted assets +
  2 utility functions + 2 sensor definitions + 2 job definitions back
  to `sync_assets.py`
- **THEN** `from orchestration.definitions import defs` succeeds
- **AND** `defs.schedules` includes both `sync_health_every_4h` +
  `dagster_sync_health_every_4h`
- **AND** the `Daily sync_health cron` requirement is satisfied

## Cross-references

- `orchestration/defs/sync_assets.py` — the canonical asset home
- `orchestration/automation/sync_schedules.py` — the cron wiring
- `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/specs/drift-remediation/spec.md` —
  the new spec that mandates the resilience
