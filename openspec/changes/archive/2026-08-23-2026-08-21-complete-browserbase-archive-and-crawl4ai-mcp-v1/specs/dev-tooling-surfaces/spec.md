# Spec Delta: dev-tooling-surfaces

## ADDED Requirements

### Requirement: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` superseded

The system SHALL recognize that the browserbase + crawl4ai MCP archive change is superseded by the active `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP). The latter covers the same scope (6 legacy MCP servers including browserbase + crawl4ai).

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up the legacy MCP archive

- **WHEN** an agent looks up the legacy MCP archive
- **THEN** the agent SHOULD load `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP)
- **AND** the older browserbase+ crawl4ai change is preserved as a historical reference