# 104 - Firecrawl v2 (deferred site)

**Status:** Researched 2026-06-29 via firecrawl MCP (zero browserbase credits)
**Canonical source:** https://docs.firecrawl.dev/features/scrape
**Cianfhoghlaim footprint:** 3 firecrawl DLT sources in `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/common/firecrawl_source.py`

## TL;DR

Firecrawl v2's `/scrape` endpoint has 12 output formats. The most
relevant for cianfhoghlaim are `markdown` (1 credit/page, the
default for DLT ingestion), `branding` (5 credits, for the croilar
portfolio design system analysis), and `json` with `prompt` (5
credits, for the BAML-extraction-replacement pattern).

**Key v2 changes from v1:**
- `changeTracking` format with `modes: ["json", "git-diff"]` for
  per-field diffs (JSON path → `{previous, current}`)
- `interact` (newer than `actions`) for stateful browser sessions
  with profiles, persistent sessions, and a live embeddable view
- `monitor` API (1.0+) for cron-scheduled recurring scrapes with
  `goal` + automatic meaningful-change judging
- `lockdown: true` for air-gapped compliance (5 credits)
- `zeroDataRetention` for SOC 2 / GDPR

## Code

The 3 v2 patterns we use at cianfhoghlaim:

1. **DLT ingestion** (most common — used by 80% of sources)
   ```python
   from firecrawl import Firecrawl
   firecrawl = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
   doc = firecrawl.scrape(url, formats=["markdown", "links"])
   yield doc.markdown  # → DLT resource
   ```

2. **BAML-replacement** (structured extraction without the
   BAML schema boilerplate)
   ```python
   result = firecrawl.scrape(
       url,
       formats=[{
           "type": "json",
           "prompt": "Extract the NCCA primary learning outcomes"
       }],
   )
   yield result.json  # already typed, no Pydantic model needed
   ```

3. **Change monitoring** (the 4 upstream-package monitors in
   `oideachais-leabharlann` capability)
   ```python
   firecrawl.create_monitor(
       url="https://motherduck.com/docs",
       schedule="every 6 hours",
       goal="Alert on breaking changes to MotherDuck DuckDB API",
   )
   ```

## Env

- `FIRECRAWL_API_KEY` — set in `.infisical.env` to
  `infisical://dev-baile/firecrawl/api_key`
- `FIRECRAWL_BASE_URL` — default `https://api.firecrawl.dev/v2`

## ccc anchors

- `firecrawl` skill at `.agents/skills/firecrawl/SKILL.md` (12 refs)
- `dlt` skill at `.agents/skills/dlt/SKILL.md` (DLT+Firecrawl pattern)
- `motherduck` skill at `.agents/skills/motherduck/SKILL.md`

## Anti-patterns

- **LLM-as-judge evals** on Firecrawl `json` output — use deterministic
  math instead.
- **Hardcoded `provider "openai"` inline** in BAML functions — use the
  canonical shared/clients.baml LiteLLM clients instead.
- **Sequential scraping** of multiple URLs — use `batch_scrape()`
  with `poll_interval=2` to parallelize.
- **`max_age=0` everywhere** — caching speeds up scrapes 5x; only
  set to 0 for compliance-sensitive fresh data.

## Decision matrix

| Use Firecrawl when | Use Chrome when | Use webfetch when |
|:--|:--|:--|
| Multi-page crawl | Local app E2E | Single static page |
| JS-rendered content | Authenticated flows | API docs lookup |
| Structured extraction (BAML-replacement) | Lighthouse + perf trace | Quick text content |
| Change monitoring (recurring) | Form submission | Public REST API |
| Branding / design system | 60fps rendering check | Markdown export |
| PDF/DOCX auto-detection | Visual regression | |
