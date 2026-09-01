## ADDED Requirements

### Requirement: The Cianfhoghlaim web layer MUST be a single TanStack Start app

The Cianfhoghlaim agentic-frontend-frameworks capability MUST be
backed by a single TanStack Start app at
`web/apps/cianfhoghlaim-nua/` (was previously 5 fragmented apps:
`cianfhoghlaim` + `oideachais` + `oideachais-dashboard` + `tuatha`
+ `croilar-web`).

The consolidated app MUST depend on the canonical
`@cianfhoghlaim/a2ui` package (Phase 2) for the A2UI v0.9
catalog + the canonical `web/hono-api/` Hono API for the
chat-with-syllabus endpoints + the canonical
`web/packages/db/convex/schema.ts` Convex schema (Phase 1's 5
new tables: `study_plans` + `quest_packs` + `oral_study_plans`
+ `formative_attempts` + `audio_segments`).

#### Scenario: A new web route is added to the consolidated app

- **WHEN** a developer adds a new route file to
  `web/apps/cianfhoghlaim-nua/routes/<route_group>/<route>.tsx`
- **THEN** the TanStack Start file-based routing auto-discovers
  it
- **AND** the route is accessible at the corresponding URL
- **AND** the route can consume the canonical A2UI catalog from
  `@cianfhoghlaim/a2ui`

### Requirement: Route groups MUST be organised by audience

The consolidated app MUST organise its routes into 6 audience-
specific route groups per the
`2026-09-01-cianfhoghlaim-nua-web-consolidation-v1` change:

1. `(student)` — the LC + JC + GCSE + A-Level subject surface
2. `(educator)` — the NCCA / NCCE learning graphs + pedagogy
   overlays + equivalencies
3. `(researcher)` — the BIEP v3 dashboards + marimo embeds +
   RAG playground
4. `(author)` — the CV + identity + music + teaching + code
   surface (was croilar-web)
5. `(mmo)` — the British Isles Formative Assessment MMO
   (was tuatha/)
6. `(admin)` — the deployment control panel + model registry
   + cost dashboards (was oideachais-dashboard/)

Each route group MUST be prefixed with the literal audience
name in parentheses per TanStack Start's file-based routing
convention (`(student)/`, `(educator)/`, etc.).

#### Scenario: A route file is placed under the wrong route group

- **WHEN** a developer adds `routes/(student)/lc/chemistry.tsx`
  to the consolidated app
- **THEN** the route is reachable at `/lc/chemistry`
- **AND** the route is NOT reachable via `/admin/lc/chemistry`
  (wrong route group)

### Requirement: Old apps MUST be archived to `web/apps/_archive/`

The 5 old apps MUST be archived to `web/apps/_archive/` (NOT
deleted) for 1 release cycle per the `retrospective-cleanup`
spec. The archive directory MUST preserve the full source tree
of each old app.

After 1 release cycle, the archived apps MUST be deleted (a
follow-on openspec change).

#### Scenario: A user visits an old app URL during the deprecation window

- **WHEN** a user visits `https://cianfhoghlaim.ie/oideachais/lc/chemistry`
  (the old oideachais URL)
- **THEN** the consolidated app's `notFoundComponent` SHALL
  redirect to the canonical Phase 3 URL
  `/lc/chemistry` (or display a deprecation notice + canonical
  URL)

### Requirement: The consolidated app MUST depend on `@cianfhoghlaim/a2ui`

The consolidated app's `package.json` MUST include
`"@cianfhoghlaim/a2ui": "workspace:*"` as a dependency. The
canonical A2UI catalog (`createCatalog()`) MUST be mounted in the
app's `<CopilotKit>` provider.

#### Scenario: The consolidated app mounts the A2UI catalog

- **WHEN** the host app wraps the root layout with
  `<CopilotKitProvider>{createCatalog()}</CopilotKitProvider>`
- **THEN** the 11 canonical A2UI components from
  `@cianfhoghlaim/a2ui` are available to all routes
- **AND** the A2UI catalog emits `data-a2ui-catalog-id="https://cianfhoghlaim.ie/a2ui/catalogs/cianfhoghlaim-nua-v1.json"`
  as the canonical catalog URL