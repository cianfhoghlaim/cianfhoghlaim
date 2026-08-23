## Implementation Tasks

- [x] 1. Add the "OpenCode Agent Dispatch Matrix" section to AGENTS.md (after the "## Best Practices" section). (verification-id: dispatch-matrix-added) (verification: inspection — `grep "## OpenCode Agent Dispatch Matrix" AGENTS.md` returns the new section)

- [x] 2. Verify all 15 agents are documented (4 primary + 5 functional + 10 domain). (verification-id: all-15-agents-documented) (verification: inspection — the new section lists all 15 names: `build`, `plan`, `data-platform`, `infrastructure`, `agent-platform`, `frontend-apps`, `research`, `baml`, `dagster`, `mise`, `notebooks`, `orchestrator`, `proposal-author`, `deep-cuts`, `dev-env-demo`)

- [x] 3. Run `mise run lint:drift-docs` to confirm no AGENTS.md count drift. (verification-id: no-drift) (verification: integration — `mise run lint:drift-docs` exits 0)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-agent-opencode-agent-coverage-expansion-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-agent-opencode-agent-coverage-expansion-v1 --strict` passes
- [x] AGENTS.md updated
- [x] All 15 agents documented
- [x] `lint:drift-docs` exits 0
