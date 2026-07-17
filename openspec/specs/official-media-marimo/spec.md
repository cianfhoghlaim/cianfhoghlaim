# official-media-marimo Specification

## Purpose

`official-media-marimo` is a capability of the Cianfhoghlaim platform.
It is the **primary manual surface** for the `official-media-pipeline`
data + the operator-facing **TanStack Start `/official-media` route**.
The marimo mission control provides:

- A chronological timeline view of all enriched official-media records
- A side-by-side identity comparison (the 4-lookup resolver results)
- A strong-stance footer card with the government organisation's
  policy positions, verified via the BAML `ClassifyOfficialMedia`
  extraction
- A Cognee dataset `cianfhoghlaim_official_media` with 4 edge types joining
  the records to other leabharlann corpora

The corresponding source code lives at:

- `cianfhoghlaim/notebooks/dashboards/official_media/official_media.py`
- `cianfhoghlaim/web/apps/cianfhoghlaim-web/src/routes/official-media/`
- `cianfhoghlaim/cognify/datasets/cianfhoghlaim_official_media.py`
## Requirements
### Requirement: OfficialMediaMissionControl

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/dashboards/official_media.py` that renders the
resolved official-media records as a single-page mission control.

#### Scenario: Dashboard renders

- **GIVEN** `cianfhoghlaim.official_media.candidates` has at least 1 row
- **WHEN** `marimo edit cianfhoghlaim/notebooks/dashboards/official_media.py`
  is run
- **THEN** the notebook SHALL render with:
  - a top metric strip (total candidates, total resolved, freshness
    histogram, category stacked bar)
  - a filterable table (category × jurisdiction × resolved_at)
  - a "skimmer" right pane with the last N Wikipedia summary updates
    (each row has deep-link buttons to the official website, Mastodon,
    Bluesky, and Companies House filing)
  - a "HMGCC co-creation" sentinel sub-section that surfaces the last
    12 weeks of co-creation project calls
  - a strong-stance footer card reading **"Why we built this →"**
    linking to `openspec/changes/official-media-pipeline/proposal.md`

#### Scenario: Empty state handled

- **GIVEN** `cianfhoghlaim.official_media.candidates` is empty
- **WHEN** the notebook is opened
- **THEN** it SHALL render an empty-state message: *"No official-media
  candidates yet. Run `dagster materialise -a official_media_extract`
  to populate."*
- **AND** the strong-stance footer SHALL still be visible

### Requirement: OfficialMediaTanStackRoute

The system SHALL provide a TanStack Start route at
`cianfhoghlaim/web/src/routes/official-media/index.tsx` that exposes the
same data with a card-grid layout grouped by `category`.

#### Scenario: Card grid renders

- **GIVEN** the FastAPI endpoint `GET /api/official-media/candidates`
  returns at least 1 row
- **WHEN** the user navigates to `/official-media`
- **THEN** the page SHALL render a card grid grouped by `category`
- **AND** each card SHALL have a *"Follow on Fediverse"* button that
  opens the resolved Mastodon/Bluesky URL
- **AND** the strong-stance footer SHALL be visible at the bottom of
  the page

#### Scenario: Upload from Instagram export

- **GIVEN** the user selects a valid Instagram export `.zip` file
- **WHEN** they click the **"Add from Instagram export"** button
- **THEN** a `POST /api/official-media/upload` request SHALL be sent
  with the zip file
- **AND** a progress indicator SHALL show the job id
- **AND** the page SHALL poll `GET /api/official-media/jobs/{id}` and
  re-render the grid when the job completes

### Requirement: OfficialMediaCogneeDataset

The system SHALL register a Cognee dataset named
`cianfhoghlaim_official_media` with the following edge types:

- `ig_profile → official_website`
- `ig_profile → fediverse_account`
- `ig_profile → companies_house_entity`
- `official_website → wikipedia_article` (bi-directional)

#### Scenario: Cognify registers the dataset

- **GIVEN** the `official_media_cognify` Dagster asset has been
  materialised
- **WHEN** the Cognee web UI is opened at
  `https://cognee.cianfhoghlaim.ie`
- **THEN** the dataset `cianfhoghlaim_official_media` SHALL appear in the
  dataset list
- **AND** querying `MATCH (p:ig_profile)-[:has_official_website]->(w:url)
  RETURN p.ig_username, w.url LIMIT 10` SHALL return at least 1 row

### Requirement: Marimo on Cloudflare deployment (KCG)

The system SHALL use the marimo-on-Cloudflare Workers + Container
pattern as the canonical deployment for production marimo
dashboards in the official-media surface.

#### Scenario: Worker + Container deploys

- **GIVEN** the canonical Dockerfile + wrangler.jsonc + Durable
  Object pattern from `.agents/skills/marimo/references/deployment-cloudflare.md`
- **WHEN** the official-media mission-control marimo is deployed
- **THEN** the marimo UI SHALL be served from a `*.workers.dev`
  URL
- **AND** the Container SHALL be reachable at TCP 8080 for
  marimo's internal RPC

### Requirement: Streamlit-compatible layout in marimo

The system SHALL support a multi-column `mo.ui.tabs({...})` layout
in the official-media mission control so the page renders
correctly for both narrow and wide viewports.

#### Scenario: Tab layout renders

- **GIVEN** a marimo cell with
  `mo.ui.tabs({"Candidates": ..., "Skimmer": ..., "HMGCC": ...})`
- **WHEN** the user opens the dashboard on a 1024×768 viewport
- **THEN** the tabs SHALL be visible as a horizontal tab bar
- **AND** selecting a tab SHALL switch the content area without
  a full page reload

