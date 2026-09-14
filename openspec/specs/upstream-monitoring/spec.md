# upstream-monitoring Specification

## Purpose
TBD - created by archiving change 2026-09-13-firecrawl-skill-and-test-audit-v1. Update Purpose after archive.

## Requirements

### Requirement: Firecrawl Skill Currency

The system SHALL keep the Firecrawl skill aligned with the actual
MCP configuration and the 4 upstream-package monitor configs.

#### Scenario: Firecrawl MCP is configured

- **WHEN** any developer runs `uv run pytest tests/firecrawl/`
- **THEN** `.mcp.json` contains a `firecrawl` entry in `mcpServers`
- **AND** the entry references `firecrawl-mcp`

#### Scenario: All 4 monitor configs are present

- **WHEN** any developer runs `uv run pytest tests/firecrawl/`
- **THEN** `docs/firecrawl/monitors/upstream_packages/` contains:
  - `dlthub_blog.yml`
  - `lancedb_blog.yml`
  - `motherduck_blog.yml`
  - `cocoindex_docs.yml`
- **AND** each is valid YAML with `name` + `targets`/`schedule` keys

#### Scenario: Firecrawl wrapper imports cleanly

- **WHEN** any developer runs `uv run pytest tests/firecrawl/`
- **THEN** `agents.meaisinfhoghlaim.firecrawl_mcp.client` imports
  (with graceful skip if optional deps missing)

#### Scenario: Both Firecrawl skills exist

- **WHEN** any developer runs `uv run pytest tests/firecrawl/`
- **THEN** `.agents/skills/firecrawl/SKILL.md` AND
  `.agents/skills/firecrawl-cli/SKILL.md` both exist

#### Scenario: bunx is available for firecrawl-mcp

- **WHEN** `which bunx` is run
- **THEN** it returns a path (bunx is required to launch firecrawl-mcp)
