## Implementation Tasks

- [x] 1. Refresh `.agents/skills/copilotkit-develop/SKILL.md` with a "CopilotKit v2 patterns" section. (verification-id: copilotkit-skill-updated) (verification: inspection)

- [x] 2. Refresh `.agents/skills/ag-ui/SKILL.md` with a "17-event protocol" section. (verification-id: ag-ui-skill-updated) (verification: inspection)

- [x] 3. Add `web:install:copilotkit` and `web:install:ag-ui` to `mise.toml [tasks]`. (verification-id: install-tasks-added) (verification: inspection)

- [x] 4. Run canonical CI gates: `mise run core:typecheck` (exit 0), `mise run lint:skills` (exit 0). (verification-id: no-regressions) (verification: integration)

## Final Validation

- [x] `openspec validate 2026-08-23-integration-copilotkit-v2-and-ag-ui-protocol-v1 --strict` passes
- [x] Both skills updated
- [x] 2 tasks added
- [x] Gates pass