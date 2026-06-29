# Delta: infrastructure-stacks

## MODIFIED Requirements

### Requirement: 3-skill entry point for browser / scraping / agent-on-the-web

The system SHALL provide exactly 3 skill entry points for the
browser / scraping / agent-on-the-web surface (per the
consolidation rule in this spec's Purpose section).

The 3 entry points are:
- `browser-tools` (the router) — covers the decision between the
  5 backends (Crawl4AI + Firecrawl + Playwright CDP + Skyvern
  opt-in + Stagehand opt-in) + the 5 corresponding skills
  + the new Crawl4AI 0.7.4 features + the KCG safety rules
  + the opt-in pattern for Skyvern + Stagehand
- `firecrawl` (the MCP variant) — for the agent runtime integration
  with the Firecrawl MCP server
- `firecrawl-cli` (the Bash variant) — for terminal / CI / scheduled
  jobs

The `crawl4ai` skill is kept as the 4th browser skill (the
self-hosted backend reference) but is NOT counted as one of the
3 entry points per the spec mandate.

#### Scenario: An agent needs to scrape a single static page

- **GIVEN** the agent is reading the `browser-tools/SKILL.md`
- **WHEN** the user asks "scrape https://example.com to markdown"
- **THEN** the loader matches the `browser-tools` skill (the router)
- **AND** the router points to the `crawl4ai` skill
- **AND** the skill recommends `client.extract_with_css(url, schema)` (zero LLM cost)

#### Scenario: The 17 prior browser / firecrawl sub-skills are removed

- **GIVEN** the v4 + browser-stack-crawl4ai refactor is archived
- **WHEN** the developer runs `ls .agents/skills/`
- **THEN** only 3 browser-related skills remain: `browser-tools` + `firecrawl` + `firecrawl-cli` (plus the 4th `crawl4ai` for the self-hosted backend reference)
- **AND** the 17 deleted sub-skills are no longer loadable: `browserbase` + `stagehand` + `cookie-sync` + `safe-browser` + `firecrawl-crawl` + `firecrawl-scrape` + `firecrawl-monitor` + `firecrawl-interact` + `firecrawl-batch` + `firecrawl-download` + `webmcp-gen` + `firecrawl-build*` + `firecrawl-research-index` + `autobrowse` + `agent-experience` + `ui-test` + `web-reader` + `fetch` + `search` + `functions` + `browserbase-cli`

### Requirement: 5-backend Moderate strategy (3 default + 2 opt-in)

The system SHALL maintain exactly 5 browser backends per the
Moderate strategy:

1. **Crawl4AI** (self-hosted, port 11235) — default ON
2. **Firecrawl MCP** (paid fallback) — default ON
3. **Playwright CDP** (self-hosted, port 9222) — default ON
4. **Skyvern** (opt-in via `BROWSER_ENABLE_SKYVERN=1`)
5. **Stagehand** (opt-in via `BROWSER_ENABLE_STAGEHAND=1`)

Browserbase was removed 2026-06-29 (no credits, no replacement plan).
Z.AI Vision + Z.AI MCP are deprecated (the modules still exist
in `paid/` for backwards compat but are not in the public API).

#### Scenario: The browser stack registers backends on startup

- **GIVEN** the `browser` stack is running with no opt-in env vars set
- **WHEN** the FastAPI lifespan handler runs
- **THEN** the 3 default-ON backends are registered (Crawl4AI, Firecrawl, CDP)
- **AND** the 2 opt-in backends are NOT registered (Skyvern, Stagehand)
- **AND** the log shows `skyvern_disabled_enable_via_BROWSER_ENABLE_SKYVERN_1` + `stagehand_disabled_enable_via_BROWSER_ENABLE_STAGEHAND_1`

#### Scenario: The operator enables Skyvern via env var

- **GIVEN** the operator has set `BROWSER_ENABLE_SKYVERN=1` in `.env`
- **WHEN** the browser stack restarts
- **THEN** Skyvern is registered as the 4th backend
- **AND** the `SkyvernBackend` is initialized via `SkyvernAPI`
- **AND** the `config.enable_skyvern` field returns `True`
