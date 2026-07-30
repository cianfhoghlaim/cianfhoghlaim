# Spec delta: `agentic-frontend-frameworks`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It adds the 5th
canonical web surface for the deployment control panel.

## ADDED Requirements

### Requirement: agentic-frontend-frameworks MUST register the 5th web surface (control-panel)

The system SHALL register `web/apps/cianfhoghlaim-web/src/routes/control-panel/index.tsx`
as the 5th canonical web surface for the deployment control panel.
The 5 surfaces are:

1. `web/apps/cianfhoghlaim-web/` (the public web app)
2. `web/apps/tuatha-ui/` (the Túatha educational MMO frontend)
3. `web/apps/croilar-web/` (the Croílár multi-persona portfolio)
4. `web/apps/croilar-portal/` (the Croílár portfolio dashboard)
5. `web/apps/cianfhoghlaim-web/control-panel/` (NEW: deployment control panel)

#### Scenario: The 5th surface mounts in the Hono API router

- **GIVEN** the new TanStack Start route at `web/apps/cianfhoghlaim-web/src/routes/control-panel/index.tsx`
- **WHEN** `web/hono-api/src/index.ts` imports `controlPanelApp` and mounts it at `/api/control-panel`
- **THEN** the 8 Hono endpoints (5 GETs + 3 POSTs) are reachable
- **AND** the marimo notebook + the web UI both read/write the same `deployment-choice.yaml`

#### Scenario: The 5th surface conforms to the agentic-frontend-frameworks contract

- **GIVEN** the deployment control panel TanStack Start route
- **WHEN** the operator opens `localhost:3000/control-panel`
- **THEN** the 5 tabs render without error (Models / Pipelines / Datasets / Stacks / Registry)
- **AND** the data is sourced from the Hono API at `/api/control-panel/*`
- **AND** the Hono API delegates to the Python bridge at `web/hono-api/control-panel/_python_bridge.py`
