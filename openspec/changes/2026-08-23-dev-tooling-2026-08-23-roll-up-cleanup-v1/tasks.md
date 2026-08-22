## Implementation Tasks

- [x] 1. Update `AGENTS.md` to add `core:tool-versions:report`, `core:tool-versions:check-stale`, and `lint:spec:purpose` to the "Priority mise tasks" list (under "Daily 'I'm working on X' commands"). (verification-id: priority-tasks-updated) (verification: inspection — AGENTS.md contains the 3 new tasks)

- [x] 2. Update `.opencode/agents/mise.md` to reference the new observability tasks (`core:tool-versions:report`, `core:tool-versions:check-stale`) in the Direct references section. (verification-id: agent-docs-updated) (verification: inspection — the agent file references the 2 tasks)

- [x] 3. Run the canonical gates to confirm no regressions: `mise run lint:skills`, `mise run core:typecheck`, `openspec validate --all --strict`. (verification-id: no-regressions) (verification: integration — all gates pass)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-dev-tooling-2026-08-23-roll-up-cleanup-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-dev-tooling-2026-08-23-roll-up-cleanup-v1 --strict` passes
- [x] AGENTS.md updated
- [x] .opencode/agents/mise.md updated
- [x] Canonical gates pass
