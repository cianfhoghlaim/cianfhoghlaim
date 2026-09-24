# `web/apps/_shared/copilotkit/` — the shared CopilotKit + AG-UI module

Per the 2026-09-24-web-agentic-deep-refactor-v1 change.

The canonical source of truth for the CopilotKit + AG-UI surface.
Both web apps (`cianfhoghlaim-web` + `cianfhoghlaim-leaving-cert`)
re-export from this module so the agent selection + the action list +
the stage_router stay consistent.

## What's shared here

- `stage_router.ts` — resolves the right Agno Team for a given BIEP v3 stage
- `index.ts` (re-export barrel) — the shared Tool type + the devFallbackConfig
  + the `buildCopilotKitRuntimeConfig()` + `collectAllAguiEvents()` helpers

## Why a separate module

The cianfhoghlaim-web app + cianfhoghlaim-leaving-cert app both mount a
Hono + CopilotKit runtime. Previously each had its own (divergent)
stage_router + actions definitions. The 2026-09-24 change consolidates them.

## Usage (from the per-app src/copilotkit/)

```ts
// cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts
export { resolveStageTeam, type StageSlug } from "../../../../_shared/copilotkit/stage_router";

// cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts
import { ALL_ACTIONS } from "../../../_shared/copilotkit";
// (or import the specific actions needed)
```

## Adding a new shared piece

1. Add the new file (or function) under `web/apps/_shared/copilotkit/`
2. Export from `index.ts`
3. Add the per-app re-export if it's specific to that app's runtime config

See `.agents/skills/copilotkit-agui-bridge/SKILL.md` for the full
CopilotKit + AG-UI surface skill.
