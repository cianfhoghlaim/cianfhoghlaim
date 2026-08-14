# web-monorepo-consolidation Specification

## Purpose

Formalize the consolidated `web/` monorepo structure
(4 apps + 3 packages + 1 monorepo workspace) and the
agent-frontend integration pattern.

## ADDED Requirements

### Requirement: web/ SHALL be a single monorepo workspace

The system MUST organize `web/` as a single bun workspaces +
Turbo monorepo with:

- 4 apps: `apps/oideachais/`, `apps/croilar/`,
  `apps/oideachais-dashboard/`, `apps/cianfhoghlaim/`
- 3 packages: `packages/ui-kit/`, `packages/auth/`, `packages/db/`
- 1 canonical Hono API gateway at `web/hono-api/`
- 1 canonical Convex deployment at
  `web/apps/oideachais-dashboard/convex/`
- 1 canonical theme at `web/packages/ui-kit/theme/`

The system MUST provide:

- `web/package.json` (the root workspace manifest)
- `web/turbo.json` (the Turbo config matching root `turbo.json`)
- `web/.gitignore` + `web/tsconfig.base.json` + `web/.npmrc`

#### Scenario: A new web feature spans all 4 apps

- **WHEN** a developer adds a new "Irish language lesson" feature
- **THEN** the feature lives at
  `apps/oideachais/routes/ga/lessons/$lessonId.tsx`
- **AND** the shared UI components live at
  `packages/ui-kit/components/`
- **AND** the auth wiring lives at `packages/auth/`
- **AND** the cross-app theme lives at
  `packages/ui-kit/theme/tokens.css`
- **AND** the developer touches at most 4 directories

### Requirement: Each app MUST have a per-app AGENTS.md

The system MUST ensure every app under `web/apps/<app>/` has its
own `AGENTS.md` following the canonical 6-section outline:

1. Routing sentence (one line: "Load this AGENTS.md when...")
2. Quick start (the canonical 3-5 `bun run` commands)
3. Key sources (the per-app file inventory table)
4. Adjacent specs (the openspec specs that govern this app)
5. DO NOT (3-5 hard rules)
6. Skill pointers (3-5 `.agents/skills/<skill>/SKILL.md` references)

#### Scenario: A new per-app AGENTS.md is added

- **WHEN** a developer adds a new app `apps/cianfhoghlaim/`
- **THEN** an `AGENTS.md` file MUST exist at the app root
- **AND** MUST follow the canonical 6-section outline
- **AND** MUST cross-link `agents/WEB_INTEGRATION.md`

### Requirement: The Hono API gateway MUST be canonical

The system MUST live the single canonical Hono API gateway at
`web/hono-api/`. No app MUST have its own
`apps/<app>/apps/api/src/` directory for CopilotKit actions.

#### Scenario: A new web app adds a CopilotKit action

- **WHEN** a developer adds a new CopilotKit action for
  `apps/oideachais/`
- **THEN** the action file lives at
  `web/hono-api/src/routes/copilotkit/oideachais.ts`
- **AND** the action is exposed at
  `/api/copilotkit/oideachais/<action>`
- **AND** the app's TanStack Start routes call the gateway
  via `fetch('/api/copilotkit/oideachais/<action>')`

### Requirement: The Convex deployment MUST be canonical

The system MUST locate the single canonical Convex deployment at
`web/apps/oideachais-dashboard/convex/`. No app MUST have its
own Convex deployment.

Per-subject tables live in the umbrella schema with an
`app` field filter (`'oideachais'`, `'croilar'`,
`'dashboard'`, `'cianfhoghlaim'`).

#### Scenario: A new per-subject Convex schema is added

- **WHEN** a developer adds a new per-subject Convex schema for
  `mathematics_lc`
- **THEN** the schema lives at
  `web/apps/oideachais-dashboard/convex/lc/mathematics.ts`
- **AND** the schema MUST have `app: 'oideachais'` + `subject: 'mathematics'`
- **AND** all queries MUST filter by `app`

### Requirement: The theme MUST be canonical

The system MUST point the single canonical theme at
`web/packages/ui-kit/theme/`:

- `tailwind.config.ts` (the canonical Tailwind config)
- `tokens.css` (the CSS variable definitions)

Per-app customization lives at `apps/<app>/theme-overrides.ts`
using Tailwind's `extends` mechanism.

#### Scenario: A new app needs custom colors

- **WHEN** a developer adds a new app `apps/cianfhoghlaim/`
- **THEN** the app's `tailwind.config.ts` MUST extend from
  `web/packages/ui-kit/theme/tailwind.config.ts`
- **AND** any per-app overrides live in
  `apps/cianfhoghlaim/theme-overrides.ts`
- **AND** the new app's Tailwind config MUST be at most 20 lines
