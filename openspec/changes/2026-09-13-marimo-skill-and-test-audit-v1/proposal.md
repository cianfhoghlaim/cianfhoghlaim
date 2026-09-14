# Change: Marimo Skill + Test Audit v1

## Why

Plan 7 (Marimo deep audit) revealed count drift and documentation gaps in the notebook surface:

1. **Count drift**:
   - `.agents/skills/marimo/SKILL.md` says "6 per-subject BIEP notebooks"
   - Actual: **66 notebooks** across 6+ categories
   - The canonical 7-tab unified subject panel (`notebooks/40_leaving_cert_subject_panel.py`) is **GONE** (lost Phase 16-29 disaster)

2. **No Marimo-specific tests**:
   - The notebook surface had no health tests
   - No tests verify the shared patterns module, PEP 723 template, control panel, or BIEP lakehouse count

This change updates the Marimo skill + adds 10 smoke tests covering the notebook surface and the lost LC panel state.

## What Changes

### 1. Skill update
- `.agents/skills/marimo/SKILL.md`:
  - Description: "6 per-subject" → "66-notebook BIEP surface"
  - Adds "⚠️ CURRENT STATUS" section with 66-notebook breakdown by category + lost LC panel note

### 2. Marimo health tests
- `tests/marimo/__init__.py`: new test package
- `tests/marimo/test_marimo.py`: 10 tests
  - `test_marimo_lib_installed` — installed
  - `test_marimo_notebook_count` — ≥50 notebooks
  - `test_marimo_patterns_module_exists` — R1 setup_biep_registry_header present
  - `test_marimo_pep723_template_exists` — _pep723_template.py present
  - `test_marimo_control_panel_exists` — 00_control_panel.py present
  - `test_marimo_biep_lakehouse_notebook_count` — ≥15 BIEP lakehouse notebooks
  - `test_marimo_official_media_count` — ≥3 official_media notebooks
  - `test_marimo_lc_subject_panel_lost` — informational placeholder
  - `test_marimo_shared_db_module_exists` — _shared/db.py present
  - `test_marimo_cli_available` — marimo CLI works

## What Does NOT Change

- ❌ No new notebooks added (deferred to Plan 10 for education sources)
- ❌ `40_leaving_cert_subject_panel.py` not re-created
- ❌ No new marimo patterns adopted
- ❌ No BIEP lakehouse pipeline notebook changes

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 2 (BAML) — notebooks use baml_client if available

## Cross-links

- Sister change: `2026-09-13-google-adk-skill-and-test-audit-v1` (Plan 6)
- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
