---
name: browser-tools
description: Router for all browser automation + web scraping + agent-on-the-web tools in KCG. Use this to decide which tool fits a task: raw Playwright/CDP, Browserbase Stagehand, Firecrawl MCP, Firecrawl CLI, crawl4ai, or a constrained safe-browser agent. Covers when to use each, the auth + cookie patterns, the CUA / DeepLocator / agent modes of Stagehand, the Firecrawl browser-sandbox + monitor + agent endpoints, and the KCG safety rules (domain allowlist, no unscraped authentication flows). Triggers: 'browse website', 'scrape URL', 'login flow', 'click button', 'extract data from page', 'browser agent', 'autonomous browsing', 'screenshot', 'PDF capture', 'authenticated scraping'.
---

# Browser Tools — Router

KCG has 5+ ways to drive a browser, scrape a page, or run an
agent-on-the-web. This skill is the router — pick the right one
for the task.

## The 6 tools

| If you need to… | Use this tool | Skill |
|:--|:--|:--|
| Run an autonomous agent that clicks / fills / navigates a real browser | **Stagehand v3** (CUA + DeepLocator + hybrid) | `stagehand` |
| Scrape a static or JS-rendered URL into clean markdown / JSON | **Firecrawl MCP** (preferred) or **Firecrawl CLI** | `firecrawl` / `firecrawl-cli` |
| Extract a JSON schema from many pages, crawl a docs site, download a site | **Firecrawl agent / crawl / download** | `firecrawl-agent` / `firecrawl-crawl` / `firecrawl-download` |
| Run an open-source self-hosted scraper with full control over the HTML output | **crawl4ai** | `crawl4ai` |
| Drive a real Chromium / Firefox locally with Playwright (no cloud) | **Playwright** (via the `browser` skill) | `browser` |
| Build a safe, constrained browser agent for an autonomous task (domain allowlist enforced) | **safe-browser** | `safe-browser` |

## Decision tree

```
Need to scrape a single static page?             → Firecrawl scrape
Need to scrape many pages from a docs site?       → Firecrawl crawl
Need to click / login / fill a form?              → Stagehand (Browserbase)
Need an autonomous agent that can plan?           → Stagehand v3 agent mode
Need to extract structured data from many pages?  → Firecrawl agent
Need a self-hosted scraper?                      → crawl4ai
Need full Playwright control locally?             → browser
Need a safe agent with a domain allowlist?         → safe-browser
Need to monitor a page for changes?               → firecrawl-monitor
Need to interact with a page (login + click)?     → firecrawl-interact
Need to scrape many URLs in batch?                → firecrawl-batch
Need to capture a full website?                   → firecrawl-download
```

## KCG safety rules

1. **No unscraped authentication flows** — any login / OAuth / MFA
   interaction MUST go through Browserbase Stagehand (which can
   use a persistent context) or a manually-set cookie via
   `cookie-sync`. Never inline credentials into a script.
2. **Domain allowlist for autonomous agents** — any agent
   that browses without human supervision must use `safe-browser`
   (or be wrapped in the `stagehand` "agent" mode with an
   explicit allowlist). Unbounded browse is a credit-burn hazard.
3. **No raw `:latest` for upstream images** — the
   `browserbase-cli` skill uses the pinned image
   `ghcr.io/cianfhoghlaim/browserbase-cli:1.x.y`.
4. **Token storage** — Firecrawl + Browserbase tokens come from
   the Infisical `dev-baile` vault. Never commit them to `.env`
   or to the source tree.

## When to use Firecrawl MCP vs CLI

Use **MCP** (`firecrawl/SKILL.md`) when the agent runtime has the
Firecrawl MCP server configured (the KCG default; the MCP tools
are visible in the agent's tool palette).

Use **CLI** (`firecrawl-cli/SKILL.md`) when:

- Running in CI / scheduled jobs (no agent runtime).
- Needing a specific endpoint the MCP doesn't expose (e.g.
  `firecrawl monitor`, `firecrawl browser-sandbox`).
- Working from a terminal where you want the human-readable
  progress output.

The two are functionally equivalent for the 4 core endpoints
(scrape, crawl, search, extract); MCP just wraps them as MCP
tools.

## When to use Stagehand v3 agent mode

The Stagehand "agent" mode (CUA-style computer-use) is the right
choice when:

- The page has a JavaScript-heavy flow that no static scraper
  can handle.
- The interaction requires multi-step planning (e.g. "go to the
  vendor's site, find the pricing page, click the first plan
  that mentions 'enterprise', screenshot it").
- You need the agent to handle errors / retries / alternate
  selectors itself.

For straight extraction without interaction, Firecrawl is
faster and 10x cheaper.

## When NOT to use any of these

- The data is already in a public API → call the API directly
  (cheaper, faster, more reliable).
- The data is already in the KCG lakehouse (DuckLake) → query
  MotherDuck.
- The data is behind a paywall / terms-of-service that forbids
  scraping → don't scrape it; use the official API.
- The page is your own → use the local app's API instead of
  scraping the UI.

## Pair this skill with

- `firecrawl/SKILL.md` — the Firecrawl MCP variant
- `firecrawl-cli/SKILL.md` — the Firecrawl Bash variant
- `stagehand/SKILL.md` — the Stagehand / Browserbase pattern
- `crawl4ai/SKILL.md` — the self-hosted open-source alternative
- `safe-browser/SKILL.md` — the constrained-agent pattern
- `secrets-management/SKILL.md` — token storage in Infisical

## Cross-references

- [Firecrawl docs](https://docs.firecrawl.dev)
- [Browserbase Stagehand docs](https://docs.stagehand.dev)
- [crawl4ai](https://docs.crawl4ai.com)
- [KCG secrets management](.agents/skills/secrets-management/SKILL.md)
