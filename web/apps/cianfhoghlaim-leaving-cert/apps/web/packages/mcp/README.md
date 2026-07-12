# MCP Design System Server (R23)

Per `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md` Requirement **R23**.

## What it does

This MCP server exposes the Cianfhoghlaim design system (tokens + A2UI catalog + Storybook) to AI agents. It lets agents **autonomously generate, validate, and self-heal UI surfaces** without violating the design system or generating unusable code.

## The 4 tools

| Tool | Purpose |
|---|---|
| `tokens_get()` | Return the full token set (CSS + TS + JSON Schema + BAML) |
| `catalog_list()` | Return the A2UI catalog (11 components: StudyPlanCard, WeekTimeline, MilestoneBadge, ExamPaperCard, MarksBreakdownTable, KCWeightsBar, StageOverview, SubjectCard, MarimoEmbed, PdfLibraryPanel, TranslationToggle) |
| `catalog_render(component, props)` | Validate + render a component; refuses banned colours + invalid padding + unsupported subjects; returns `suggested_fix` on failure |
| `storybook_stories(component)` | Return the Storybook stories for a component |

## Usage

```bash
# Smoke test (no MCP SDK required)
python3 design-system-server.py --smoke

# Run the MCP server (requires `pip install mcp` or equivalent)
python3 design-system-server.py --port 7777

# Wire into an agent runtime (e.g. OpenCode / Claude / Cursor)
# Add this server to the agent's MCP config, then call the 4 tools.
```

## Self-heal pattern

When `catalog_render` refuses to emit a component, it returns:

```json
{
  "ok": false,
  "error": "banned_colour: #FF0000 is not a valid Cianfhoghlaim colour token",
  "suggested_fix": {
    "use_instead": "var(--ci-brand-primary)  // or any --ci-* token",
    "available_tokens": { /* all 74 CSS tokens */ }
  }
}
```

An AI agent reads `suggested_fix`, retries with the suggested props, and gets a success. This is the canonical **machine-readable self-heal** loop for the Cianfhoghlaim design system.

## Files

| File | Purpose |
|---|---|
| `design-system-server.py` | The MCP server (this directory) |
| `../src/styles/tokens.css` | Single source of truth (74 CSS custom properties) |
| `../src/styles/tokens.ts` | TypeScript mirror (typed accessors: `tokenColor()`, `tokenValue()`) |
| `../src/styles/tokens.schema.json` | JSON Schema (A2UI catalog validation) |
| `../../baml_src/design_tokens.baml` | BAML classes (agent-visible tokens) |

## Validation

```bash
cd apps/web
bun run tokens:validate   # exits 0 if all 4 sources are drift-free
```

## Architecture

```
                       ┌─────────────────────────────────┐
                       │  Machine-readable design tokens │
                       │  (CSS + TS + Schema + BAML)     │
                       └───────────────┬─────────────────┘
                                       │
                                       ▼
                       ┌─────────────────────────────────┐
                       │  design-system-server.py (this) │
                       │                                 │
                       │  4 tools:                       │
                       │   - tokens_get()                 │
                       │   - catalog_list()               │
                       │   - catalog_render()             │
                       │   - storybook_stories()          │
                       └───────────────┬─────────────────┘
                                       │
                                       ▼
                       ┌─────────────────────────────────┐
                       │  AI agent runtime               │
                       │  (OpenCode / Claude / Cursor)   │
                       └───────────────┬─────────────────┘
                                       │
                                       ▼
                       ┌─────────────────────────────────┐
                       │  A2UI surfaces                  │
                       │  (CopilotKit v2 emit + render)  │
                       └─────────────────────────────────┘
```

## See also

- `openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md` — R21 + R22 + R23
- `.agents/skills/mcp-apps-builder/SKILL.md` — MCP server patterns (from opencode/skills)
- `.agents/skills/copilotkit/skills/a2ui-renderer/SKILL.md` — A2UI declarative surfaces
