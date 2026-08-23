# 2026-08-23 — meaisínfhoghlaim framework upgrade cycle (5 new ml:agents:upgrade:* tasks)

## Why

The meaisínfhoghlaim agent fleet (12 specialist agents + 8 NCCA
educational agents) uses 5 frameworks: Pydantic AI, Google ADK, Agno,
Pipecat, CopilotKit. Each framework ships releases independently. The
current workflow requires running `uv add <pkg>@latest` manually
inside `agents/` and then re-running the agent smoke tests.

This change adds **5 dedicated upgrade tasks** that wrap the per-framework
upgrade + smoke test workflow. Each task:
1. Bumps the framework to its latest version (verified via `uv pip list --outdated`)
2. Re-runs `uv sync` to update `uv.lock`
3. Re-runs the relevant smoke tests (e.g., `ml:agents:smoke` for the ADK agents)
4. Surfaces the diff for the agent to review

## What changes

### 5 new mise tasks in `mise.toml`

| Task | Framework | What it does |
|:--|:--|:--|
| `ml:agents:upgrade:pydantic-ai` | Pydantic AI 1.17+ | `uv add pydantic-ai@latest` + smoke test |
| `ml:agents:upgrade:google-adk` | Google ADK 1.17+ | `uv add google-adk@latest` + smoke test |
| `ml:agents:upgrade:agno` | Agno 2.6+ | `uv add agno@latest` + smoke test |
| `ml:agents:upgrade:pipecat` | Pipecat 0.5+ | `uv add pipecat-ai@latest` + smoke test |
| `ml:agents:upgrade:copilotkit` | CopilotKit 1.67+ | `uv add copilotkit@latest` + smoke test |

Each task follows the same pattern:
```bash
run = "cd ${MISE_PROJECT_ROOT:-.}/agents && uv add <pkg>@latest && uv sync && mise run ml:agents:smoke"
```

### A `ml:agents:upgrade:all` omnibus task

Runs all 5 framework upgrades in sequence. Use sparingly (each
framework may have breaking changes that need individual review).

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - The actual upgrade (the task just orchestrates the `uv add` + smoke test; the agent decides whether to bump)
  - Breaking-change migration paths (each upgrade is independent; tracked as separate openspec changes)

## Acceptance criteria

1. All 5 `ml:agents:upgrade:*` tasks + 1 `ml:agents:upgrade:all` task exist in `mise.toml`
2. Each task runs from `${MISE_PROJECT_ROOT:-.}/agents` (the subproject)
3. Each task includes a smoke test invocation
4. `openspec validate 2026-08-23-agent-meaisinfhoghlaim-upgrade-cycle-v1 --strict` exits 0
5. Running any single upgrade task in dry-run mode shows the upgrade command + smoke test command

## Rollback plan

- Remove the 6 tasks from `mise.toml`
- No data loss; no API changes; no migration
