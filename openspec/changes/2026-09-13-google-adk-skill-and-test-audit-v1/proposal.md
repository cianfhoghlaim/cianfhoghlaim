# Change: Google ADK Skill + Test Audit v1

## Why

Plan 6 (Google ADK deep audit) revealed a major version drift and
documentation gaps in the agent fleet surface:

1. **Major version drift**:
   - `.agents/skills/google-adk/SKILL.md` claims `>=2.1.0` (verified 2026-06)
   - Actual installed: `google-adk==1.17.0` (PyPI, 2026-09-12)
   - The skill numbering was wrong — 1.x is the canonical ADK line

2. **No ADK-specific tests**:
   - 12 agent files under `agents/meaisinfhoghlaim/` had no health tests
   - All agents use `try: from baml_client import b` + fallback (per Plan 2)
   - No test verifies the graceful degradation pattern

This change updates the skill + adds 8 smoke tests covering the agent
fleet surface and the BAML fallback pattern.

## What Changes

### 1. Skill update
- `.agents/skills/google-adk/SKILL.md`:
  - Version: `>=2.1.0` → `>=1.17.0` (corrected version)
  - Adds "⚠️ CURRENT STATUS" section documenting 12 agent files,
    the BAML fallback pattern, and un-adopted ADK 1.17 features

### 2. Agent fleet health tests
- `tests/google_adk/__init__.py`: new test package
- `tests/google_adk/test_google_adk.py`: 8 tests
  - `test_google_adk_lib_installed` — 1.x present
  - `test_agents_meaisinfhoghlaim_exists` — 4 sub-clusters present
  - `test_agent_modules_count` — ≥10 ADK .py files
  - `test_celtic_grammar_agent_imports` — graceful BAML degradation
  - `test_celtic_morphology_agent_imports` — same
  - `test_firecrawl_mcp_client_imports` — same
  - `test_agents_have_baml_fallback_pattern` — canonical `try: from baml_client import b`
  - `test_agent_fleet_orchestration_skill_exists` — orchestration skill present

## What Does NOT Change

- ❌ No new agent files added (deferred to Phase 16-29 re-work)
- ❌ No Agent Engine deployment (out of scope)
- ❌ No A2A protocol adoption changes
- ❌ No OpenTelemetry native observability migration

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 2 (BAML) — agents use `baml_client` if available, fallback otherwise

## Cross-links

- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
