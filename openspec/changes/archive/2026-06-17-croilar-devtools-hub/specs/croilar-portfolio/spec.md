# Spec Delta: `croilar-portfolio`

## MODIFIED Requirements

### Requirement: 9 Subproject Routes

The system SHALL continue to expose 9 subproject routes at the public root.

#### Scenario: No regression

- **WHEN** a visitor navigates to `/`, `/cv`, `/music`, `/code`, `/research`, `/teaching`, `/data`, `/identity`, or `/contact`
- **THEN** the page SHALL render as before (no UI change from this change)

## ADDED Requirements

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
- **THEN** the page SHALL resolve the slug to a notebook in `sruth/croilar/notebooks/` (or the WASM export under `sruth/croilar/apps/web/public/wasm/`)
- **AND** the page SHALL render the marimo WASM export inline

#### Scenario: Auth gate

- **WHEN** a user without `croilar-admin` org owner|admin role opens `/notebooks`
- **THEN** the page SHALL render an `AccessDenied` component

## MODIFIED Requirements

### Requirement: Image Management

The system SHALL process and serve all images via the croilar-assets R2 bucket + sharp pipeline.

#### Scenario: No regression

- **WHEN** an image is added to `sruth/croilar/web/public/images/`
- **THEN** the build-time sharp pipeline SHALL still compress it and upload to R2

### Requirement: Deployment

The system SHALL deploy `sruth/croilar/web` to Cloudflare Pages.

#### Scenario: No regression

- **WHEN** the build completes
- **THEN** `wrangler pages deploy dist` SHALL still push the static site

### Requirement: PII Handling

The system SHALL encrypt PII (identity documents) at rest using SOPS.

#### Scenario: No regression

- **WHEN** a PDF is added to `sruth/croilar/identity/raw/`
- **THEN** it SHALL still be GPG-encrypted and only the metadata SHALL be committed
