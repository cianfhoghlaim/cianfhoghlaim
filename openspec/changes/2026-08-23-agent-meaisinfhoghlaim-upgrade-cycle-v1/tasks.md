## Implementation Tasks

- [x] 1. Add the 6 new `ml:agents:upgrade:*` tasks to `mise.toml [tasks]`. Each follows the pattern `cd agents && uv add <pkg>@latest && uv sync && mise run ml:agents:smoke`. (verification-id: upgrade-tasks-added) (verification: inspection — `mise tasks --all | grep ml:agents:upgrade` shows 6 tasks)

- [x] 2. Verify each task runs from the agents subproject (uses `MISE_PROJECT_ROOT` + `cd agents`). (verification-id: subproject-routing) (verification: inspection — each task's `run` starts with `cd ${MISE_PROJECT_ROOT:-.}/agents`)

- [x] 3. Run the canonical CI gates to confirm no regressions: `mise run core:typecheck` (exit 0), `openspec validate --all --strict` (exit 0). (verification-id: no-regressions) (verification: integration — both gates pass)

## Final Validation

Expected archive gate: `openspec validate 2026-08-23-agent-meaisinfhoghlaim-upgrade-cycle-v1 --archive-gate`

- [x] `openspec validate 2026-08-23-agent-meaisinfhoghlaim-upgrade-cycle-v1 --strict` passes
- [x] All 6 tasks exist
- [x] Each task runs from the agents subproject
- [x] Canonical gates pass
