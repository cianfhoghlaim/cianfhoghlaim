# Spec delta: `agent-observability`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
5-layer observability stack to include the centralized-registry
drift detection.

## ADDED Requirements

### Requirement: agent-observability MUST include lint:registry in the observability stack

The system SHALL update `openspec/specs/agent-observability/spec.md`
to include `scripts/registry_audit.py` (`mise run lint:registry`) as
the 6th layer of the observability stack (alongside Langfuse, MLflow,
RAGAS, Logfire, and the existing 5-layer sync_health sensor).

#### Scenario: registry_drift_count flows through sync_health metadata

- **GIVEN** the new `_get_registry_drift_count()` helper in `orchestration/defs/sync_assets.py`
- **WHEN** `mise run sync:dagster` materializes `dagster_sync_health`
- **THEN** the `registry_drift_count` field is emitted as Dagster metadata
- **AND** a `registry_drift_alert` sensor fires when the count > 0

#### Scenario: agent-observability connects to the deployment control panel

- **GIVEN** the 5-tab marimo control panel at `notebooks/00_control_panel.py`
- **WHEN** the operator opens Tab 5 "Registry"
- **THEN** the registry drift count is shown as a StatCard (default=ok, drift>0=warning)
- **AND** the last_audit timestamp is displayed
