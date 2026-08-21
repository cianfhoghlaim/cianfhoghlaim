# Delta: agentic-frontend-frameworks

## ADDED Requirements

### Requirement: design-system MCP server for AG-UI self-heal

The system SHALL expose the in-house design-system MCP server
(`web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py`,
513 LOC) as a first-class MCP surface for AG-UI agents.

The 4 tools SHALL be discoverable:

| Tool | Purpose |
|:--|:--|
| `tokens_get()` | Return the full design token set (CSS + TS + JSON Schema + BAML) |
| `catalog_list()` | Return the A2UI catalog (11 components: StudyPlanCard, WeekTimeline, MilestoneBadge, ExamPaperCard, MarksBreakdownTable, KCWeightsBar, StageOverview, SubjectCard, MarimoEmbed, PdfLibraryPanel, TranslationToggle) |
| `catalog_render(component, props)` | Validate + render a component; refuse banned colours + invalid padding + unsupported subjects; return `suggested_fix` on failure |
| `storybook_stories(component)` | Return the Storybook stories for a component |

This satisfies R23 of `2026-07-18-british-isles-portal-activation-v3`.

#### Scenario: An AG-UI agent renders a valid component

- **GIVEN** the design-system MCP server is running on `python design-system-server.py --port 7777`
- **AND** the `design-system` entry is wired in both `opencode.json` and `.mcp.json`
- **WHEN** an AG-UI agent calls `catalog_render(component="StudyPlanCard", props={...})` with valid props
- **THEN** the server returns `{ok: true, rendered: <component>}`
- **AND** the agent emits the rendered component to the CopilotKit UI

#### Scenario: An AG-UI agent renders an invalid component (self-heal)

- **GIVEN** the design-system MCP server is running
- **WHEN** an AG-UI agent calls `catalog_render(component="StudyPlanCard", props={colour: "#FF0000"})` (banned colour)
- **THEN** the server returns `{ok: false, error: "banned_colour: #FF0000 is not a valid Cianfhoghlaim colour token", suggested_fix: {use_instead: "var(--ci-brand-primary)", available_tokens: {...}}}`
- **AND** the agent reads `suggested_fix`, retries with the corrected props, and gets a success
- **AND** `bun run mcp:smoke:design-system` confirms the self-heal round-trip

### Requirement: design-system MCP smoke task

A `mcp:smoke:design-system` mise task SHALL validate the design-system
MCP server is reachable and the 4 tools are functional. The task
SHALL include a self-heal round-trip test (catalog_render with
banned colour → suggested_fix → retry → success).

#### Scenario: The smoke task detects a dead design-system MCP server

- **GIVEN** the design-system MCP server is not running
- **WHEN** `bun run mcp:smoke:design-system` runs as part of CI
- **THEN** the task exits non-zero
- **AND** the CI gate `mise run lint:mcp-runtime` fails the build