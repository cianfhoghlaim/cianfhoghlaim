## ADDED Requirements

### Requirement: Endpoint health monitoring for the British Isles

The system MUST provide a canonical `endpoint_recovery` helper at
`dlt/common/endpoint_recovery.py` that wraps every British Isles
DLT source's outbound network call. The helper MUST try the
following strategies in order:

1. **Plain HTTP crawl** via `dlt/common/site_crawler.py:crawl_site`
   for endpoints that respond with 200 to a browser User-Agent.
2. **Firecrawl `stealth` proxy** (via the Firecrawl MCP
   `firecrawl_scrape(..., proxy="stealth")`) for endpoints that 403
   to plain HTTP.
3. **Wayback Machine fallback**
   (`https://web.archive.org/web/2024/<url>`) for endpoints that
   403 even with stealth or that time-out.

Every call MUST return a `RecoveredPage` dataclass and emit a
structlog `endpoint_status{status, backend_used}` event.

#### Scenario: NCCA returns 403 to plain HTTP

- **WHEN** `endpoint_recovery.fetch("https://ncca.ie/en/", strategy="auto")`
  returns `status_code=403`
- **THEN** the helper MUST retry with `strategy="stealth"`
- **AND** if stealth returns 200, the helper MUST return that
  result tagged `backend_used="firecrawl_stealth"`
- **AND** if stealth also 403s, the helper MUST retry with the
  Wayback Machine
- **AND** the final returned `RecoveredPage.backend_used` MUST be
  one of `{"direct", "firecrawl_stealth", "wayback", "none"}`

### Requirement: 11 British Isles endpoints recovered

The system MUST recover the following 11 broken endpoints:

| Source | Endpoint | Strategy |
|:--|:--|:--|
| NCCA | `https://ncca.ie` | `stealth` |
| CurriculumOnline | `https://www.curriculumonline.ie` | `stealth` |
| SQA | `https://www.sqa.org.uk/sqa/56983.html` | `firecrawl_map` discovery |
| AQA | `https://www.aqa.org.uk/subjects/gcse` | `firecrawl_map` discovery |
| CCEA | `https://ccea.org.uk` | `stealth` |
| Courts.ie judgements | `https://www.courts.ie/judgements` | URL fix to `/search/judgements` |
| GMC | `https://www.gmc-uk.org` | `stealth` + `wait_for=10s` |
| IoM health | `https://www.gov.im/...` | `stealth` |
| IoM education | `https://www.gov.im/education` | `stealth` |
| Pearson | `https://qualifications.pearson.com/...` | `firecrawl_map` discovery |
| WJEC | `https://www.wjec.co.uk` | `firecrawl_map` discovery |

#### Scenario: All 11 sources are recovered

- **WHEN** `endpoint_recovery.probe_all_39()` runs against the 39
  canonical British Isles endpoints
- **THEN** all 39 endpoints MUST return `status_code ∈ (200, 201, 204)`
- **AND** the 11 previously-broken endpoints MUST report
  `backend_used ∈ {"firecrawl_stealth", "wayback"}`

### Requirement: endpoint_health DuckLake table

The system MUST persist a row per `endpoint_recovery.fetch()` call to
the canonical DuckLake table
`cianfhoghlaim.endpoint_health`. The Dagster L2 asset
`endpoint_health_sink` MUST fire every 6 hours and populate the
table from `endpoint_recovery.probe_all_39()`.

#### Scenario: A new endpoint becomes unhealthy

- **WHEN** one of the 39 canonical endpoints returns a non-200 status
  for 2 consecutive probes
- **THEN** the `endpoint_health_alerts` asset MUST post a Slack alert
  to `#upstream-endpoints` within the next 6-hour window

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella path + source_id contract
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the flagship BIEP spec
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- [`site-crawler`](../site-crawler/spec.md) —
  the canonical site-scraper primitive
- [`upstream-package-monitoring`](../upstream-package-monitoring/spec.md) —
  the parallel monitor for the dlthub / firecrawl / motherduck / lancedb / cocoindex upstream packages
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/firecrawl/SKILL.md` — Firecrawl MCP usage
