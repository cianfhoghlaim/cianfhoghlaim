# 2026-07-15-pipeline-architecture-clarity-v1

## Why

The Cianfhoghlaim DLT layer has accumulated three classes of structural
debt that block the Phase-2+ work of the `multimodal-code-and-media-intel`
change and the planned cross-nation extension of the BIEP pipeline:

1. **Private-helper leakage across packages** — `dlt/british_isles/ireland/education/curriculum.py:_crawl_source`
   is imported by 7+ downstream sources (including cross-package imports
   from `dlt/british_isles/ireland/law/citizensinformation.py`,
   `dlt/british_isles/ireland/medicine/hse.py`, etc.). A leading-underscore
   private helper should not be imported from another package.
2. **Three overlapping crawler primitives** — `dlt/common/firecrawl_source.py`
   (browser + firecrawl adapter), `dlt/common/incremental.py:crawl_source`
   (URL discovery + crawl), and `dlt/british_isles/ireland/education/curriculum.py:_crawl_source`
   all do overlapping work. There is no single canonical entry point.
3. **5 pre-existing conformance FAILs** that are not real regressions —
   3 utility files in `dlt/filesystem/` (`_citation_extractor.py`,
   `_takeout_paths.py`, `_epub_extractor.py`) that are not LanceDB flows
   at all, plus the 2 test files I added in the multimodal-code change.
   The `cocoindex_v1_migrate.py` audit treats them as flows because they
   live in `dlt/filesystem/` (or `cocoindex/` for tests), so they FAIL the
   R1+R2 check. They need an explicit `# R4-exempt:` marker (or for the
   3 utility files, a relocation to `dlt/common/` where the audit ignores
   them).

This change closes all three gaps so the BIEP v2 cross-nation extension
(Change E) and the multimodal-code-and-media-intel Phase 2+ (Change G)
can build on a single canonical web-scraper primitive.

## What Changes

### 1. New canonical primitive `dlt/common/site_crawler.py` (~250 lines)

A single 3-way site-crawler adapter that subsumes the existing
`firecrawl_source.py` + `incremental.py:crawl_source` +
`curriculum.py:_crawl_source`. Backend priority matches the existing
`firecrawl_source.py: get_scraper_client()`:

1. **BrowserClient** (self-hosted, `$0`) — when `BROWSER_API_URL` is set
2. **Firecrawl API** (paid fallback) — when `FIRECRAWL_API_KEY` is set
3. **Local scrape cache** (`stedding/ingest_queue/<source_key>/`) — when
   `USE_LOCAL_SCRAPES=true` (the AGENTS.md "Respect the Ingestion Cache"
   rule)

Exposes one public API:

```python
from cianfhoghlaim.dlt.common.site_crawler import (
    scrape_url,         # scrape a single page → dict with markdown/html/links
    crawl_site,         # discover + batch-scrape URLs from a base URL
    map_urls,           # discover URLs without scraping
    CrawledPage,        # typed result dataclass
)
```

The legacy helpers remain as thin re-export wrappers so existing call
sites keep working during the deprecation window.

### 2. R4-exempt markers + relocation of 3 utility files

- Add `# R4-exempt: this file is a utility, not a LanceDB flow — see oideachais-cocoindex-v1-migration.md`
  at the top of `_citation_extractor.py`, `_takeout_paths.py`,
  `_epub_extractor.py` (or relocate them to `dlt/common/utilities/` which
  the audit tool does not scan).
- Add the same marker to the 2 test files (`test_phase0_primitives.py`,
  `test_youtube_kg_smoke.py`) — they're in `cocoindex/` purely for
  colocated-test convenience, not because they're flows.

### 3. Update 7+ downstream DLT sources to import from `site_crawler`

Refactor the imports in:
- `dlt/british_isles/ireland/law/citizensinformation.py`
  (currently `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source`)
- `dlt/british_isles/ireland/medicine/hse.py`
  (currently `from cianfhoghlaim.dlt.common.incremental import crawl_source`)
- `dlt/british_isles/england/medicine/nice.py`
- `dlt/british_isles/england/medicine/gmc.py`
- `dlt/british_isles/england/medicine/nhs_england.py`
- `dlt/british_isles/scotland/medicine/nhs_scotland.py`
- `dlt/british_isles/ireland/law/irish_statute_book.py`
- `dlt/british_isles/ireland/education/curriculum.py` (make `_crawl_source` a
  thin alias for the new primitive + add a deprecation comment)

### 4. New CI gate `.github/workflows/cocoindex-conformance.yaml`

A pre-commit + PR-check workflow that runs:

```yaml
- run: uv run python dlt/common/cocoindex_v1_migrate.py --check-only
- run: openspec validate --strict
```

This was referenced in the archived `2026-07-09-cocoindex-v1-remaining-apps-v1`
proposal (section 3 of the proposal.md) but the workflow file was never
landed. Without it, R4 regressions slip through silently.

### 5. `firecrawl_source.py` + `incremental.py` keep their public API as
   thin re-exports of `site_crawler.py`

Backward compat — the old import paths continue to work. A
`DeprecationWarning` is emitted on the first call to the legacy helpers.

## Capabilities

### New Capabilities
- `site-crawler`: the canonical 3-way web-scraper primitive
  (BrowserClient → Firecrawl → local cache). Lives at
  `dlt/common/site_crawler.py`.

### Modified Capabilities
- `indexing-and-cognition`: add the `cocoindex-conformance` CI workflow
  as a hard requirement (the workflow was always implicit, now it's
  explicit). The 9→12 MCP-tool count from the multimodal-code change
  already bumps this; the workflow addition is the second change to
  this spec.
- `oideachais-pipeline`: register `site_crawler.py` as the canonical
  web-scraper entry point. Existing firecrawl/incremental/curriculum
  helpers become deprecation-warned thin re-exports.

## Impact

- **`dlt/`**: 1 new file (`common/site_crawler.py`) +
  3 utility-file relocations + 8 import-path updates
- **`openspec/specs/`**: 1 new spec (`site-crawler`)
- **`.github/workflows/`**: 1 new workflow file
- **`bonneagar/`**: no changes
- **`leabharlann/`**: no changes

## Dependencies

Blocked by: none — this is a foundational refactor that pre-existed
the multimodal-code work and is independently shippable.

Affected repos: **cianfhoghlaim only**.

## Risks

- **Risk**: The `firecrawl_source.py` and `incremental.py:crawl_source`
  are used by sources that may have subtle behavioral differences
  (different retry logic, different URL filtering, different logging).
  **Mitigation**: The new `site_crawler.py` exposes a superset API +
  the legacy helpers emit `DeprecationWarning` but keep working. The
  change is opt-in per source; no DLT source needs to migrate in this
  change. Migration happens organically in Change E (BIEP v2).

- **Risk**: The CI workflow may fail on unrelated existing issues
  (e.g., the pre-existing broken cocoindex installation). **Mitigation**:
  The workflow uses `continue-on-error: false` for the conformance check
  but `continue-on-error: true` for the openspec validate (since the
  v4-drift-remediation change may need to land first). The exact matrix
  is captured in the workflow file.

## Quality gates

- `openspec validate --strict` MUST pass before commit
- `uv run python dlt/common/cocoindex_v1_migrate.py --check-only`
  MUST report at least 50/53 flows pass (was 48/53 before; the 3 utility
  files + 2 test files are now R4-exempt)
- `git grep "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source"`
  MUST return 0 matches after the refactor
- `git grep "from cianfhoghlaim.dlt.common.incremental import crawl_source"`
  MUST return 0 matches after the refactor

## Cross-references

- `openspec/changes/archive/2026-07-09-cocoindex-v1-remaining-apps-v1/proposal.md`
  (the CI workflow was originally proposed here)
- `openspec/specs/indexing-and-cognition/spec.md` (the spec that owns the
  cocoindex-code MCP server + the conformance audit)
- `openspec/specs/oideachais-pipeline/spec.md` (the spec that owns the DLT
  layer + web scrapers)
- `.agents/skills/dlt/SKILL.md` (DLT conventions)
- `.agents/skills/cocoindex/SKILL.md` (R1+R2+R3+R4 contract)
- `AGENTS.md` (the "Respect the Ingestion Cache" rule for `USE_LOCAL_SCRAPES`)