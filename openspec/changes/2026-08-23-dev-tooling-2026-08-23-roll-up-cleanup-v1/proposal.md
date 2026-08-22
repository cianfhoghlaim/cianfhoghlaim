# 2026-08-23 — Dev-tooling docs roll-up (Phase 2 final cleanup)

## Why

After Phase 1 (3 real failure remediations) + Phase 2 (4 openspec changes), the dev-environment tooling surface has accumulated:

- 2 new mise tasks (`core:tool-versions:report`, `core:tool-versions:check-stale`)
- 1 new mise task (`lint:spec:purpose`)
- 2 new shell scripts (`scripts/tool-versions-report.sh`, `scripts/check_tool_versions_stale.sh`)
- A new "First-time mise install" section in `.agents/skills/mise/SKILL.md`
- Pinned versions for 7 critical tools in `mise.toml [tools]`
- Filled-in Purpose sections for 10 data specs

Without a docs roll-up, agents reading `AGENTS.md` / `openspec/AGENTS.md` won't know about the new tasks. This change is a **docs-only** roll-up that cross-links the new surfaces from the priority quick-reference tables.

## What changes

### 1. `AGENTS.md` — add new tasks to "Priority mise tasks"

Add 3 new tasks to the "Priority mise tasks" list:
- `core:tool-versions:report`
- `core:tool-versions:check-stale`
- `lint:spec:purpose`

### 2. `openspec/AGENTS.md` — add new openspec commands (none needed; the 7 Phase 2 tasks don't add new openspec CLI wrappers)

### 3. `.opencode/agents/mise.md` — add 2 new mise 2026.8+ features

Document:
- `mise fmt` (auto-format mise.toml)
- `mise generate pre-commit` (generate the pre-commit hook)
- `core:tool-versions:report` / `core:tool-versions:check-stale` (the new observability surface)

## Dependencies

- **Blocked by (soft):** the 4 Phase 2 openspec changes
- **Affected repos:** cianfhoghlaim only
- **Out of scope:** skill file updates for tools beyond mise (already updated in earlier rounds)

## Acceptance criteria

1. `AGENTS.md` contains `core:tool-versions:report`, `core:tool-versions:check-stale`, `lint:spec:purpose` in the priority mise tasks list
2. `.opencode/agents/mise.md` references the new observability tasks
3. `openspec validate 2026-08-23-dev-tooling-2026-08-23-roll-up-cleanup-v1 --strict` exits 0

## Rollback plan

- Revert the 3 docs files via `git checkout`
- No code changes to revert
