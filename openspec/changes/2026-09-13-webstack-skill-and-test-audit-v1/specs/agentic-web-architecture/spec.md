## ADDED Requirements

### Requirement: Web Stack Health Detection

The system SHALL keep the web stack inventory auditable: 14 web apps
under `web/apps/`, the 48 Hono API routes, the 4 CopilotKit route
mounts (lc, jc, a-level, gcse), and the A2UI surface generator.

#### Scenario: Hono API has ≥ 30 route files

- **WHEN** any developer runs `uv run pytest tests/webstack/`
- **THEN** `web/hono-api/src/routes/**/*.ts` contains ≥ 30 .ts files
- **AND** the 4 CopilotKit stage directories (lc, jc, a-level, gcse) exist

#### Scenario: A2UI surface generator is present

- **WHEN** any developer runs `uv run pytest tests/webstack/`
- **THEN** `web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx` exists
- **AND** the file exports the `A2UISurfaceGenerator` component

#### Scenario: 4 canonical web apps exist

- **WHEN** any developer runs `uv run pytest tests/webstack/`
- **THEN** the following apps exist under `web/apps/`:
  - `cianfhoghlaim-web/`
  - `croilar-web/`
  - `croilar-portal/`
  - `tuatha-ui/`

#### Scenario: agentic-frontend-frameworks skill exists

- **WHEN** any developer runs `uv run pytest tests/webstack/`
- **THEN** `.agents/skills/agentic-frontend-frameworks/SKILL.md` exists

#### Scenario: Web is a workspace

- **WHEN** the web/ root is inspected
- **THEN** either `pnpm-workspace.yaml` exists OR `package.json` has a
  `"workspaces"` field
