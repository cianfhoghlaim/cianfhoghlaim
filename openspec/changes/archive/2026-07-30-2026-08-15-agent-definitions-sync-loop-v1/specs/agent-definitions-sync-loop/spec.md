# Spec delta: `agent-definitions-sync-loop`

This delta is part of the openspec change
`2026-08-15-agent-definitions-sync-loop-v1`. The 6 ADDED Requirements
in the delta were already added to the canonical `agent-definitions-sync-loop`
spec by the parallel-session work. This delta adds ONE new requirement:
the agent definitions surface for the deployment control panel.

## ADDED Requirements

> Note: The 6 base requirements (Layer 1-5 + orchestrator) were already
> added to the canonical spec by the parallel-session work. This delta
> focuses only on the deployment control panel integration.

### Requirement: agent-definitions layer status surfaces in deployment control panel

The system SHALL surface the `sync:agents` Layer 10 status in the
deployment control panel marimo notebook (`notebooks/24_deployment_control_panel.py`)
with one click-to-run button + the latest sync report preview.

#### Scenario: Deployment control panel surfaces agents layer

- **WHEN** the user opens `notebooks/24_deployment_control_panel.py`
- **THEN** the "agents" layer status SHALL show ✅ done / ⚠️ pending / 🚫 failing
- **AND** clicking the agents button SHALL emit a click-to-run marker
  (the actual `mise run sync:agents` invocation is operator-side)
- **AND** the latest sync report from `stedding/sync-reports/agents-{date}.md`
  SHALL be shown as a preview tooltip