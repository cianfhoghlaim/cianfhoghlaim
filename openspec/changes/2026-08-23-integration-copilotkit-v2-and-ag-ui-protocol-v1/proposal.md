# 2026-08-23 — Refresh CopilotKit v2 + AG-UI protocol skill (skill update + 2 tasks)

## Why

The web app already uses CopilotKit v2 + AG-UI SSE (per the 2026-08-13
web-monorepo consolidation change). But the canonical patterns aren't
documented in:
- `.agents/skills/copilotkit-develop/SKILL.md` (still describes v1 patterns)
- `.agents/skills/ag-ui/SKILL.md` (doesn't document the 17-event protocol)

The 109 source files importing from `@copilotkit/react-core/v2` (per
the Phase 1 web:install fix) need a canonical reference for the v2
import path + the v2 API surface.

## What changes

### 1. Skill refresh: `.agents/skills/copilotkit-develop/SKILL.md`

- Add a "CopilotKit v2 patterns" section documenting:
  - The `/v2` sub-export import path
  - The v2 API changes (CopilotRuntime v2 + CopilotChat v2 + useCopilotChat v2)
  - The 4 new `useFrontedTool` / `useHumanInTheLoop` / `useAttachments` / `useCapabilities` hooks
  - The migration table from v1 → v2 (with the agentic-frontend-frameworks spec cross-link)

### 2. Skill refresh: `.agents/skills/ag-ui/SKILL.md`

- Add a "17-event protocol" section documenting:
  - The 17 events (RunStarted, RunFinished, TextMessageStart, TextMessageContent, ToolCallStart, ToolCallArgs, ToolCallResult, StateSnapshot, StateDelta, MessagesSnapshot, Raw, Custom, Source, ToolCallEnd, TextMessageEnd, RunError, StepStarted, StepFinished)
  - The SSE wire format
  - The cross-link to the runtime + react-core skills

### 3. 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `web:install:copilotkit` | `bun install @copilotkit/react-core @copilotkit/react-ui` (the 2 canonical deps, with `/v2` correctly resolved) |
| `web:install:ag-ui` | `bun install @ag-ui/core` (the AG-UI protocol types, pinned at ^0.5.0) |

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the 2026-08-13 web-monorepo consolidation change
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. Both skill files updated with the new sections
2. The 2 new tasks exist in `mise.toml`
3. `mise run web:install` still passes (the imports use `/v2` correctly per the Phase 1 fix)
4. `openspec validate 2026-08-23-integration-copilotkit-v2-and-ag-ui-protocol-v1 --strict` exits 0