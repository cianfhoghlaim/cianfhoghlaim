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

### Requirement: Five follow-up marimo dashboards at notebooks/09_official_media/03..07_*.py

The system SHALL provide 5 follow-up marimo dashboards at
`notebooks/09_official_media/{03..07}_*.py` that
visualise the 5 spec requirements of the `official-media-marimo`
capability. The 5 dashboards SHALL:

1. AST-parse cleanly (no SyntaxError).
2. Pass `uv run marimo check` with no critical issues.
3. Be discoverable via `uv run cianfhoghlaim-marimo list 09_official_media`.
4. Render via `uv run marimo run --headless <file>` without runtime
   failure (the headless server should bind to a port and serve the
   notebook).
5. Read data from `md:cianfhoghlaim_official_media` (MotherDuck + DuckLake
   lakehouse) and fall back gracefully to a synthetic allowlist-derived
   dataset when the lakehouse is unreachable.
6. Each dashboard SHALL render 3–5 altair visualisations
   (`mo.ui.altair_chart` + `alt.Chart`).
7. Each dashboard SHALL invoke at least 1 BAML extractor
   (`b.ClassifyOfficialMedia`) via the `cianfhoghlaim.baml_client`
   package, in a try/except wrapper so missing BAML runtime
   (`USE_LOCAL_SCRAPES=true` mode) does not crash the notebook.

The 5 dashboards are:

- `03_post_trends.py` — R1 timeline: posts per day, posts per platform,
  engagement heatmap (3 panels).
- `04_mention_network.py` — R2 TanStack route preview: source platform,
  mention overlap matrix, top-15 mention pairs (3 panels).
- `05_fediverse_coverage.py` — R3 Cognee dataset edges: 4 edge-type
  counts, fediverse instance distribution, edge direction (3 panels).
- `06_cross_archive.py` — R4 cross-archive + Cloudflare deployment:
  link strength by category, NCCA subject coverage, deployment status
  (3 panels).
- `07_moderation_sentiment.py` — R5 multi-column tabs: sentiment over
  time, moderation flags, sentiment by category, BAML extractor
  (4 tabs via `mo.ui.tabs({...})`).

#### Scenario: All 5 dashboards AST-parse

- **GIVEN** the 5 dashboards exist at
  `notebooks/09_official_media/{03..07}_*.py`
- **WHEN** the user runs `ast.parse(open(f).read())` for each
- **THEN** all 5 files parse without SyntaxError

#### Scenario: All 5 dashboards pass marimo check (no critical)

- **GIVEN** the 5 dashboards exist
- **WHEN** the user runs `uv run marimo check <file>` for each
- **THEN** none of the 5 files report any `critical[...]` issue
  (only non-fatal `warning[general-formatting]` and
  `warning[markdown-indentation]` are acceptable)

#### Scenario: CLI discovery finds the 5 new entries

- **GIVEN** the 5 dashboards exist
- **WHEN** the user runs
  `uv run cianfhoghlaim-marimo list 09_official_media`
- **THEN** the output includes all 5 new entries
  (`03_post_trends.py`, `04_mention_network.py`,
  `05_fediverse_coverage.py`, `06_cross_archive.py`,
  `07_moderation_sentiment.py`) alongside the 2 pre-existing entries

#### Scenario: Dashboard 07 demonstrates the R5 tab layout

- **GIVEN** `07_moderation_sentiment.py` renders
- **WHEN** the user opens the dashboard
- **THEN** the 4 tabs (Sentiment over time, Moderation flags,
  Sentiment by category, BAML extractor) SHALL be visible as a
  horizontal tab bar
- **AND** selecting a tab SHALL switch the content area without a
  full page reload (per the R5 Streamlit-compatible layout contract)

#### Scenario: Dashboard 06 surfaces the R4 Cloudflare deployment

- **GIVEN** `06_cross_archive.py` renders
- **WHEN** the user opens the dashboard
- **THEN** Panel C SHALL surface the R4 Cloudflare deployment status
  (Marimo UI URL from `MARIMO_DEPLOYMENT_URL` env var, Container
  endpoint from `MARIMO_CONTAINER_HOST` + `MARIMO_CONTAINER_PORT`)
- **AND** the canonical default URL SHALL be
  `https://marimo-official-media.cianfhoghlaim.workers.dev`
- **AND** the canonical default Container endpoint SHALL be
  `marimo-official-media.arm1-oci:8080`

### Requirement: Portal marimo cross-reference

The system SHALL cross-reference the `portal-cloudflare-r2` marimo
notebook deployment in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R15 so that future agents looking up the canonical marimo-on-Cloudflare
pattern find both the mission-control and the study-plan examples.

#### Scenario: An agent searches for the canonical marimo pattern

- **WHEN** the agent opens `openspec/specs/official-media-marimo/spec.md`
- **THEN** the `## See also` section MUST link to the leaving-cert-portal
  R15 requirement (marimo notebook deployed to Cloudflare)

