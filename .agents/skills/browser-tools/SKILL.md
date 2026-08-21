---
name: browser-tools
description: Router for all browser automation + web scraping + agent-on-the-web tools in Cianfhoghlaim. Use this to decide which tool fits a task: Crawl4AI (self-hosted REST), Crawl4AI MCP (v0.9.x native), Firecrawl MCP, Firecrawl CLI, Skyvern, Stagehand, or Playwright/CDP. Covers when to use each, the auth + cookie patterns, the 6-backend architecture (3 default + 2 opt-in + 1 MCP-native), the new Crawl4AI v0.9.x features (native MCP server, secure-by-default, JWT auth), the opt-in pattern for Skyvern + Stagehand, and the KCG safety rules (domain allowlist, no unscraped authentication flows). Triggers: 'browse website', 'scrape URL', 'login flow', 'click button', 'extract data from page', 'browser agent', 'autonomous browsing', 'screenshot', 'PDF capture', 'authenticated scraping', 'Crawl4AI', 'deep crawl', 'MCP-native'.
---

# Browser Tools — Router (post v4 + Crawl4AI v0.9.x + native MCP)

Cianfhoghlaim has **6 ways** to drive a browser, scrape a page, or
run an agent-on-the-web. This skill is the router — pick the
right one for the task.

## The 6 backends (Moderate strategy, 6 = 4 default + 2 opt-in)

| Backend | Default? | Cost | Port | When to use |
|:--|:--|:--|--:|:--|
| **Crawl4AI REST** (self-hosted) | ✅ ON | $0 | 11235 | The default Python SDK path. CSS+LLM extraction, deep crawl, hooks. Best for Python pipelines. |
| **Crawl4AI MCP** (self-hosted, v0.9.x native) | ✅ ON | $0 | 11235 | **NEW 2026-08-21**: the native MCP server (`/mcp/sse`, `/mcp/ws`). JWT-authed. Best for MCP-native agents. |
| **Firecrawl MCP** (paid) | ✅ ON | $0.005-0.05/page | MCP | Paid fallback. Best for anti-bot + JS-rendered + agent/research. |
| **Playwright CDP** (self-hosted) | ✅ ON | $0 | 9222 | Drive a real browser locally. Best for fine-grained interactions. |
| **Skyvern** (opt-in) | ⚙️ `BROWSER_ENABLE_SKYVERN=1` | $0 | 8000 | Vision-based semantic navigation. Opt-in for vision-heavy flows. |
| **Stagehand** (opt-in) | ⚙️ `BROWSER_ENABLE_STAGEHAND=1` | $0 | 3100 | AI-powered UI interactions + agent mode. Opt-in for autonomous flows. |

> **Browserbase was removed 2026-06-29** (no credits, no replacement plan)
> **and re-confirmed 2026-08-21** (per `openspec/changes/2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/`).
> The 2 opt-in backends are OFF by default to keep the surface area small.

## The 5 corresponding skills

| If you need to… | Use this tool | Skill |
|:--|:--|:--|
| Bulk extraction from a single URL into markdown/JSON (Python pipeline) | **Crawl4AI REST** | `crawl4ai` |
| Bulk extraction from many URLs (deep crawl) | **Crawl4AI REST** (BFS/DFS) | `crawl4ai` |
| MCP-native bulk extraction (MCP client / OpenCode agent) | **Crawl4AI MCP** (v0.9.x) | n/a — `mcp:smoke:crawl4ai` |
| Agent-driven research + structured extraction | **Firecrawl** (MCP) or **CLI** | `firecrawl` / `firecrawl-cli` |
| Cloud-based anti-bot + JS-rendered scraping | **Firecrawl** (MCP) | `firecrawl` |
| Local Chromium / Firefox via Playwright | **Playwright** (via the `browser` stack) | `browser` |
| Vision-based semantic navigation | **Skyvern** (opt-in) | n/a — set BROWSER_ENABLE_SKYVERN=1 |
| AI-powered UI interactions + agent mode | **Stagehand** (opt-in) | n/a — set BROWSER_ENABLE_STAGEHAND=1 |

## Decision tree (Crawl4AI-first)

```
Need to scrape a single static page (Python pipeline)?  → Crawl4AI REST (use css strategy)
Need MCP-native bulk extraction (agent runtime)?        → Crawl4AI MCP (v0.9.x native)
Need to extract structured data with a schema?        → Crawl4AI (use LLM strategy)
Need to deep-crawl a docs site?                        → Crawl4AI (BFS/DFS strategy)
Need to click / login / fill a form?                   → Firecrawl MCP interact (or Playwright if local)
Need vision-based navigation?                          → Skyvern (opt-in)
Need an autonomous agent that can plan?                 → Stagehand agent mode (opt-in)
Need a self-hosted scraper with no LLM cost?            → Crawl4AI (use css strategy — free)
Need full Playwright control locally?                   → browser (Playwright stack)
Need to monitor a page for changes?                     → Firecrawl MCP monitor
Need to interact with a page (login + click)?           → Firecrawl MCP interact
Need to scrape many URLs in batch?                      → Crawl4AI batch or Firecrawl batch
```

## The 5 backends in Python

```python
from cianfhoghlaim.core.browser import BrowserClient, BackendType

client = BrowserClient()

# 1. Crawl4AI (default, self-hosted, port 11235)
result = client.search(backend=BackendType.CRAWL4AI_LOCAL, query="...")

# 2. Firecrawl (default, paid MCP)
result = client.search(backend=BackendType.FIRECRAWL_MCP, query="...")

# 3. Playwright CDP (default, self-hosted, port 9222)
result = client.search(backend=BackendType.CDP_LOCAL, query="...")

# 4. Skyvern (opt-in, only if BROWSER_ENABLE_SKYVERN=1)
result = client.search(backend=BackendType.SKYVERN_LOCAL, query="...")

# 5. Stagehand (opt-in, only if BROWSER_ENABLE_STAGEHAND=1)
result = client.search(backend=BackendType.STAGEHAND_LOCAL, query="...")
```

## The new Crawl4AI 0.7.4 features (Phase E)

| Feature | Use case | API |
|:--|:--|:--|
| `JsonCssExtractionStrategy` | Zero-cost extraction for known-structure pages (NCCA, SEC, DES) | `client.extract_with_css(url, schema)` |
| `LLMExtractionStrategy` | Type-safe structured extraction with Pydantic | `client.extract_with_llm(url, PydanticClass)` |
| `use_managed_browser=True` | Persistent login sessions (QubStudent, etc.) | `client.authenticate(profile_name)` |
| `BFSDeepCrawlStrategy` / `DFSDeepCrawlStrategy` | Full-site crawling | `client.bulk_crawl(seed_url, strategy="BFS")` |
| Hooks (`on_page_context_created`, etc.) | Login automation + cookie capture | n/a (advanced) |

## KCG safety rules

1. **No unscraped authentication flows** — any login / OAuth / MFA
   interaction MUST go through Firecrawl interact (which can
   use a persistent context) or a manually-set cookie. Never
   inline credentials into a script.
2. **Domain allowlist for autonomous agents** — any agent
   that browses without human supervision must use the new
   opt-in Stagehand (with an explicit allowlist) or the
   Skyvern vision-based navigation. Unbounded browse is a
   credit-burn hazard.
3. **No raw `:latest` for upstream images** — the
   `browser` stack uses pinned images (Crawl4AI 0.7.4,
   Skyvern 1.x.y, Stagehand 1.x.y).
4. **Token storage** — Firecrawl + Skyvern + Stagehand tokens
   come from the Infisical `dev-baile` vault. Never commit
   them to `.env` or to the source tree.
5. **Credit budget guard** — every Firecrawl call is routed
   through `CreditBudget` (SQLite-backed, persistent across
   restarts). When the budget is depleted, the router falls
   back to a free backend (Crawl4AI). The budget never raises
   `BudgetExhaustedError` to the caller.

## When to use Firecrawl MCP vs CLI

Use **MCP** (`firecrawl/SKILL.md`) when the agent runtime has the
Firecrawl MCP server configured (the Cianfhoghlaim default; the
MCP tools are visible in the agent's tool palette).

Use **CLI** (`firecrawl-cli/SKILL.md`) when:

- Running in CI / scheduled jobs (no agent runtime).
- Needing a specific endpoint the MCP doesn't expose (e.g.
  `firecrawl monitor`, `firecrawl browser-sandbox`).
- Working from a terminal where you want the human-readable
  progress output.

The two are functionally equivalent for the 4 core endpoints
(scrape, crawl, search, extract); MCP just wraps them as MCP
tools.

## When to use the opt-in backends

The 5-backend Moderate strategy keeps Skyvern + Stagehand OFF
by default to minimize surface area. To enable them, set the
env vars:

```bash
# In .env or mise.toml
BROWSER_ENABLE_SKYVERN=1
BROWSER_ENABLE_STAGEHAND=1
```

When enabled, the corresponding DLT sources + Dagster assets
are registered (per the `defs/browser/auth_assets.py` pattern).

## Cross-references

- The canonical Python module: `cianfhoghlaim.core.browser`
  (formerly `sruth_browser`; renamed 2026-06-29 per
  openspec/changes/2026-06-29-browser-stack-crawl4ai-refactor)
- The browser stack YAML files: `bonneagar/stacks/browser/`
  (v4 worktree split; bug fixes need 2 PRs)
- The new Dagster Component: `cianfhoghlaim/assets/_cianfhoghlaim_dagster_defs/defs/browser/`
  (DltLoadCollectionComponent + crawl4ai_defs + firecrawl_defs + auth_defs)
- The BAML extraction: `cianfhoghlaim/core/baml/_cianfhoghlaim_src/author_archive.baml`
  (calls ScrapeStrategist for site map + bulk scrape)
- The DAG asset groups that use this: `author_archive_assets.py`,
  `leabharlann_inbox_assets.py`, `croilar_cv_extraction.py`,
  `official_media/scraping_assets.py`

## History

- 2026-08-14: Firecrawl MCP promoted to the canonical **external search surface** of the agent stack (per the `2026-08-14-firecrawl-mcp-ccc-dual-search-v1` change). The `FirecrawlMCPClient` wrapper at `agents/meaisinfhoghlaim/firecrawl_mcp/client.py` exposes all 12 MCP tools with Pydantic + Langfuse `@observe`. The complete routing table (ccc vs cognee vs firecrawl_mcp) lives at `AGENTS.md` §"Triple-search architecture" and the [`dual-search-architecture`](../openspec/specs/dual-search-architecture/spec.md) spec.
- 2026-06-28: v4 consolidation (5 quadrants → 1 cianfhoghlaim package)
- 2026-06-29: Browser stack + Crawl4AI refactor
  - Phase A: DAG integration (new `defs/browser/` Component)
  - Phase B: killed browserbase (no credits)
  - Phase D: cut to 3 backends, added Skyvern + Stagehand back as opt-in
  - Phase E: new Crawl4AI 0.7.4 features (CSS+LLM, auth, deep crawl)
  - Phase F: renamed `sruth_browser` → `browser` (v4 cleanup)
