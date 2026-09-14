# Change: Lakehouse Skill + Test Audit v1

## Why

Plan 9 (Lakehouse deep audit) revealed destination code location drift and documentation gaps:

1. **Destination code moved**:
   - `dlt_sources/lakehouse/` is empty (only `__pycache__/`)
   - The actual destination dispatch is in `dlt_sources/common/`:
     - `destinations_cianfhoghlaim.py` (the 3-tier dispatch)
     - `destinations_tuatha.py`
     - `motherduck_options.py`
     - `named_destinations.py`

2. **No Lakehouse-specific tests**:
   - No tests verify the 99 bonneagar stacks
   - No tests verify the 3-tier destination dispatch
   - No tests verify the 3 lakehouse-related skills (ducklake, lancedb, motherduck)

This change updates the 3 lakehouse skills + adds 9 smoke tests covering the destination layer and the 99-stack bonneagar surface.

## What Changes

### 1. Skill updates
- `.agents/skills/motherduck/SKILL.md`: adds CURRENT STATUS with 99-stack breakdown + destination code location (dlt_sources/common/)
- `.agents/skills/ducklake/SKILL.md`: adds brief CURRENT STATUS note
- `.agents/skills/lancedb/SKILL.md`: adds brief CURRENT STATUS note

### 2. Lakehouse health tests
- `tests/lakehouse/__init__.py`: new test package
- `tests/lakehouse/test_lakehouse.py`: 9 tests
  - `test_bonneagar_stacks_count` — ≥50 production stacks
  - `test_dlt_motherduck_extra_installed` — dlt installed
  - `test_dlt_common_destinations_module_exists` — named_destinations.py present
  - `test_dlt_common_motherduck_options_exists` — motherduck_options.py present
  - `test_lakehouse_bonneagar_stack_exists` — lakehouse/ stack exists
  - `test_lakehouse_stack_uses_ducklake` — compose references ducklake
  - `test_motherduck_token_env_var` — env var documented
  - `test_lakehouse_skills_all_three_exist` — 3 lakehouse skills
  - `test_lakehouse_dlt_uses_3tier_dispatch` — destinations_cianfhoghlaim.py

## What Does NOT Change

- ❌ No new stacks added
- ❌ No destination code modified
- ❌ No DuckLake 1.0 features adopted (data inlining, bucket partitioning)
- ❌ No FalkorDB graph rebuild (deferred to Plan 8 Firecrawl re-do)

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 1 (DLT) + Plan 8 (Firecrawl)

## Cross-links

- Sister change: `2026-09-13-firecrawl-skill-and-test-audit-v1` (Plan 8)
- Sister change: `2026-09-13-marimo-skill-and-test-audit-v1` (Plan 7)
- Sister change: `2026-09-13-google-adk-skill-and-test-audit-v1` (Plan 6)
- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
