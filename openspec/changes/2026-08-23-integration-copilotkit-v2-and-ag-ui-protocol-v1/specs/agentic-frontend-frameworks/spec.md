## ADDED Requirements

### Requirement: copilotkit-v2-patterns

The `.agents/skills/copilotkit-develop/SKILL.md` skill MUST document the
CopilotKit v2 import patterns + the v2 API surface. Per the
`2026-08-23-integration-copilotkit-v2-and-ag-ui-protocol-v1` change.

#### Scenario: skill documents the /v2 sub-export import

- **WHEN** a new agent reads `.agents/skills/copilotkit-develop/SKILL.md`
- **THEN** the skill MUST explain the `/v2` sub-export import path
- **AND** the skill MUST link to the runtime + ag-ui skills for the
  related concerns

### Requirement: ag-ui-17-event-protocol

The `.agents/skills/ag-ui/SKILL.md` skill MUST document the AG-UI 17
event protocol + the SSE wire format. Per the
`2026-08-23-integration-copilotkit-v2-and-ag-ui-protocol-v1` change.

#### Scenario: skill documents all 17 AG-UI events

- **WHEN** a new agent reads `.agents/skills/ag-ui/SKILL.md`
- **THEN** the skill MUST list all 17 events (RunStarted through StepFinished)
- **AND** the skill MUST show the SSE event format example