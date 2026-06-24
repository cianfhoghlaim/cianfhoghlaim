## ADDED Requirements

### Requirement: Browser tools consolidation

KCG browser / scraping / agent-on-the-web skills MUST be consolidated to exactly 3 entry points: 1 routing skill (`browser-tools`) + the 2 Firecrawl variants (MCP + Bash CLI). All upstream-specific skills (browserbase-cli, stagehand, cookie-sync, safe-browser, firecrawl-crawl, firecrawl-scrape, etc.) MUST be deleted, with their content absorbed into the router or the 2 kept Firecrawl skills.

#### Scenario: Agent picks the right browser tool

- **WHEN** an agent needs to scrape a URL, click a button, or run an autonomous agent-on-the-web task
- **THEN** the loader matches one of: `browser-tools` (router), `firecrawl` (MCP), `firecrawl-cli` (Bash)
- **AND** the 17 prior browser / firecrawl sub-skills are removed

#### Scenario: Router points to all 3 entry points

- **WHEN** `browser-tools/SKILL.md` is read
- **THEN** it contains a 6-tool table (Stagehand, Firecrawl MCP, Firecrawl CLI, crawl4ai, browser, safe-browser) + a decision tree + KCG safety rules
