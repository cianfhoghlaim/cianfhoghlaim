## ADDED Requirements

### Requirement: ml-agents-upgrade-tasks

The meaisínfhoghlaim agent fleet upgrade workflow SHALL be exposed
via 6 mise tasks — 5 per-framework tasks (pydantic-ai / google-adk /
agno / pipecat / copilotkit) + 1 omnibus task. Per the
`2026-08-23-agent-meaisinfhoghlaim-upgrade-cycle-v1` change.

#### Scenario: each task runs the framework upgrade + smoke test

- **WHEN** `mise run ml:agents:upgrade:<framework>` runs
- **THEN** it MUST `cd agents` (the subproject)
- **AND** MUST run `uv add <pkg>@latest` to bump the framework
- **AND** MUST run `uv sync` to update the lockfile
- **AND** MUST run `mise run ml:agents:smoke` to verify nothing broke

#### Scenario: omnibus task upgrades all 5 frameworks

- **WHEN** `mise run ml:agents:upgrade:all` runs
- **THEN** it MUST invoke all 5 per-framework upgrade tasks in sequence
- **AND** MUST emit a per-framework pass/fail summary at the end
