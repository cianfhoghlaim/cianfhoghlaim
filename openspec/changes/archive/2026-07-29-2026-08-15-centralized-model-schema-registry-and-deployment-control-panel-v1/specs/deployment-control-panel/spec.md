# Spec delta: `deployment-control-panel`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
The 5 ADDED Requirements were already added to the canonical
`deployment-control-panel` spec by the parallel-session work. This
delta adds ONE new requirement: the audit log.

## ADDED Requirements

### Requirement: Audit log for control-panel actions

The system SHALL record every change made through the deployment
control panel (model enable/disable + jurisdiction enable/disable) in
a `stedding/deployment-control-panel/audit.log` file. Each line
SHALL be a JSON object with the timestamp, the user (from
Pocket ID OIDC), the action type, and the changed value.

#### Scenario: operator disables a model via the control panel

- **GIVEN** the operator opens the marimo control panel
- **WHEN** they click "disable" on `minimax-m3` in the text_llm family
- **THEN** the system SHALL append a JSON line to
  `stedding/deployment-control-panel/audit.log`:
  `{"timestamp": "...", "user": "...", "action": "disable",
   "family": "text_llm", "model": "minimax-m3"}`
- **AND** the next `mise run sync:all` SHALL reflect the change in
  the deployment-choice.yaml
