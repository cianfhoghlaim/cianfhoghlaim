# dual-search-architecture Specification

## Purpose
TBD - created by archiving change 2026-08-14-firecrawl-mcp-ccc-dual-search-v1. Update Purpose after archive.
## Requirements
### Requirement: ccc search precedes any grep/find
The system SHALL enforce that every agent session runs `bun run ccc:search` before any `grep` or `find` call (existing convention — formalised here).

#### Scenario: agent searches for a symbol
- **WHEN** an agent receives a query about a symbol, function, or pattern in the codebase
- **THEN** the agent SHALL run `bun run ccc:search "<query>"` first
- **AND** only fall back to `grep`/`find` when ccc returns 0 hits

### Requirement: Firecrawl MCP search complements ccc search
The system SHALL provide `firecrawl_search` as the canonical external search surface.

#### Scenario: agent needs upstream package state
- **WHEN** `ccc:search` returns <3 hits OR the query references an upstream package (e.g. "Dagster", "BAML", "CocoIndex")
- **THEN** the agent SHALL run `firecrawl_search` with `categories: ["developer"]`
- **AND** log both queries to Langfuse (per the agent-observability skill)
- **AND** the Langfuse trace MUST include both tool names in the same session

#### Scenario: agent needs primary-source answer
- **WHEN** the agent needs to find a GitHub issue / merged PR / README snippet for an upstream package
- **THEN** the agent SHALL use `firecrawl_developer_search` (the Developer Index MCP tool)
- **AND** cite the URL in the agent's output

#### Scenario: agent needs academic literature
- **WHEN** the agent needs to find papers, read passages, or follow citations (biomedical, life-science, arXiv)
- **THEN** the agent SHALL use `firecrawl_research_search_papers` + `firecrawl_research_inspect_paper` + `firecrawl_research_read_paper` (the Research Index MCP tools)
- **AND** cite the `paperId` in the agent's output

### Requirement: every dependency version is verified fresh
The system SHALL cite at least one `firecrawl_search` or `firecrawl_scrape` URL in every openspec change that pins a dependency version.

#### Scenario: openspec change pins a new version
- **WHEN** an openspec change adds or modifies a `pyproject.toml` / `package.json` / `mise.toml` version pin
- **THEN** the proposal.md SHALL include a `## Upstream verification` section with ≥1 firecrawl_search result
- **AND** the URL SHALL resolve to the upstream changelog / release notes (not a marketing page)

### Requirement: 5 new concept guides in .cocoindex_code/guides.yml
The system SHALL add 5 firecrawl-related guides to `.cocoindex_code/guides.yml` (entries 27-31).

#### Scenario: agent searches for firecrawl concept
- **WHEN** the agent runs `bun run ccc:search "firecrawl search"` or `bun run ccc:search "firecrawl mcp tools"`
- **THEN** the result SHALL include the corresponding concept guide
- **AND** the result SHALL point to a real on-disk file path (per `mise run lint:guides-yml`)

#### Scenario: bring-up smoke test verifies the 5 guides
- **WHEN** `scripts/bring-up-smoke-test.sh` runs
- **THEN** the script SHALL grep for `firecrawl-search` in `.cocoindex_code/guides.yml`
- **AND** exit 0 only when the guide is present

### Requirement: FirecrawlMCPClient wraps all 12 MCP tools
The system SHALL provide a `FirecrawlMCPClient` class at `agents/meaisinfhoghlaim/firecrawl_mcp/client.py` that wraps all 12 Firecrawl MCP tools with Pydantic response models + Langfuse `@observe` decorators.

#### Scenario: agent calls FirecrawlMCPClient.search
- **WHEN** the agent calls `FirecrawlMCPClient.search(query="...", limit=5)`
- **THEN** the call SHALL be wrapped in `@observe(name="firecrawl_search")` from `langfuse.decorators`
- **AND** the response SHALL be validated against a Pydantic model
- **AND** a row SHALL be emitted to `cianfhoghlaim.firecrawl_meta.scrapes` (when the table exists — Phase 4a creates it)

#### Scenario: agent calls FirecrawlMCPClient.scrape with PII flag
- **WHEN** the agent calls `FirecrawlMCPClient.scrape(url="...", redact_pii=True, zero_data_retention=True)`
- **THEN** the MCP call SHALL include `redactPII: true` and `zeroDataRetention: true`
- **AND** the response metadata SHALL record both flags

