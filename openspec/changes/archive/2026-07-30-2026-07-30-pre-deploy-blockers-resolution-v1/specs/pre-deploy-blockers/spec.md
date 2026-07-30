# Spec delta: `pre-deploy-blockers`

This delta is part of the openspec change
`2026-07-30-pre-deploy-blockers-resolution-v1`. The 3 ADDED Requirements
in the delta were already added to the canonical `pre-deploy-blockers`
spec by the parallel-session work. This delta adds ONE new requirement:
the integration with the deployment control panel.

## ADDED Requirements

> Note: The 3 base requirements (image digest pinning, arm1-oci headroom check,
> T1 stack docs + secrets env generation) were already added to the canonical
> spec by the parallel-session work. This delta focuses only on the
> deployment control panel integration.

### Requirement: pre-deploy tasks surface in the deployment control panel

The system SHALL surface the 4 pre-deploy mise tasks (pre-deploy:fetch-image-digests,
pre-deploy:arm1-oci-headroom, pre-deploy:generate-stack-docs,
pre-deploy:generate-stack-secrets) in the deployment control panel marimo notebook
(`notebooks/24_deployment_control_panel.py`) as a "Pre-deploy blockers" panel
at the top of the notebook, with one click-to-run button per task.

#### Scenario: Deployment control panel surfaces pre-deploy status

- **WHEN** the user opens `notebooks/24_deployment_control_panel.py`
- **THEN** the "Pre-deploy blockers" panel SHALL show the current status of all 4 tasks
  (✅ done / ⚠️ pending / 🚫 failing) based on the latest pre-deploy reports in
  `stedding/pre-deploy/`
- **AND** clicking each task button SHALL emit a click-to-run marker (the actual
  `mise run` invocation is operator-side; the click only sets the intent flag)

#### Scenario: Pre-deploy panel auto-refreshes after each mise run

- **WHEN** any of the 4 pre-deploy mise tasks is invoked
- **THEN** the `stedding/pre-deploy/` reports SHALL be regenerated
- **AND** the deployment control panel SHALL re-read the reports on the next
  refresh
