# Browser Stack + Crawl4AI Refactor

## Why

The `sruth_browser` Python module + the `browser` Docker Compose stack
have drifted from the v4 priorities:

1. **10 backends** (CDP, Crawl4AI, Skyvern, Stagehand, Browserbase,
   Firecrawl, Z.AI Vision, Z.AI MCP, Browserbase-MCP, Z.AI-via-Firecrawl)
   — Browserbase has no credits and is dead weight. The Z.AI backends
   are not used in any pipeline.
2. **Crawl4AI 0.7.4 has new features** (CSS+LLM dual extraction,
   `use_managed_browser=True` for auth, `BFSDeepCrawlStrategy` /
   `DFSDeepCrawlStrategy`, hooks) that the current `Crawl4AIBackend`
   doesn't use. We're paying LLM costs for what should be a free CSS
   extraction.
3. **9 browser skills** (browserbase, browserbase-cli, stagehand,
   cookie-sync, safe-browser, firecrawl-crawl, firecrawl-scrape,
   firecrawl-monitor, firecrawl-interact) violate the
   `infrastructure-stacks/spec.md` mandate of "exactly 3 entry points:
   browser-tools router + the 2 Firecrawl variants".
4. **The `sruth_browser` Python module** is the last major code unit
   that retains the `sruth_` prefix; v4 consolidation renamed most
   others to `cianfhoghlaim.*`.
5. **The browser stack YAML files** live in `bonneagar/` (the v4
   worktree split) but the Python code lives in `cianfhoghlaim/`.
   Bug fixes need 2 PRs. This is intentional per the worktree split,
   but should be documented.

## What Changes

### 1. Kill browserbase

Remove `BrowserbaseBackend`, `BackendType.BROWSERBASE_MCP`,
`browserbase_*` env vars, and the `.agents/skills_backup/browserbase*`
references. (No credits, no replacement plan.)

### 2. Cut to 3 backends, then add Skyvern + Stagehand back as opt-in

Final state: 5 backends (Crawl4AI + Firecrawl + 1 self-hosted
Playwright + Skyvern opt-in + Stagehand opt-in). The cut-to-3
intermediate state is safer (less surface area during the rename).

### 3. Wire new Crawl4AI 0.7.4 features

`JsonCssExtractionStrategy` (zero-cost for known-structure pages),
`LLMExtractionStrategy` with Pydantic schema (type-safe structured
extraction), `use_managed_browser=True` for auth, deep-crawl
strategies, hooks. Replaces expensive BAML extractions for
known-structure sources (NCCA, SEC, DES, Apple Award CVs).

### 4. Consolidate browser skills to 3 entry points

Per `infrastructure-stacks/spec.md`:
- `browser-tools` (router, NEW) — the 6-tool table + decision tree + KCG safety rules
- `firecrawl` (MCP, existing) — focused on the MCP variant only
- `firecrawl-cli` (Bash, NEW) — the Bash CLI variant

Delete `.agents/skills_backup/{browserbase, browserbase-cli,
stagehand, cookie-sync, safe-browser, firecrawl-crawl,
firecrawl-scrape, firecrawl-monitor, firecrawl-interact, firecrawl-batch,
firecrawl-download, webmcp-gen, firecrawl-build, firecrawl-build-scrape,
firecrawl-build-search, firecrawl-build-interact, firecrawl-build-onboarding,
firecrawl-research-index, autobrowse, agent-experience, ui-test,
web-reader, fetch, search, functions, cookie-sync, webmcp-gen,
autobrowse, agent-experience, ui-test, fetch, search, functions}`.
Absorb their content into the router or the 2 kept Firecrawl skills.

### 5. Rename `sruth_browser` → `browser`

Full v4 cleanup. `mv cianfhoghlaim/core/browser/sruth_browser/
cianfhoghlaim/core/browser/browser/`. Update 50+ import sites via
`sed`. The DLT sources (firecrawl_source.py) already use the v4
absolute path `from cianfhoghlaim.core.browser.X import ...` so
only the test files + internal cross-references need updating.

### 6. DAG-first integration

Create `defs/browser/` Component at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/browser/` with
4 sub-defs:
- `defs.yaml` (the DltLoadCollectionComponent for bulk ingestion)
- `crawl4ai_defs.yaml` (the new Crawl4AI App component)
- `firecrawl_defs.yaml` (the Firecrawl fallback Component)
- `auth_defs.yaml` (the Skyvern+Stagehand opt-in Component)

Then wire into the 4 existing Dagster asset groups:
`author_archive_assets.py` (ScrapeStrategist → browser.ScrapeStrategist),
`leabharlann_inbox_assets.py` (add `browser.web_search` for each
research link), `croilar_cv_extraction.py` (replace per-source browser
calls with `BrowserClient`), `author-archive-cross-corpus-kg` (use
the new `Crawl4AI.batch_extract`).

## Tasks

See `tasks.md` for the 6-phase plan (A: DAG, B: kill browserbase,
C: skills, D: backends, E: Crawl4AI features, F: rename + archive).

## Validation

- `openspec validate 2026-06-29-browser-stack-crawl4ai-refactor --strict` passes
- `uv run pytest cianfhoghlaim/core/browser/tests/` passes
- `python3 -c "from cianfhoghlaim.core.browser import BrowserClient, ScrapeStrategist"` succeeds
- 5 dagster asset groups reference the new `defs/browser/` Component
- `mise run lint:skills` passes (3 browser skills: browser-tools, firecrawl, firecrawl-cli)
