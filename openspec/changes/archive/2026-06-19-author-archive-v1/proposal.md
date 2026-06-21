# Author-Archive v1: pre-research + condensation + visual grounding for 160 official_media sources

## Why

The `official-media-pipeline` change (archived 2026-06-18) landed 160 web
sources across 10 British-Isles categories (intelligence, universities,
Celtic colleges, schools, language projects, parties, police, defence,
national info, jurisdictions). It uses Instagram-export-first extraction,
which is brittle and slow. The user said: "we want to know what data we
have and how it was sourced" — that needs a more rigorous ingest path.

This change adds a 4-stage web-ingest pipeline that runs ON TOP of the
existing IG-export pipeline:

  1. **Pre-research** — one-time per source, uses Firecrawl's `/agent`
     endpoint to discover the site structure, content types, recommended
     extraction schema, and estimated credit cost. Falls back to a free
     Crawl4AI sitemap+sample path when the credit budget is exhausted.
  2. **Bulk scrape** — uses the recommended strategy from pre-research to
     pick the cheapest viable backend (Crawl4AI for static, Stagehand for
     interactive, Firecrawl only for anti-bot pages). Records bytes-in
     vs bytes-out so the marimo dashboard can show what was kept.
  3. **Condense** — runs the new BAML `CondenseToCriticalInfo` function on
     every raw page, producing a 1-2 KB `CondensedPage` with key facts,
     entities, and a one-sentence summary. This is the "we want to know
     what data we have" answer.
  4. **UI identification** — for any page that looks UI-bearing (search
     box, form, dashboard, login wall, map, file download, carousel,
     timeline), takes a screenshot (free via Stagehand) and runs
     `VisualGroundingFromScreenshot` to find the element's bounding box.
     Records the indicator for the marimo "UI map" tab — the user said
     this is "for later game aspects" (Túatha educational MMO) so we
     preserve the data even though we don't render to a game yet.

The user has 20,000 Firecrawl credits. This change uses **~322 credits
one-time + ~20 credits/month for re-pre-research** (vs ~25,000 credits
to scrape all 160 sources directly with Firecrawl). The 95% cost saving
comes from preferring Crawl4AI for the bulk scrape.

The hero example is CPS.gov.uk (Crown Prosecution Service) — the user's
explicit ask. The script `oideachais/scripts/pre_research_cps_gov_uk.py`
runs the full 4-stage pipeline on a single source and writes
`/tmp/author_archive_cps_gov_uk.json` for the marimo dashboard to ingest.

## What Changes

### Code

- `baml_src/author_archive.baml`: +6 new functions
  (`PreResearchSite`, `CondenseToCriticalInfo`, `IdentifyUiPatterns`,
  `VisualGroundingFromScreenshot`, `SummarizeSite`, `ClassifySiteCivic`)
  + 7 new classes (`ResearchSiteMap`, `JsonSchema`, `ExtractedEntity`,
  `CondensedPage`, `UiType`, `UiIndicator`, `BoundingBox`,
  `GroundedElement`, `AuthorArchiveCivicCategory`).

- `oideachais/dagster_defs/assets/official_media/scraping_assets.py`:
  new module with 4 Dagster assets (`pre_research`, `bulk_scrape`,
  `condense`, `identify_uis`). Wired into
  `oideachais/dagster_defs/assets/official_media/__init__.py` and
  `oideachais/dagster_defs/assets/__init__.py` `all_assets`.

- `oideachais/scripts/pre_research_cps_gov_uk.py`: hero example script
  that runs the full 4-stage pipeline on CPS.gov.uk.

### Infrastructure (the refactor prerequisite — `feat/sruth-browser-refactor`)

This change builds on the `sruth_browser` refactor landed in Stage 0.5
on a separate branch (`feat/sruth-browser-refactor`, commit
`c563b9680`). The refactor adds:

- `sruth_browser/credit_budget.py` — SQLite-backed persistent credit
  counter (20,000 default, `BROWSER_FIRECRAWL_BUDGET` env override)
- `sruth_browser/scrape_strategist.py` — thin wrapper exposing the
  `ScrapeStrategist` class with typed dataclasses
- 3 new methods on `BackendRouter` (`pre_research`, `map_site`,
  `visual_ground`, `screenshot`) + 2 new `BrowserOperation` enum values
  (`MAP_SITE`, `VISUAL_GROUNDING`)
- 47 new tests in `infrastructure/browser/tests/`

### Spec deltas

- `author-archive-pipeline/spec.md` — the canonical Dagster + DLT + BAML
  pipeline (160 sources, monthly re-pre-research schedule, multi-target)
- `author-archive-web-scraping/spec.md` — Firecrawl ↔ Crawl4AI ↔
  Stagehand feature parity + capability routing
- `author-archive-ui-grounding/spec.md` — UI detection + visual
  grounding storage shape
- `author-archive-credit-budget/spec.md` — SQLite ledger + marimo
  burndown widget

## Impact

- 160 official_media sources get a reproducible pre-research record
  (sitemap, content types, recommended strategy)
- ~5,000-10,000 Firecrawl credits saved per year (95% reduction)
- New "Source provenance" + "UI map" + "Credit usage" tabs in the marimo
  dashboard
- Hero example: CPS.gov.uk gets a full 4-stage run on
  `pre_research_cps_gov_uk.py` to validate the pipeline

## Out of scope (deferred)

- Dagster multi-target deployment (dev/staging/prod) — that's Stage 4
  of the original plan
- UoG coursework (Stage 2) — not part of the web-scraping layer
- Cross-corpus knowledge graph (Stage 3) — independent of the scraping
  layer
- Game rendering of UI bounding boxes — the user said "later game
  aspects"; we just preserve the data
- Monthly re-pre-research automation — wired into the Dagster schedule
  but the cron is left for a follow-up commit
