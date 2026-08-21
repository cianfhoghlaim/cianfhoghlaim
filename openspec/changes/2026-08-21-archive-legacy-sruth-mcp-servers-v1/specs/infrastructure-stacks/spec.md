# Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Historic-reference deprecation pattern for legacy MCP directories

The system SHALL support a "historic-reference deprecation" pattern
for legacy MCP server directories that:
1. Are NOT wired into any active MCP config (`opencode.json` /
   `.mcp.json`)
2. Use a pre-v7 namespace that has been renamed
3. Provide no production value (the functionality has been
   absorbed elsewhere)

A legacy directory following this pattern SHALL carry a
`_DEPRECATED.md` file at its root with:
- A top-line `# DEPRECATED — YYYY-MM-DD` marker
- A reference to the openspec change that deprecated it
- A reference to the v7-flatten change (when applicable)
- A statement of the canonical replacement (if any)
- A "DO NOT" section listing what NOT to do with the directory
- A "Cross-references" section linking to related changes

#### Scenario: A legacy sruth mcp_server directory is correctly deprecated

- **GIVEN** this change has been archived
- **WHEN** the developer runs `ls sruth/códeolas/mcp_server/`
- **THEN** the directory contains `_DEPRECATED.md` plus the historic
  `__init__.py`, `server.py`, `tools.py` files
- **AND** `_DEPRECATED.md` references this change by id
- **AND** `_DEPRECATED.md` references the
  `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`
  change

#### Scenario: The deprecated directories are NOT loaded by the agent runtime

- **GIVEN** this change has been archived
- **WHEN** the agent runtime starts and loads MCP servers from
  `opencode.json` + `.mcp.json`
- **THEN** no entry from `sruth/códeolas/mcp_server/`,
  `sruth/crypteolas/mcp_server/`, or `sruth/oideachais/mcp_server/`
  is loaded
- **AND** no import of these modules succeeds from the canonical
  Python entry points