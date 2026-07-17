# `site-crawler` Specification

## Purpose

`site-crawler` is a capability of the Cianfhoghlaim platform. It is
the canonical 3-way web-scraper primitive that backs every `dlt` source
in the Cianfhoghlaim platform that scrapes or crawls a remote website
(NCCA, SEC, gov.ie circulars, citizensinformation.ie, hse.ie, nice.org.uk,
etc.). It supersedes the three overlapping pre-existing primitives
(`dlt/common/firecrawl_source.py`, `dlt/common/incremental.py:crawl_source`,
`dlt/british_isles/ireland/education/curriculum.py:_crawl_source`).

The corresponding source code lives at `cianfhoghlaim/dlt/common/site_crawler.py`.

## Requirements

### Requirement: The system SHALL provide a single canonical 3-way web-scraper primitive at `dlt/common/site_crawler.py`

The `site-crawler` primitive MUST expose one public API with three entry
points:

```python
from cianfhoghlaim.dlt.common.site_crawler import (
    scrape_url,      # single-page scrape
    crawl_site,      # discover + batch-scrape URLs from a base URL
    map_urls,        # discover URLs without scraping
    CrawledPage,    # typed result dataclass
)
```

The 3 backend tiers MUST resolve in the following priority order, with
the first available backend winning:

1. **`BrowserClient`** (self-hosted, `$0` cost) — when the
   `BROWSER_API_URL` env var is set
2. **`FirecrawlApp`** (paid API fallback) — when the `FIRECRAWL_API_KEY`
   env var is set
3. **Local scrape cache** (`stedding/ingest_queue/<source_key>/`) — when
   `USE_LOCAL_SCRAPES=true` (the AGENTS.md "Respect the Ingestion Cache"
   rule)

#### Scenario: BrowserClient is selected when `BROWSER_API_URL` is set

- **GIVEN** the `BROWSER_API_URL=http://browser.cianfhoghlaim.ie` env var
  is set in the deployment
- **WHEN** a DLT source calls `crawl_site("https://example.gov.ie")`
- **THEN** the primitive uses the BrowserClient for both `discover_site`
  + `batch_scrape`
- **AND** the returned `CrawledPage` rows have `backend="browser"`
- **AND** the implementation NEVER falls back to Firecrawl when the
  BrowserClient raises an exception (it instead raises the exception
  to the caller)

#### Scenario: Firecrawl is the fallback when only the API key is set

- **GIVEN** `BROWSER_API_URL` is unset and `FIRECRAWL_API_KEY` is set
- **WHEN** a DLT source calls `crawl_site("https://example.gov.ie")`
- **THEN** the primitive uses `FirecrawlApp.crawl_url` for the crawl
- **AND** the returned `CrawledPage` rows have `backend="firecrawl"`

#### Scenario: Local scrape cache is the offline fallback

- **GIVEN** `USE_LOCAL_SCRAPES=true` is set in the dev environment
- **WHEN** a DLT source calls `crawl_site("https://example.gov.ie")`
- **THEN** the primitive reads from
  `stedding/ingest_queue/example.gov.ie/<path>.json` and yields one
  `CrawledPage` per cached file
- **AND** the rows have `backend="local_cache"`
- **AND** no network calls are made

### Requirement: The 3 pre-existing crawler helpers MUST emit a `DeprecationWarning` and re-export from `site_crawler.py`

The legacy helpers MUST remain importable to give existing call sites a
deprecation window:

* `dlt/common/firecrawl_source.py:crawl_website` — re-exports
  `site_crawler.crawl_site`
* `dlt/common/incremental.py:crawl_source` — re-exports
  `site_crawler.crawl_site`
* `dlt/british_isles/ireland/education/curriculum.py:_crawl_source` —
  re-exports `site_crawler.crawl_site`

All 3 MUST emit a `DeprecationWarning` on first import that points at
the new canonical import path.

#### Scenario: Legacy import emits a deprecation warning

- **GIVEN** an existing DLT source does
  `from cianfhoghlaim.dlt.common.incremental import crawl_source`
- **WHEN** the module is imported
- **THEN** Python emits a `DeprecationWarning` with the text
  `... use cianfhoghlaim.dlt.common.site_crawler.crawl_site instead`
- **AND** the `crawl_source` symbol resolves to the same function as
  `site_crawler.crawl_site`

### Requirement: DLT sources MUST NOT import `_crawl_source` across packages

The pre-existing pattern of importing the leading-underscore `_crawl_source`
helper from `dlt/british_isles/ireland/education/curriculum.py` into other
packages (e.g., `dlt/british_isles/ireland/law/citizensinformation.py`)
MUST be replaced with `from cianfhoghlaim.dlt.common.site_crawler import
crawl_site`.

#### Scenario: No cross-package private-helper imports

- **WHEN** `git grep "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source"`
  is run
- **THEN** the only matches are inside a deprecation comment in
  `curriculum.py` itself
- **AND** no other DLT source imports the private helper

### Requirement: The cocoindex-conformance CI gate MUST run on every PR

A new GitHub Actions workflow at
`.github/workflows/cocoindex-conformance.yaml` MUST run on every push to
main + every PR open/synchronize. The workflow MUST execute:

1. `uv run python cianfhoghlaim/dlt/common/cocoindex_v1_migrate.py --check-only`
   with `continue-on-error: false` (the hard R1+R2+R3+R4 gate)
2. `openspec validate --strict --changes` with `continue-on-error: true`
   (informational — the v4-drift remediation may need to land first)

#### Scenario: PR fails the conformance check

- **GIVEN** a PR adds a new CocoIndex v1 flow that fails R4 (missing
  `declare_vector_index`)
- **WHEN** the CI workflow runs
- **THEN** the conformance check exits 1
- **AND** the PR-comment bot posts the per-flow violation table on the PR
- **AND** the merge button is blocked (the workflow is a required check)

## Cross-references

- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — the parent DLT spec that
  the `site-crawler` primitive underpins
- `openspec/specs/indexing-and-cognition/spec.md` — the cocoindex-conformance
  CI workflow lives alongside the existing cocoindex-code MCP server + the
  CCC v1 surface
- `openspec/changes/archive/2026-07-09-cocoindex-v1-remaining-apps-v1/proposal.md`
  — the original archive proposal that named the conformance workflow
  (never landed)
- `AGENTS.md` — the "Respect the Ingestion Cache" rule for `USE_LOCAL_SCRAPES`
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/cocoindex/SKILL.md` — R1+R2+R3+R4 contract