# copilotkit-agentic-surface Specification

## Purpose
TBD - created by archiving change 2026-09-24-web-agentic-deep-refactor-v1. Update Purpose after archive.

## Requirements

### Requirement: Shared CopilotKit + AG-UI module
The system SHALL provide a shared `web/apps/_shared/copilotkit/` module that:
- Exports the canonical Tool type + defineTool helper
- Exports callAgentRegistryRuntime() for the Python subprocess fallback
- Exports buildCopilotKitRuntimeConfig() + collectAllAguiEvents() with dev/prod branches
- Exports the 18-action canonical list (6 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject + 1 SCR commentary + 4 stage-specific + 2 misc)

#### Scenario: Both web apps import the shared module
- **WHEN** `cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts` imports from `web/apps/_shared/copilotkit/stage_router.ts`
- **AND** `cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/stage_router.ts` imports from `web/apps/_shared/copilotkit/stage_router.ts`
- **THEN** the stage_router resolves to the canonical Python stage_teams via lazy import

### Requirement: 18 canonical CopilotKit actions (real handlers)
The system SHALL provide 18 canonical CopilotKit actions in `actions.ts` (per the 2026-09-24 change). Each action's handler queries the Drizzle-backed DB (not stubbed).

#### Scenario: getSyllabusTopics returns real syllabus topics
- **WHEN** the operator invokes getSyllabusTopics with subject="mathematics"
- **THEN** the handler queries `lc_knowledge_graph` for the matching subject + level
- **AND** returns a non-empty topics array with weighting_pct from the DB
- **AND** the response is cached in the SPA (per the BIEP v3 cache policy)

### Requirement: AG-UI handshake endpoint
The system SHALL provide `POST /api/copilotkit/registry/handshake` that:
- Acknowledges the AG-UI protocol register event
- Returns the runtime_config + the collected AG-UI events
- Handles dev fallback (returns the in-process mirror if `COPILOTKIT_DEV_MODE=1`)

#### Scenario: SPA sends the AG-UI protocol handshake
- **WHEN** the SPA sends POST /api/copilotkit/registry/handshake with body `{ protocol: "ag-ui/v1", agent: { name: "lesson_planner_agent" } }`
- **THEN** the route returns `{ acknowledged: true, protocol: "ag-ui/v1", runtime_config: {...}, registered_agents: [...], collected_events: {...}, handshake_with: {...} }`
