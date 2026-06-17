# `croilar-portfolio` capability spec

## Purpose

`croilar-portfolio` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

The personal-portfolio subproject for Cian. Public TanStack Start site with 9 subprojects (Home, CV, Music, Code, Research, Teaching, Data, Identity, Contact) — bilingual (English + Irish) — served from Cloudflare Pages + R2.
## Requirements
### Requirement: 9 Subproject Routes
The system SHALL expose 9 subproject routes at the public root.

#### Scenario: Home route renders
- **WHEN** a visitor navigates to `/`
- **THEN** the home page SHALL render with name, photo, hero tagline, and links to all 9 subprojects
- **AND** the page SHALL be in English by default with an `ga` alternate

#### Scenario: CV route renders
- **WHEN** a visitor navigates to `/cv`
- **THEN** the CV page SHALL render sections for Education, Awards, Publications, References, Teaching, all extracted from BAML schemas over the source PDFs in `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/achievement/` and `teaching/`
- **AND** the page SHALL include a semantic search input over the extracted Markdown

#### Scenario: Music route renders
- **WHEN** a visitor navigates to `/music`
- **THEN** the music page SHALL render embedded Spotify/SoundCloud/YouTube players for the artist's catalogue
- **AND** the page SHALL show audio analytics (tempo, energy, danceability) extracted via BAML from DLT pipelines

#### Scenario: Code route renders
- **WHEN** a visitor navigates to `/code`
- **THEN** the code page SHALL render the GitHub repos for `@Yedya` sorted by stars + last-updated

#### Scenario: Research route renders
- **WHEN** a visitor navigates to `/research`
- **THEN** the research page SHALL render outputs cross-linked from `oideachais/` and `meaisínfhoghlaim/`, filtered by author "Cian de Búrca"
- **AND** the page SHALL link back to the originating monorepo subproject

#### Scenario: Teaching route renders
- **WHEN** a visitor navigates to `/teaching`
- **THEN** the teaching page SHALL render placements, student feedback, and curriculum designed, all extracted via BAML from teaching PDFs

#### Scenario: Data route renders
- **WHEN** a visitor navigates to `/data`
- **THEN** the data page SHALL render the live status of all 12+ Dagster pipeline assets (via Dagster GraphQL API)
- **AND** the page SHALL include links to the Dagster UI (private Pangolin resource)

#### Scenario: Identity route renders
- **WHEN** a visitor navigates to `/identity`
- **THEN** the identity page SHALL render verification metadata (Pangolin-protected)
- **AND** PII documents SHALL NOT be served — only their verification metadata
- **AND** the page SHALL require Pocket ID OIDC authentication

#### Scenario: Contact route renders
- **WHEN** a visitor navigates to `/contact`
- **THEN** the contact page SHALL render an end-to-end encrypted contact form
- **AND** form submissions SHALL be HMAC-signed and sent to a Hono Worker on Cloudflare

### Requirement: Image Management

The system SHALL process and serve all images via the croilar-assets R2 bucket + sharp pipeline.

#### Scenario: No regression

- **WHEN** an image is added to `croilar/web/public/images/`
- **THEN** the build-time sharp pipeline SHALL still compress it and upload to R2

### Requirement: Deployment

The system SHALL deploy `croilar/web` to Cloudflare Pages.

#### Scenario: No regression

- **WHEN** the build completes
- **THEN** `wrangler pages deploy dist` SHALL still push the static site

### Requirement: PII Handling

The system SHALL encrypt PII (identity documents) at rest using SOPS.

#### Scenario: No regression

- **WHEN** a PDF is added to `croilar/identity/raw/`
- **THEN** it SHALL still be GPG-encrypted and only the metadata SHALL be committed

### Requirement: Live Data Binding

The system SHALL replace the three hard-coded mock data sources in the portal with live Convex subscriptions.

#### Scenario: /data/pipelines is live

- **WHEN** a user opens `/data/pipelines`
- **THEN** the page SHALL call `useQuery(api.pipelines.list, {})` and render the live Dagster asset list
- **AND** the data SHALL be grouped by `assetGroupName`
- **AND** there SHALL be no `mockPipelines` array in the source

#### Scenario: /monitoring/logs is live

- **WHEN** a user opens `/monitoring/logs`
- **THEN** the page SHALL call `useQuery(api.convexFunctionCalls.tail, { limit: 200 })` and render the recent Convex action calls
- **AND** the data SHALL be filterable by project, function, and ok/error
- **AND** there SHALL be no `mockLogs` array in the source

#### Scenario: /monitoring/metrics is live

- **WHEN** a user opens `/monitoring/metrics`
- **THEN** the page SHALL call `useQuery(api.convexMetrics.get, { scope: "global" })` and render p50, p95, qps, and error_rate
- **AND** there SHALL be a per-project drill-down that switches `scope` to `project:<id>`
- **AND** there SHALL be no `mockMetrics` array in the source

### Requirement: Per-Project Web View

The system SHALL expose a `/web` portal page that shows the web-stack inventory for each project.

#### Scenario: Project picker

- **WHEN** a user opens `/web`
- **THEN** the page SHALL show 4 tiles: `tuatha`, `oideachais`, `croilar`, `meaisínfhoghlaim`
- **AND** each tile SHALL show route count, Convex function count, BAML schema count, and latest test status

#### Scenario: Per-project view

- **WHEN** a user opens `/web/$project`
- **THEN** the page SHALL show 6 sections: routes, Convex functions, BAML schemas, test runs, Cloudflare, marimo notebooks
- **AND** each section SHALL be backed by the corresponding Convex module (`tanstackRoutes`, `convexFunctions`, `bamlSchemas`, `testRuns`, `cloudflareResources`, `marimoNotebooks`)
- **AND** each row SHALL have a "troubleshoot" button that opens a side drawer

#### Scenario: Troubleshoot drawer

- **WHEN** a user clicks the "troubleshoot" button on any row
- **THEN** a side drawer SHALL open showing:
  - Source code link (deep link to GitHub)
  - Related Convex functions (by file path overlap)
  - Related BAML schemas (by class/function name overlap)
  - Related marimo notebooks (by topic)
  - Recent test runs touching that file

#### Scenario: Auth gate

- **WHEN** a user without `croilar-admin` org owner|admin role opens `/web` or `/web/$project`
- **THEN** the page SHALL render an `AccessDenied` component
- **AND** the underlying Convex queries SHALL also reject unauthorized callers (defense in depth)

### Requirement: Notebooks View

The system SHALL expose a `/notebooks` portal page that lists marimo notebooks across the monorepo and renders them inline.

#### Scenario: Notebook grid

- **WHEN** a user opens `/notebooks`
- **THEN** the page SHALL show a card grid from `marimoNotebooks`
- **AND** each card SHALL show the notebook title, description, project, and cell count

#### Scenario: Inline WASM render

- **WHEN** a user opens `/notebooks/$slug`
- **THEN** the page SHALL resolve the slug to a notebook in `croilar/notebooks/` (or the WASM export under `croilar/apps/web/public/wasm/`)
- **AND** the page SHALL render the marimo WASM export inline

#### Scenario: Auth gate

- **WHEN** a user without `croilar-admin` org owner|admin role opens `/notebooks`
- **THEN** the page SHALL render an `AccessDenied` component

