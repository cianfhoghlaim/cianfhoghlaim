# Author-Archive Web Scraping (Firecrawl ↔ Crawl4AI ↔ Stagehand parity)

This spec is the capability matrix for the 5 `sruth_browser` backends
and the credit-budget routing that decides which one runs each call.

## Purpose

The user has 20,000 Firecrawl credits. Naively scraping all 160
official_media sources with Firecrawl would burn ~25,000 credits. This
spec defines the routing rules that bring the cost down to ~322
credits one-time + ~20 credits/month for re-pre-research (a 95%
reduction).

## Capability matrix

| Capability | Firecrawl (paid) | Crawl4AI (free) | Stagehand (free) | CDP (free) | Browserbase (paid) | Z.AI vision (paid) |
|:--|:--|:--|:--|:--|:--|:--|
| `scrape` (markdown) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `extract` (schema) | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `map_site` (sitemap) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **`/agent` (pre-research)** | **✅ only** | ❌ | ❌ | ❌ | ❌ | ❌ |
| `screenshot` | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `visual_grounding` | ❌ | ❌ | ✅ (`observe()`) | ✅ (pixel) | ✅ | ✅ (GLM-4.6v) |
| `interact` (click/type) | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Anti-bot bypass** | ✅ | ❌ | ⚠️ | ❌ | ✅ | ❌ |

The **only capability Firecrawl has exclusively** is `/agent`
(autonomous research) and anti-bot bypass. Everything else can be done
for free by Crawl4AI (bulk) or Stagehand (interactive).

## ADDED Requirements

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

## Credit math (verified)

| Action | Cost | Count | Total |
|:--|:--|:--|:--|
| Pre-research (Firecrawl `/agent`) | 2 credits | 160 sources | 320 |
| Pre-research (free fallback for budget exhaustion) | 0 | ~5 sources | 0 |
| Bulk scrape (Crawl4AI) | 0 | 160 sources × ~1000 pages | 0 |
| Bulk scrape (Firecrawl fallback for `firecrawl-agent` sites) | 1 | ~5 sources × ~100 pages | 500 |
| UI identification (Stagehand `screenshot` + `observe`) | 0 | ~50 sources with UIs | 0 |
| Monthly re-pre-research | 2 | ~10 stale sites | 20 |
| **One-time total** | | | **820** |
| **Year-1 total (with monthly)** | | | **820 + 20×12 = 1,060** |
| **Reserved for academic papers (Stage 5 future)** | | | 5,000-10,000 |
| **Reserved for anti-bot fallbacks** | | | 5,000-10,000 |
| **Headroom** | | | ~5,000-10,000 |

## Cross-references

- `infrastructure/browser/sruth_browser/backends/router.py` — the router
- `infrastructure/browser/sruth_browser/scrape_strategist.py` — the wrapper
- `infrastructure/browser/sruth_browser/credit_budget.py` — the ledger
- `infrastructure/browser/tests/test_scrape_strategist.py` — 24 tests
