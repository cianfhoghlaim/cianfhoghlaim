# Change: Web Stack Skill + Test Audit v1

## Why

Plan 11 (web stack deep audit) verified the production web surface
inventory and confirmed the 4 canonical web apps + CopilotKit route
mounts are intact after the Phase 16-29 disaster.

1. **Web surface inventory**:
   - 14 web apps in web/apps/ (4 canonical from agentic-frontend-frameworks skill)
   - 32 package.json files (workspace structure)
   - 48 Hono API route .ts files (including CopilotKit)
   - A2UISurfaceGenerator.tsx restored (was lost in disaster, restored in Plan 58)

2. **No web-stack-specific tests**: The 48 Hono API routes + 14 web
   apps + A2UI surface had no health tests

This change adds 10 smoke tests covering the web stack surface and
the agentic-frontend-frameworks umbrella skill.

## What Changes

### 1. Web stack health tests
- `tests/webstack/__init__.py`: new test package
- `tests/webstack/test_webstack.py`: 10 tests
  - `test_hono_api_package_exists` — @cianfhoghlaim/hono-api present
  - `test_hono_api_routes_count` — ≥30 Hono API .ts files
  - `test_hono_api_copilotkit_routes` — lc, jc, a-level, gcse exist
  - `test_a2ui_surface_generator_exists` — restored component present
  - `test_web_apps_count` — ≥10 web apps
  - `test_canonical_web_apps_present` — 4 canonical apps (cianfhoghlaim-web, croilar-web, croilar-portal, tuatha-ui)
  - `test_hono_api_index_module_compiles` — index.ts imports Hono
  - `test_web_package_workspaces` — pnpm or bun workspaces
  - `test_hono_api_image_generation_route` — image-generation.ts
  - `test_agentic_frontend_skill_present` — umbrella skill exists

## What Does NOT Change

- ❌ No new web apps added
- ❌ No Hono API routes modified
- ❌ No A2UI component changes
- ❌ No CopilotKit route additions
- ❌ No deployment configuration changes

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 6 (Google ADK) — the web stack consumes agent fleet

## Cross-links

- Sister change: `2026-09-13-education-sources-test-audit-v1` (Plan 10)
- Sister change: `2026-09-13-lakehouse-skill-and-test-audit-v1` (Plan 9)
- Sister change: `2026-09-13-firecrawl-skill-and-test-audit-v1` (Plan 8)
- Sister change: `2026-09-13-marimo-skill-and-test-audit-v1` (Plan 7)
- Sister change: `2026-09-13-google-adk-skill-and-test-audit-v1` (Plan 6)
- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
