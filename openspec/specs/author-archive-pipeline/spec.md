# author-archive-pipeline Specification

## Purpose
TBD - created by archiving change author-archive-v1. Update Purpose after archive.
## Requirements
### Requirement: Per-source pre-research

The system MUST run the `official_media_pre_research` Dagster asset
exactly once for every source in `oideachais/sources.yaml` with
`kind == "official_media"`, before the bulk-scrape asset for that
source. The pre-research MUST:

- Use the `sruth_browser.BackendRouter.pre_research` method, which
  guards every Firecrawl call with the global `CreditBudget`.
- Charge exactly 2 credits per source per pre-research call (default).
- Fall back to a free Crawl4AI sitemap+sample path when the credit
  budget is exhausted (no exception raised, no asset failure).
- Persist the result to `oideachais.official_media.research_sitemap`
  (LanceDB) keyed by `source_id`.
- Skip any source whose `pre_researched_at` is less than 30 days old
  (idempotent re-runs).

#### Scenario: First run on a fresh source

- **WHEN** the source has no `pre_researched_at` timestamp
- **THEN** the asset calls `BackendRouter.pre_research(url, goal, budget_hint=2)`
- **AND** the asset charges 2 credits to the `CreditBudget`
- **AND** the asset persists the result to `oideachais.official_media.research_sitemap`
- **AND** the asset records `pre_researched_at = now()`

#### Scenario: Idempotent re-run

- **WHEN** the source's `pre_researched_at` is less than 30 days old
- **THEN** the asset skips the source
- **AND** no credits are charged

#### Scenario: Credit budget exhausted

- **WHEN** the `CreditBudget.has(2)` returns `False`
- **THEN** the asset calls `_free_pre_research()` (Crawl4AI fallback)
- **AND** no credits are charged
- **AND** the result is persisted with `backend_used = "crawl4ai_local"`

### Requirement: Bulk scrape with the recommended strategy

The `official_media_bulk_scrape` Dagster asset SHALL use the
`recommended_strategy` field from the pre-research record to pick a
backend:

- `crawl4ai-static` → Crawl4AI (free)
- `firecrawl-agent` → Firecrawl /scrape (1 credit per page)
- `stagehand-interactive` → Stagehand (free, requires login)

For each page, the asset SHALL record `bytes_in` (raw markdown byte
count) and `bytes_out` (the final markdown byte count) so the marimo
dashboard can render the compression ratio.

#### Scenario: Static source

- **WHEN** the pre-research `recommended_strategy = "crawl4ai-static"`
- **THEN** the asset uses Crawl4AI (`prefer_free=True`)
- **AND** 0 credits are charged

#### Scenario: Heavy JS source

- **WHEN** the pre-research `recommended_strategy = "firecrawl-agent"`
- **THEN** the asset uses Firecrawl /scrape
- **AND** 1 credit is charged per page

#### Scenario: Source with login wall

- **WHEN** the pre-research `recommended_strategy = "stagehand-interactive"`
- **THEN** the asset uses Stagehand
- **AND** 0 credits are charged (Stagehand is local)

### Requirement: BAML condensation to critical info

The `official_media_condense` Dagster asset SHALL run the new BAML
`CondenseToCriticalInfo` function on every raw page produced by the
bulk-scrape asset.

#### Scenario: Successful condense

- **WHEN** a raw page has `success=True` and non-empty `markdown`
- **THEN** the asset calls `baml.CondenseToCriticalInfo(markdown, goal, 2048)`
- **AND** the result is persisted to `oideachais.official_media.condensed_pages`

#### Scenario: BAML call fails

- **WHEN** the LiteLLM gateway is unreachable or returns an error
- **THEN** the asset logs a warning
- **AND** the asset continues to the next page
- **AND** the asset run does NOT fail

### Requirement: UI identification + visual grounding

The `official_media_identify_uis` Dagster asset SHALL, for any page that
the BAML `IdentifyUiPatterns` function flags as having a UI:

- Take a screenshot of the page (free via Stagehand `screenshot()` or
  Crawl4AI `/crawl` with `screenshot` format)
- Run the new BAML `VisualGroundingFromScreenshot` function to find
  the element's bounding box in 0-1 normalised image coordinates
- Persist the result to `oideachais.official_media.ui_elements`
  (LanceDB) keyed by `(url, ui_type)`

The asset SHALL handle the case where no free browser backend is
available (skip the page, emit a metadata counter, continue).

#### Scenario: Page with a search box

- **WHEN** `IdentifyUiPatterns` returns `ui_type = "SEARCH_BOX"`
- **THEN** the asset takes a screenshot
- **AND** runs `VisualGroundingFromScreenshot`
- **AND** persists the bounding box to `oideachais.official_media.ui_elements`

#### Scenario: No browser backend available

- **WHEN** no free browser backend is running (e.g. CI without Stagehand)
- **THEN** the asset skips the page
- **AND** emits `screenshots_taken` and `uis_identified` counters
- **AND** the asset run does NOT fail

### Requirement: Credit ledger visibility

The marimo dashboard SHALL surface a "Credit usage" widget that shows:

- Total budget (default 20,000, overridable via `BROWSER_FIRECRAWL_BUDGET`)
- Used credits
- Remaining credits
- Per-backend burndown (`firecrawl_mcp`, `zai_vision`, etc.)

The data source is the global `sruth_browser.credit_budget.CreditBudget`
singleton, accessible via `get_budget().get_summary()`.

#### Scenario: Budget healthy

- **WHEN** `used < 0.5 * total`
- **THEN** the widget shows green status

#### Scenario: Budget half-spent

- **WHEN** `used >= 0.5 * total`
- **THEN** the widget shows amber status

#### Scenario: Budget nearly spent

- **WHEN** `used >= 0.9 * total`
- **THEN** the widget shows red status
- **AND** recommends enabling `prefer_free=True` for new sources

### Requirement: Source provenance in the marimo dashboard

The system MUST include a "Source provenance" tab in the
`oideachais.notebooks.dashboards.official_media.official_media`
marimo notebook. The tab MUST show, for every source:

- The 2-3 sentence `site_structure_summary` from the pre-research record
- The `recommended_strategy` value
- The `backend_used` for the most recent bulk-scrape
- The `bytes_in` / `bytes_out` / `compression_ratio` for the most
  recent condense
- A link to the raw `CondensedPage` record

#### Scenario: User opens the Source provenance tab

- **WHEN** the user clicks the "Source provenance" tab in the marimo notebook
- **THEN** the table shows one row per source with: site_structure_summary,
  recommended_strategy, backend_used, bytes_in, bytes_out, compression_ratio

### Requirement: CPS.gov.uk hero example

The script `oideachais/scripts/pre_research_cps_gov_uk.py` SHALL run
all 4 stages on `https://www.cps.gov.uk` and persist the result to
`/tmp/author_archive_cps_gov_uk.json`. The script SHALL be runnable
with no Firecrawl key (it falls back to the free path) and SHALL
print a credit summary at the end.

#### Scenario: Script run with Firecrawl key

- **WHEN** the Firecrawl API key is set
- **THEN** Phase 1 (pre-research) uses the `firecrawl_mcp` backend
- **AND** 2 credits are charged
- **AND** the output JSON contains `backend_used = "firecrawl_mcp"`

#### Scenario: Script run without Firecrawl key

- **WHEN** no Firecrawl API key is set
- **THEN** Phase 1 falls back to the `crawl4ai_local` backend
- **AND** 0 credits are charged
- **AND** the output JSON contains `backend_used = "crawl4ai_local"`

### Requirement: Sample sources cover all 10 official_media categories

The `OFFICIAL_MEDIA_SAMPLE_SOURCES` list in `scraping_assets.py` SHALL
include at least one source from each of the 10 official_media
categories (intelligence, universities, Celtic colleges, schools,
language projects, parties, police, defence, national info,
jurisdictions). The CPS.gov.uk entry counts as a `jurisdictions`
sample.

#### Scenario: All 10 categories present

- **WHEN** the CI runs the `official_media_pre_research` asset
- **THEN** at least 17 sources are attempted
- **AND** each of the 10 categories has at least one sample source

