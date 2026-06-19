# author-archive-web-scraping Specification

## Purpose
TBD - created by archiving change author-archive-v1. Update Purpose after archive.
## Requirements
### Requirement: Pre-research prefers Firecrawl with credit guard

`BackendRouter.pre_research` SHALL default to Firecrawl `/agent` (the
only backend with autonomous research). The method SHALL charge 2
credits per call (default `budget_hint`). The method SHALL fall back
to a free Crawl4AI sitemap+sample path when the `CreditBudget.has(budget_hint)`
returns `False`. The method SHALL fall back to the free path when the
paid backend raises any exception (the budget is only charged on
success). The method SHALL respect `prefer_free=True` to skip Firecrawl
even when the budget allows it.

#### Scenario: Fresh source with budget available

- **WHEN** `CreditBudget.has(2)` is `True`
- **AND** `prefer_free` is `False` (default)
- **THEN** the method calls Firecrawl `/agent`
- **AND** on success, charges 2 credits
- **AND** returns a `ResearchResult` with `backend_used = FIRECRAWL_MCP`

#### Scenario: Budget exhausted

- **WHEN** `CreditBudget.has(2)` is `False`
- **THEN** the method calls `_free_pre_research()` (Crawl4AI fallback)
- **AND** 0 credits are charged
- **AND** returns a `ResearchResult` with `backend_used = CRAWL4AI_LOCAL`

#### Scenario: Paid backend raises

- **WHEN** the Firecrawl call raises any exception
- **THEN** the method catches it
- **AND** the method's circuit breaker records the failure
- **AND** the method falls back to `_free_pre_research()`
- **AND** 0 credits are charged

#### Scenario: User forces free

- **WHEN** `prefer_free = True`
- **THEN** the method calls `_free_pre_research()` directly
- **AND** 0 credits are charged

### Requirement: Bulk scrape prefers free backends

`BackendRouter.select_backend(SCRAPE)` SHALL prefer the free
`CRAWL4AI_LOCAL` backend. The `ScrapeStrategist.bulk_scrape` method
SHALL use `prefer_free=True` by default. The `FirecrawlBackend` is the
paid fallback used only when:

- The site's `recommended_strategy` is `firecrawl-agent` (heavy JS
  rendering that Crawl4AI cannot handle), OR
- Crawl4AI's circuit breaker has tripped (3 consecutive failures)

#### Scenario: Default scrape

- **WHEN** `prefer_free=True` (default)
- **THEN** the asset uses Crawl4AI
- **AND** 0 credits are charged

#### Scenario: Heavy JS source

- **WHEN** the pre-research `recommended_strategy = "firecrawl-agent"`
- **THEN** the asset uses Firecrawl /scrape
- **AND** 1 credit is charged per page

### Requirement: Map site prefers Crawl4AI

`BackendRouter.map_site` SHALL default to `CRAWL4AI_LOCAL` and only
fall back to `FIRECRAWL_MCP` when `prefer_free=False`.

#### Scenario: Default map

- **WHEN** `prefer_free=True` (default)
- **THEN** the method uses Crawl4AI
- **AND** 0 credits are charged

### Requirement: Visual grounding prefers free `observe()`

`BackendRouter.visual_ground` SHALL default to the free `STAGEHAND_LOCAL`
backend (which calls the `observe()` action on a transient page).
The `ZAI_VISION` paid backend is the last-resort fallback. The
`BrowserbaseBackend` is the middle-tier fallback.

#### Scenario: Default grounding

- **WHEN** Stagehand is registered
- **THEN** the method uses Stagehand `observe()`
- **AND** 0 credits are charged

#### Scenario: Stagehand unavailable

- **WHEN** Stagehand is not registered
- **AND** Z.AI vision is registered
- **THEN** the method uses Z.AI vision
- **AND** Z.AI credits are charged (separate budget from Firecrawl)

### Requirement: Screenshot prefers free CDP/Stagehand

`BackendRouter.screenshot` SHALL default to the cheapest backend that
supports the `SCREENSHOT` operation. Both `CDP_LOCAL` and
`STAGEHAND_LOCAL` are free and listed first in the `BACKEND_PRIORITY`
for `SCREENSHOT`.

#### Scenario: Default screenshot

- **WHEN** Stagehand is registered
- **THEN** the method uses Stagehand `screenshot()`
- **AND** 0 credits are charged

