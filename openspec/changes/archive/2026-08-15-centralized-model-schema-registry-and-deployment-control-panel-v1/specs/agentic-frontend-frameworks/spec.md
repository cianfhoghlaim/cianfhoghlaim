# Spec delta: `agentic-frontend-frameworks`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the new `web/apps/cianfhoghlaim-web/control-panel/` as
the 5th canonical surface (after `cianfhoghlaim-web`, `croilar-web`,
`croilar-portal`, `tuatha-ui`).

## ADDED Requirements

### Requirement: Web UI control panel is registered as the 5th canonical surface

The system SHALL register the new `web/apps/cianfhoghlaim-web/control-panel/`
as the 5th canonical agentic web surface (TanStack Start + Convex +
Hono + oRPC). The 5 surfaces are:

1. `web/apps/cianfhoghlaim-web/` (the public web app)
2. `web/apps/croilar-web/` (multi-persona portfolio)
3. `web/apps/croilar-portal/` (portfolio dashboard)
4. `web/apps/tuatha-ui/` (Túatha educational MMO)
5. `web/apps/cianfhoghlaim-web/control-panel/` (NEW: deployment
   control panel)

#### Scenario: Control panel boots with all 5 routes

- **GIVEN** `web/apps/cianfhoghlaim-web/` configured with the
  control-panel routes
- **WHEN** the operator runs `bun run dev` and navigates to
  `http://localhost:3000/control-panel`
- **THEN** all 5 routes render without error:
  `/control-panel/models`, `/control-panel/pipelines`,
  `/control-panel/datasets`, `/control-panel/stacks`,
  `/control-panel/registry`