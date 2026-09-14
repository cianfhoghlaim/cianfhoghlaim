# Change: Firecrawl Skill + Test Audit v1

## Why

Plan 8 (Firecrawl deep audit) revealed documentation gaps and an
incomplete monitor pipeline:

1. **Skill missing current status**: Both `firecrawl/SKILL.md` (meta) and
   `firecrawl-cli/SKILL.md` (Bash) lacked a CURRENT STATUS section
   documenting the 4 monitor configs + the upstream-blog → cocoindex → KG pipeline

2. **Incomplete pipeline**: The 4 monitor configs scrape upstream blogs
   but the downstream CocoIndex App (`upstream_api_surface_app`) that
   would extract `ApiChange` records was lost in the Phase 16-29 disaster

3. **No Firecrawl-specific tests**: No tests verify MCP config, monitor
   configs, or skill content

This change updates the meta-skill + adds 8 smoke tests covering the
Firecrawl surface and the monitor pipeline state.

## What Changes

### 1. Skill update
- `.agents/skills/firecrawl/SKILL.md`:
  - Adds "⚠️ CURRENT STATUS" section with 4 monitor configs + MCP
    server config + lost CocoIndex App note

### 2. Firecrawl health tests
- `tests/firecrawl/__init__.py`: new test package
- `tests/firecrawl/test_firecrawl.py`: 8 tests
  - `test_firecrawl_mcp_configured` — .mcp.json has firecrawl entry
  - `test_firecrawl_monitor_configs_present` — all 4 YAMLs exist
  - `test_firecrawl_monitor_configs_valid_yaml` — valid YAML schema
  - `test_firecrawl_mcp_client_imports` — wrapper imports
  - `test_firecrawl_skills_both_exist` — firecrawl + firecrawl-cli skills
  - `test_firecrawl_bunx_available` — bunx available for MCP
  - `test_firecrawl_meta_skill_references_monitor_pipeline` — meta-skill
    mentions the upstream-blog → cocoindex → KG pipeline
  - `test_firecrawl_cli_documents_12_subcommands` — CLI skill covers 12

## What Does NOT Change

- ❌ No new monitor configs added
- ❌ No upstream_api_surface_app CocoIndex App re-created (lost Phase 16-29)
- ❌ No FalkorDB graph rebuild
- ❌ No new Firecrawl tools wrapped

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 4 (CocoIndex) — monitor pipeline feeds cocoindex

## Cross-links

- Sister change: `2026-09-13-marimo-skill-and-test-audit-v1` (Plan 7)
- Sister change: `2026-09-13-google-adk-skill-and-test-audit-v1` (Plan 6)
- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
