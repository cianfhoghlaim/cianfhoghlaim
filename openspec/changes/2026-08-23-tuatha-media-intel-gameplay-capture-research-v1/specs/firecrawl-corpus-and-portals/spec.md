# Spec Delta: firecrawl-corpus-and-portals

## ADDED Requirements

### Requirement: 3-plan Firecrawl ladder with auto-detect of keyless tier

The system SHALL provide 3 Firecrawl plan configurations
(`firecrawl_plan_a_keyless`, `firecrawl_plan_b_paid_basic`,
`firecrawl_plan_c_full`) and SHALL auto-detect the keyless
tier (no `FIRECRAWL_API_KEY` env var) at process start.

The plan definitions SHALL match the canonical
`KEYLESS_TOOLS` set in
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py`:

- **Plan A — keyless**: `firecrawl_search`,
  `firecrawl_scrape`, `firecrawl_parse` only
- **Plan B — paid basic**: adds `firecrawl_map`,
  `firecrawl_crawl`, `firecrawl_batch_scrape`,
  `firecrawl_monitor_create`, `firecrawl_monitor_check`
- **Plan C — full**: adds `firecrawl_agent`,
  `firecrawl_interact`, `firecrawl_research_search_papers`,
  `firecrawl_research_inspect_paper`,
  `firecrawl_developer_search`, `firecrawl_ask`

Every `firecrawl_*` call SHALL be logged to
`cianfhoghlaim.firecrawl_meta.scrapes` per invariant #1.

#### Scenario: A source declares Plan A and the key is absent

- **GIVEN** `source.yaml:firecrawl_plan = "plan_a_keyless"`
- **AND** the `FIRECRAWL_API_KEY` env var is empty
- **WHEN** any agent calls `FirecrawlMCPClient.crawl(...)`
- **THEN** the call SHALL raise a
  `FirecrawlPlanUnavailable` error (the Plan B/C tool is
  not available)
- **AND** the `stedding/ingest_queue/USE_LOCAL_SCRAPES` cache
  is consulted as a substitution

#### Scenario: Plan B is gated by the budget asset

- **GIVEN** `source.yaml:firecrawl_plan = "plan_b_paid_basic"`
- **AND** the `firecrawl_budget_asset` (invariant #6) reports
  the daily budget is exhausted
- **WHEN** any agent calls
  `FirecrawlMCPClient.crawl(...)`
- **THEN** the call SHALL be refused with a
  `FirecrawlBudgetExceeded` error
- **AND** the source SHALL fall back to Plan A
  (`firecrawl_scrape` only)

### Requirement: Per-source `firecrawl_plan` declaration in the DLT source `source.yaml`

The system SHALL require every DLT source that uses Firecrawl
to declare its `firecrawl_plan` in its `source.yaml` manifest
(per the `media-intel-corpus` plugin contract).

The system SHALL refuse to materialise any DLT source that
declares a plan that is not provisioned (e.g. Plan C
declared but only Plan A is available).

#### Scenario: A source declares Plan C but only Plan A is provisioned

- **GIVEN** `source.yaml:firecrawl_plan = "plan_c_full"`
- **AND** only the keyless tier is available
- **WHEN** the DLT source materialises
- **THEN** the materialisation SHALL fail with a
  `FirecrawlPlanUnavailable` error
- **AND** the Dagster sensor SHALL log the failure
- **AND** the operator SHALL be notified via the marimo
  control panel
