---
title: 'Browser Automation'
domain: 'agents'
status: 'stable'
description: 'Decision tree for firecrawl-mcp, browserbase-mcp, sruth-browser, Stagehand, and skyvern. Site analysis via BAML is a first-class mode for page-level fingerprinting.'
read_when:
  - adding a new DLT source that needs to crawl
  - building an agent that needs to interact with a website
  - wiring the firecrawl or browserbase MCP
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - browser automation firecrawl browserbase stagehand
  - sruth-browser
  - site analysis
---

# Browser Automation

> **For the LLM-stack hierarchy** (BAML → litellm → ADK/AGNO → ccc
> cocoindex-code → Cognee), see
> [`docs/04-ai-ml/llm-stack-hierarchy.md`](../04-ai-ml/llm-stack-hierarchy.md).
> For change-watching, see [`docs/03-agents/change-detection.md`](change-detection.md).
> For the storage substrate, see [`docs/02-data-platform/storage-mental-model.md`](../02-data-platform/storage-mental-model.md).

## Decision tree

```
What do you need?
│
├── Scrape a public page (markdown + links)
│     │
│     ├── LLM-extracted structured data? (CMS, layout, page summary)
│     │     → use oideachais/site_analysis/ (BAML SiteAnalysis schema)
│     │       ─ JSON-RPC to firecrawl-mcp + browserbase-mcp
│     │       ─ stub mode under USE_LOCAL_SCRAPES=true
│     │
│     └── Just need the raw markdown?
│           │
│           ├── 1st choice: firecrawl-mcp (in opencode.json)
│           ├── 2nd choice: sruth-browser selfhosted (infrastructure/browser/sruth_browser/)
│           └── 3rd choice: Firecrawl API (paid fallback)
│
├── Interact with a page (click, form fill, login)
│     │
│     ├── 1st choice: browserbase-mcp (in opencode.json)
│     ├── 2nd choice: Stagehand selfhosted (infrastructure/browser/stagehand_proxy.py)
│     └── 3rd choice: skyvern selfhosted
│
├── Bulk-extract a whole domain (LLM-driven)
│     │
│     └── Crawl4AI (infrastructure/stacks/engineering/crawl4ai/)
│         Use for: hundreds of pages, when the LLM needs to read every one.
│
└── Discover URLs on a domain (no scraping yet)
      │
      └── firecrawl-mcp.map  (cheaper than crawl; use as pre-flight)
```

## What is wired today

| Tool | Where | Status |
|---|---|---|
| `firecrawl-mcp` | `opencode.json` | **wired** (MCP server running) |
| `browserbase-mcp` | `opencode.json` | **wired** (MCP server running) |
| `sruth-browser` | `infrastructure/browser/sruth_browser/` | **wired** (in-tree, selfhosted); also a Python package `sruth-browser` in the uv workspace |
| `Stagehand` | `infrastructure/browser/stagehand_proxy.py` | **wired** (proxy to OpenCode Go API for chat-completions) |
| `Crawl4AI` | `infrastructure/stacks/engineering/crawl4ai/` | **wired** (compose stack) |
| `skyvern` | `infrastructure/browser/sruth_browser/backends/selfhosted/` | **wired** (selfhosted backend) |
| `oideachais/site_analysis/` | `oideachais/site_analysis/` | **wired** (BAML schema, extractor, DLT source, Dagster assets) |

## What is NOT wired (and when to reach for it)

- `Firecrawl` API as a direct endpoint: only as a last-resort
  fallback. Use `firecrawl-mcp` instead (same backend, MCP-wrapped).
- `Browserbase` direct: use `browserbase-mcp`.

## `oideachais/site_analysis/` — the BAML-fingerprint mode

For a per-source software + layout + page-description fingerprint, use
the BAML `SiteAnalysis` schema at `oideachais/baml_src/site_analysis.baml`.
The flow is:

1. `oideachais.site_analysis.extractor.extract_source(source_id, base_url)`
2. → JSON-RPC to `firecrawl-mcp` with the BAML schema as `jsonOptions.schema`
3. → JSON-RPC to `browserbase-mcp` for the screenshot
4. → write row to `oideachais.site_analysis.site_analyses` (DuckLake)
5. → embed via CocoIndex into LanceDB `oideachais.site_analysis.descriptions`
6. → cognify into Cognee dataset `oideachais_site_analysis`
7. → Dagster assets at `oideachais/dagster_defs/assets/site_analysis/extract.py`

In test mode (`USE_LOCAL_SCRAPES=true`) the extractor delegates to the
fixture at `oideachais/site_analysis/_stubs/`. The asset graph
materialises cleanly without a live browser or firecrawl key.

## `sruth-browser` — the in-tree Python client

The `sruth-browser` Python package (in the uv workspace) wraps all 6
backends behind a single `BrowserClient` API:

- `infrastructure/browser/sruth_browser/backends/paid/firecrawl.py`
- `infrastructure/browser/sruth_browser/backends/paid/browserbase.py`
- `infrastructure/browser/sruth_browser/backends/selfhosted/cdp_backend.py`
- `infrastructure/browser/sruth_browser/backends/selfhosted/crawl4ai_backend.py`
- `infrastructure/browser/sruth_browser/backends/selfhosted/skyvern_backend.py`
- `infrastructure/browser/sruth_browser/backends/selfhosted/stagehand_backend.py`

Use it from Python code (e.g. inside a DLT resource) when you don't
want to go through the MCP.

## Where this doc is consumed

- `oideachais/dlt_sources/common/firecrawl_source.py` — the `crawl_website` /
  `scrape_page` router reads this tree.
- `oideachais/site_analysis/extractor.py` — the MCP JSON-RPC path follows the tree.
- `oideachais/agents/*` — the agent skills (`firecrawl`, `browser`,
  `browserbase-cli`) all read this doc.

## See also

- [`docs/03-agents/change-detection.md`](change-detection.md) — sitemap / ChangeDetection.io
- [`docs/04-ai-ml/llm-stack-hierarchy.md`](../04-ai-ml/llm-stack-hierarchy.md) — where BAML fits
- [`oideachais/site_analysis/`](../../oideachais/site_analysis/) — the BAML extractor
- [`infrastructure/browser/sruth_browser/`](../../infrastructure/browser/sruth_browser/) — the in-tree browser
- [`opencode.json`](../../opencode.json) — MCP server config
