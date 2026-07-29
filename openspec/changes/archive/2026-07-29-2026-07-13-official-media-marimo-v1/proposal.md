# Official Media Marimo Dashboards v1

## Why

The `official-media-marimo` capability spec (5 requirements: R1 mission
control, R2 TanStack route, R3 Cognee dataset, R4 Cloudflare deployment,
R5 Streamlit-compatible tab layout) describes the marimo operator surface
for the British Isles government / political / public-service / university
/ emergency-services / intelligence-agency pipeline.

The original marimo surface shipped with the change at
`openspec/changes/archive/2026-06-18-official-media-pipeline/` is a single
notebook (`01_official_media.py`) — the 4-panel mission control (top
metric strip, filterable table, skimmer, HMGCC sentinel). The spec's R1
clause is covered by that notebook, but **R2–R5 are not backed by
marimo dashboards**:

- **R2** (TanStack Start `/official-media` route) is a TanStack concern,
  but the marimo view of the same data is missing.
- **R3** (Cognee `cianfhoghlaim_official_media` dataset) is a Cognify
  concern, but the marimo view of the 4 edge types is missing.
- **R4** (Cloudflare Workers + Container deployment) is a deployment
  concern, but the marimo cross-archive join (official-media × BLPIPA /
  NCCA) is missing.
- **R5** (Streamlit-compatible multi-column tab layout) is a layout
  concern, but the demonstration dashboard is missing.

This change ships **5 follow-up marimo dashboards** at
`notebooks/09_official_media/{03..07}_*.py`, plus the
openspec change artifacts (proposal + tasks + 1 MODIFIED spec delta).

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `notebooks/09_official_media/03_post_trends.py` | NEW (R1 timeline — 3 panels: posts per day, per platform, engagement heatmap) | +~360 |
| `notebooks/09_official_media/04_mention_network.py` | NEW (R2 TanStack route preview — 3 panels: source platform, mention overlap matrix, top-15 mention pairs) | +~345 |
| `notebooks/09_official_media/05_fediverse_coverage.py` | NEW (R3 Cognee dataset edges — 3 panels: 4 edge-type counts, fediverse instance distribution, edge direction) | +~390 |
| `notebooks/09_official_media/06_cross_archive.py` | NEW (R4 cross-archive + deployment — 3 panels: link strength by category, NCCA subject coverage, R4 Cloudflare deployment status) | +~425 |
| `notebooks/09_official_media/07_moderation_sentiment.py` | NEW (R5 multi-column tabs — 4 tabs: sentiment over time, moderation flags, sentiment by category, BAML extractor) | +~390 |
| `openspec/changes/2026-07-13-official-media-marimo-v1/proposal.md` | NEW (this file) | +~120 |
| `openspec/changes/2026-07-13-official-media-marimo-v1/tasks.md` | NEW (6 task groups) | +~120 |
| `openspec/changes/2026-07-13-official-media-marimo-v1/specs/official-media-marimo/spec.md` | NEW (1 ADDED requirement) | +~40 |

Total: 5 dashboards (~1,900 LOC) + 3 change artifacts (~280 LOC).

## Out of scope

- The existing `01_official_media.py` (4-panel mission control) and
  `02_email_inbox_triage.py` (inbox triage) notebooks are NOT touched.
- The 7 `baml/education/lc_extraction/*.baml` files (owned by the BIEP
  v1 change) are NOT modified.
- The `dlt/official_media/` sources (owned by the official-media-pipeline
  spec) are NOT modified.
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  are NOT modified.

## Cross-archive impact

This change ONLY touches:
- `notebooks/09_official_media/03..07_*.py` (5 NEW files)
- `openspec/changes/2026-07-13-official-media-marimo-v1/` (3 NEW files)

No cross-repo sync required (this is a single-repo change scoped to
`cianfhoghlaim`).

## Acceptance gates

- `openspec validate 2026-07-13-official-media-marimo-v1 --strict` passes
- 5 marimo dashboards at `notebooks/09_official_media/03..07_*.py` exist +
  AST-parse cleanly
- `uv run marimo check` returns no critical issues for any of the 5
- `uv run cianfhoghlaim-marimo list 09_official_media` discovers all 5
  (plus the 2 pre-existing notebooks)
- 1 MODIFIED spec delta on `official-media-marimo` is well-formed
- Pushed to `origin/pick-4-biep-v1` (NOT `main`)
