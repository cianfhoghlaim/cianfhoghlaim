---
name: firecrawl-cli
description: The Bash CLI variant of the Firecrawl skill. Use when running Firecrawl from a terminal, CI pipeline, or scheduled job (no agent runtime). Covers the `firecrawl` CLI binary + the 12 subcommands (scrape, crawl, search, extract, map, agent, deep-research, browser-sandbox, monitor, batch, download, feedback). Triggers: 'firecrawl CLI', 'firecrawl batch', 'firecrawl monitor', 'firecrawl browser-sandbox', 'firecrawl from terminal', 'firecrawl in CI'.
---

# Firecrawl CLI — Bash Variant

This skill is the **Bash CLI variant** of the Firecrawl skill.
The other variant is the **MCP variant** (see `firecrawl/SKILL.md`),
which exposes Firecrawl as MCP tools for the agent runtime.

The two are functionally equivalent for the 4 core endpoints
(scrape, crawl, search, extract). The CLI is preferred when:

- Running in CI / scheduled jobs (no agent runtime).
- Needing a specific endpoint the MCP doesn't expose
  (e.g. `firecrawl monitor`, `firecrawl browser-sandbox`).
- Working from a terminal where you want the human-readable
  progress output (e.g. for ad-hoc research tasks).

## Installation

```bash
# Install the Firecrawl CLI
npm install -g firecrawl-cli

# Or use the npx pattern (no install)
npx firecrawl --help

# Or via the KCG mise task (preferred in Cianfhoghlaim)
mise run firecrawl:cli -- --help
```

## Authentication

The CLI reads the `FIRECRAWL_API_KEY` from the environment. In
Cianfhoghlaim, this is auto-hydrated via the Infisical `dev-baile`
vault (set the env var to `infisical://dev-baile/firecrawl/api_key`).

```bash
# Check auth
firecrawl auth status
```

## The 12 subcommands

### Core (4 — covered by both CLI and MCP)

```bash
# 1. scrape — single page to markdown
firecrawl scrape https://example.com --format markdown --only-main-content

# 2. crawl — recursive crawl of a site
firecrawl crawl https://docs.example.com --limit 100 --include-paths /api

# 3. search — web search with content scraping
firecrawl search "Celtic education Ireland" --limit 10 --provider "sambanova"

# 4. extract — structured extraction with a JSON schema
firecrawl extract https://example.com/product \
  --schema '{"name":"string","price":"number","inStock":"boolean"}'
```

### Advanced (8 — CLI only or CLI-primary)

```bash
# 5. map — sitemap discovery
firecrawl map https://example.com --search "API docs" --limit 50

# 6. agent — autonomous research
firecrawl agent \
  --goal "Identify all research papers on Irish NLP from 2020-2025" \
  --max-steps 10

# 7. deep-research — multi-step research with citations
firecrawl deep-research \
  --topic "Celtic curriculum knowledge graphs" \
  --max-depth 3 \
  --output-format "markdown+citations"

# 8. browser-sandbox — interactive browser session
firecrawl browser-sandbox --url https://example.com/login \
  --interactive --timeout 60000

# 9. monitor — recurring scrape with change detection
firecrawl monitor create --url https://example.com \
  --goal "Alert on breaking changes" --schedule "every 6 hours"

# 10. batch — scrape many URLs in parallel
firecrawl batch urls.txt --format markdown --concurrency 5

# 11. download — full-website capture
firecrawl download https://example.com --output ./snapshot --format html

# 12. feedback — submit endpoint-quality feedback
firecrawl feedback --job-id "abc-123" --rating good --note "Excellent"
```

## Output formats (12)

| Format | Cost | Use case |
|:--|:--|:--|
| `markdown` | 1 credit | Default; LLM-ready content |
| `summary` | 1 credit | Concise summary |
| `html` | 1 credit | Cleaned HTML |
| `rawHtml` | 1 credit | Unmodified HTML |
| `screenshot` | 1 credit | Page screenshot (URL expires in 24h) |
| `links` | 1 credit | All link URLs |
| `json` | 1 credit | Structured JSON (with schema) |
| `changeTracking` | varies | Per-field diffs (JSON path → `{previous, current}`) |
| `branding` | 5 credits | Brand identity (colors, fonts, design system) |
| `product` | 1 credit | Deterministic product extraction |
| `audio` | 5 credits | MP3 from supported video URLs |
| `video` | 5 credits | Best-quality video from supported URLs |

## When to use CLI vs MCP

Use **CLI** when:
- Running in CI / scheduled jobs (no agent runtime).
- Needing a specific endpoint the MCP doesn't expose
  (`firecrawl monitor`, `firecrawl browser-sandbox`).
- Working from a terminal where you want the human-readable
  progress output (e.g. for ad-hoc research tasks).
- Needing a one-off ad-hoc invocation with custom flags
  (e.g. `--proxy stealth`, `--zero-data-retention`).

Use **MCP** (`firecrawl/SKILL.md`) when:
- The agent runtime has the Firecrawl MCP server configured
  (the Cianfhoghlaim default; the MCP tools are visible in
  the agent's tool palette).
- The agent needs to compose Firecrawl calls in a multi-step
  workflow.
- You're building an agentic feature that needs Firecrawl
  as a tool (not a script).

## Cross-references

- The router skill: `browser-tools/SKILL.md`
- The MCP variant: `firecrawl/SKILL.md`
- The browser stack YAML files: `bonneagar/stacks/browser/`
- The Infisical vault: `dev-baile/firecrawl/*` (8 secrets)
