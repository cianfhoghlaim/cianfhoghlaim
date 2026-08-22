## ADDED Requirements

### Requirement: dev-tooling-roll-up-coverage

The Phase 2 docs roll-up MUST update AGENTS.md + .opencode/agents/mise.md to reference the 3 new tasks (`core:tool-versions:report`, `core:tool-versions:check-stale`, `lint:spec:purpose`) introduced by Phase 2's 4 openspec changes. The docs MUST be updated as part of the `2026-08-23-dev-tooling-2026-08-23-roll-up-cleanup-v1` change.

#### Scenario: AGENTS.md includes the 3 new tasks

- **WHEN** `grep -E "core:tool-versions:report|core:tool-versions:check-stale|lint:spec:purpose" AGENTS.md` runs
- **THEN** it MUST return at least 3 matches (one per new task)
- **AND** the tasks MUST appear in the "Priority mise tasks" section

#### Scenario: .opencode/agents/mise.md references the observability tasks

- **WHEN** `.opencode/agents/mise.md` is read
- **THEN** the file MUST reference both `core:tool-versions:report` and `core:tool-versions:check-stale`
- **AND** the references MUST be in the Direct references section
