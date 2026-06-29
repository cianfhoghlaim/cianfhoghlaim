---
name: browserbase
description: "Cloud browser automation toolkit — the 17 BrowserBase sub-skills for browser automation, Stagehand MCP server, fetch endpoint, WebMCP generation, and agent-on-the-web research. Use when needing to interact with any web page via natural language or selectors, scrape authenticated or rate-limited sites, monitor a page for changes, generate a persistent WebMCP accessor for a frequent source site, run an autonomous research agent on the web, or audit the developer experience of a web product. The Cianfhoghlaim 2026-06-28 BrowserBase 6,000-credit research program (`openspec/research/2026-06-28-browserbase-credit-program/`) uses these sub-skills to document 30+ key packages + 12 source websites for agent consumption."
license: MIT
metadata:
  openclaw:
    install:
      - kind: node
        package: "@browserbasehq/mcp"
        bins: ["mcp-browserbase"]
      - kind: node
        package: "browse"
        bins: ["browse"]
  homepage: https://docs.browserbase.com
---

# BrowserBase — Cloud Browser Automation Toolkit

BrowserBase gives every agent a remote Chromium instance via the MCP
protocol (6 tools exposed by the hosted Streamable HTTP server at
`https://mcp.browserbase.com/mcp`: `start`, `end`, `navigate`, `act`,
`observe`, `extract`) plus a curated skill tree below for the heavier
workflows.

The Cianfhoghlaim monorepo uses BrowserBase for two distinct workloads:

1. **Agentic web research** — the 2026-06-28 BrowserBase 6,000-credit
   research program documents 30+ packages + 12 source websites.
   See `openspec/research/2026-06-28-browserbase-credit-program/`.
2. **Live source ingestion** — `firecrawl` MCP is the KCG-preferred
   primary path, but BrowserBase handles JavaScript-rendered SPAs that
   Firecrawl can't reach (examinations.ie dropdowns, NCCA curriculum
   selectors, etc.). Always check `stedding/ingest_queue/` first; only
   fall back to BrowserBase for SPAs that the cache can't serve.

## When to load which sub-skill

| Sub-skill | Trigger | Use case |
|:--|:--|:--|
| [`browser`](./browser/SKILL.md) | "browse this URL", "navigate the site", "click the button" | Interactive pages, JS-heavy SPAs, login flows. Uses `browse open <url> --remote` CLI. |
| [`fetch`](./fetch/SKILL.md) | "fetch this URL", "get the page content", "GET this endpoint" | Static HTML / JSON / API responses (no JS rendering). Cheaper than browser. |
| [`browser-trace`](./browser-trace/SKILL.md) | "trace the page", "find the selector", "what's the JSON shape" | Extract structure (selectors, JSON paths) for downstream WebMCP. |
| [`webmcp-gen`](./webmcp-gen/SKILL.md) | "generate a WebMCP accessor", "compile this manifest", "make a persistent tool" | Build a reusable WebMCP init script for a frequent source. |
| [`company-research`](./company-research/SKILL.md) | "research this company", "ICP analysis", "depth=quick\|deep\|deeper" | Structured company research with sources + scoring. |
| [`safe-browser`](./safe-browser/SKILL.md) | "browse allowlisted sites", "browse with guardrails", "constrained agent" | Allowlist + rate-limit + PII redaction for risky sources. |
| [`cookie-sync`](./cookie-sync/SKILL.md) | "sync my cookies", "browse as me", "login via Browserbase" | Local Chrome cookies → Browserbase persistent context. |
| [`browserbase-cli`](./browserbase-cli/SKILL.md) | "deploy a function", "create a context", "browserbase API" | Serverless Functions + platform API workflows. |
| [`browser-to-api`](./browser-to-api/SKILL.md) | "convert site to API", "openapi from URL" | Reverse-engineer an OpenAPI spec from a UI. |
| [`browser-use-to-stagehand`](./browser-use-to-stagehand/SKILL.md) | "port my browser-use script", "convert to Stagehand" | Migrate browser-use → Stagehand. |
| [`autobrowse`](./autobrowse/SKILL.md) | "let the agent figure it out", "autonomous browsing" | Goal-driven multi-step navigation. |
| [`agent-experience`](./agent-experience/SKILL.md) | "audit this SDK for agent DX", "test the docs" | Drop subagents at a product, score their DX. |
| [`competitor-analysis`](./competitor-analysis/SKILL.md) | "compare competitors", "feature matrix" | Multi-site comparative research. |
| [`event-prospecting`](./event-prospecting/SKILL.md) | "find leads at <conference>", "scrape speakers" | Conference speaker → person-first report. |
| [`functions`](./functions/SKILL.md) | "deploy this as a function", "schedule it" | Browserbase Functions (serverless browser). |
| [`search`](./search/SKILL.md) | "search the web", "find URLs" | Google / DuckDuckGo structured search. |
| [`ui-test`](./ui-test/SKILL.md) | "test this UI", "screenshot diff" | Visual regression + assertion tests. |

## Primary research program selector

For the 2026-06-28 BrowserBase 6,000-credit program (43 prompts, 4 Phases):

- **Packages** (Phase 1 + 2): use `fetch` primarily (cheapest), switch to
  `browser` only for SPA docs (Dagster, CocoIndex, MotherDuck, Cognee).
- **Sites** (Phase 3): use `browser-trace` first to discover the cascade,
  then `fetch` for the leaf URLs.
- **Validation**: use `safe-browser` for any site with auth or rate-limit
  risk (curriculumonline.ie, examinations.ie, ncca.ie).
- **Persistent accessors**: use `webmcp-gen` for the top-3 highest-frequency
  sites (currently: examinations.ie, ncca.ie, curriculumonline.ie) — saves
  ~75 credits per future scrape.

## KCG integration

The BrowserBase MCP is configured in `opencode.json` as the hosted
Streamable HTTP endpoint (no local process required):

```json
"browserbase": {
  "type": "http",
  "url": "https://mcp.browserbase.com/mcp",
  "env": {
    "BROWSERBASE_API_KEY": "infisical://dev-baile/browserbase/api_key"
  },
  "enabled": true
}
```

The 6 tools exposed are: `start`, `end`, `navigate`, `act`, `observe`,
`extract`. Browserbase's default Stagehand model is Gemini Flash Lite
(absorbed into their LLM cost — no extra Anthropic bill). If quality is
insufficient on a specific site, revert to self-hosted STDIO with
`anthropic/claude-sonnet-4.5` (costs ~$0.003/action through Anthropic).

## Fallback paths

1. **`stedding/ingest_queue/`** — every source has a curated cache.
   Set `os.environ['USE_LOCAL_SCRAPES'] = 'true'` first to avoid draining
   API credits. The cache mirrors the upstream at known-good points in
   time.
2. **`firecrawl` MCP** — KCG-preferred primary path. Faster, cheaper, but
   no JS rendering.
3. **`@browserbasehq/mcp` self-hosted STDIO** — when hosted SHTTP fails
   or Gemini Flash Lite quality is insufficient. Pin to
   `@browserbasehq/mcp@3.0.0` (latest stable, no `--experimental` flag).
4. **Stagehand self-hosted** — when both MCP options fail. Use the
   Node.js / Python SDK directly with a custom `modelName`.

## Related Cianfhoghlaim infrastructure

- `infrastructure/stacks/firecrawl/` — KCG's primary scraper (alternative)
- `infrastructure/stacks/olake/` — CDC engine for streaming source changes
- `infrastructure/stacks/changedetection/` — change watcher (Phase 3 sites
  can be wired here for re-runs)
- `infrastructure/stacks/letta/` — persistent agent memory (BrowserBase
  research sessions can store their notes here)
- `openspec/research/2026-06-28-browserbase-credit-program/` — the output
  tree for all research notes (Phase 1+2+3 deliverables)
