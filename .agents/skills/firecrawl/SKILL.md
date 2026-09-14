---
name: firecrawl
description: Use the Firecrawl MCP server (the 12 Firecrawl tools exposed to the agent runtime). Use when integrating Firecrawl into application code or as an agent tool for web scraping, search results, structured extraction, browser interaction, or research paper retrieval. For the Bash CLI variant (terminal/CI/scheduled jobs), use the `firecrawl-cli` skill instead. For the routing decision (when to use Firecrawl vs Crawl4AI vs Skyvern vs Stagehand vs Playwright), use the `browser-tools` skill. Triggers for Firecrawl API calls, "fire girl" shorthand, or any app-level web-data requirement that should map to /scrape, /search, /interact, or /research.
license: ISC
metadata:
  author: firecrawl
  version: "0.1.0"
  homepage: https://www.firecrawl.dev
  source: https://github.com/firecrawl/skills
inputs:
  - name: FIRECRAWL_API_KEY
    description: Firecrawl API key for cloud usage. Store in `.env` or the runtime environment before making Firecrawl API calls.
    required: true
  - name: FIRECRAWL_API_URL
    description: Optional base URL for self-hosted Firecrawl deployments. Only set this when the project is not using the hosted `api.firecrawl.dev`.
    required: false
---

# Firecrawl (meta-skill)

Use this skill when the task is "use Firecrawl" in any form — either integrating it into application code, or as a one-off research tool. The skill picks the right sub-skill for the job.

## Sub-skill routing

Default toward the most specific sub-skill:

- **`firecrawl-build`** — integrating Firecrawl into application code (web search, live search, page scraping, structured extraction, browser interaction). Use when building any feature that needs data from the web in code, even if the user does not mention Firecrawl explicitly.
- **`firecrawl-build-scrape`** — Firecrawl `/scrape` endpoint (single-page content extraction). Use for single-page markdown, HTML, screenshots, metadata, or structured output.
- **`firecrawl-build-search`** — Firecrawl `/search` endpoint (web search with optional content scraping). Use for finding pages on the web.
- **`firecrawl-build-interact`** — Firecrawl `/interact` endpoint (dynamic pages, browser actions). Use after scraping to handle JS-rendered pages, pagination, forms, or auth-aware flows.
- **`firecrawl-build-onboarding`** — getting started, project setup, SDK installation, auth flow.
- **`firecrawl-research-index`** — terminal-only research: finding the papers that answer a query (semantic search, semantic + structural expansion, in-body verification). Use for single-paper lookups or full multi-paper sets.

## Choosing a sub-skill

1. If the task is **building product code that needs web data**, route to `firecrawl-build` (or the more specific build sub-skill).
2. If the task is **one-off terminal research** (find papers, browse docs, extract data), route to `firecrawl-research-index` for papers or to `firecrawl-build-scrape` for general web pages.
3. If the task is **onboarding/setup**, route to `firecrawl-build-onboarding`.

## The endpoints, and what each is uniquely good at

- **`/scrape`** (single page): markdown, HTML, screenshots, metadata, structured JSON extraction, or screenshot
- **`/search`** (web): title, URL, description, optional markdown content
- **`/interact`** (dynamic pages, browser actions): clicks, form fills, pagination, auth-aware flows
- **`/research`** (papers): semantic (HyDE) search over abstracts, structural/semantic expansion, in-body verification

## CONSTRAINTS

- **NEVER** make a Firecrawl call without `FIRECRAWL_API_KEY` set in the environment (or `.env`)
- For one-off terminal tasks, prefer `crawl4ai` (local) if no API credits are available
- Self-hosted Firecrawl works too — set `FIRECRAWL_API_URL` to point at your instance


## ⚠️ CURRENT STATUS (2026-09-13, Plan 8 audit)

- **MCP server**: configured at `.mcp.json` (`bunx -y firecrawl-mcp`)
  - 12 tools exposed: scrape, map, search, parse, crawl, agent,
    interact, batch_scrape, monitor_*, research_*, developer_search, ask
- **4 monitor configs** at `docs/firecrawl/monitors/upstream_packages/`:
  - `dlthub_blog.yml` — dlt/dltHub blog (30-min cadence)
  - `lancedb_blog.yml` — LanceDB blog
  - `motherduck_blog.yml` — MotherDuck blog
  - `cocoindex_docs.yml` — CocoIndex docs (5 surfaces + llms-full.txt)
- **Wrapper**: `agents/meaisinfhoghlaim/firecrawl_mcp/client.py`
  wraps all 12 tools with Pydantic + Langfuse observability
- **No Firecrawl v2 SDK installed locally** — uses `bunx firecrawl-mcp`
- **Firecrawl docs are not in `docs/firecrawl/`** — only the 4 monitor
  configs are present (the upstream blog posts themselves are fetched
  live via Firecrawl)

### Firecrawl monitor → CocoIndex pipeline (Phase 8 from the v6 plan)

The 4 monitor configs scrape upstream blog posts every 30 min. The
extracted `ApiChange` records would normally flow into a v1 CocoIndex
App (`upstream_api_surface_app`) which writes them to the
`upstream_packages_graph` FalkorDB graph — **but this pipeline is
currently broken** (the CocoIndex App was lost in Phase 16-29).
Re-implementation deferred to when Phase 16-29 work is re-applied.
