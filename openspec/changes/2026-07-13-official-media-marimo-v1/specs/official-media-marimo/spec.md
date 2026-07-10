## ADDED Requirements

### Requirement: Five follow-up marimo dashboards at notebooks/09_official_media/03..07_*.py

The system SHALL provide 5 follow-up marimo dashboards at
`cianfhoghlaim/notebooks/09_official_media/{03..07}_*.py` that
visualise the 5 spec requirements of the `official-media-marimo`
capability. The 5 dashboards SHALL:

1. AST-parse cleanly (no SyntaxError).
2. Pass `uv run marimo check` with no critical issues.
3. Be discoverable via `uv run cianfhoghlaim-marimo list 09_official_media`.
4. Render via `uv run marimo run --headless <file>` without runtime
   failure (the headless server should bind to a port and serve the
   notebook).
5. Read data from `md:oideachais_official_media` (MotherDuck + DuckLake
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
  `cianfhoghlaim/notebooks/09_official_media/{03..07}_*.py`
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
