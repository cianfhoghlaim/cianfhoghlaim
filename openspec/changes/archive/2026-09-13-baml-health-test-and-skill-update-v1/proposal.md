# Change: BAML Health Test + Skill Update v1

## Why

Plan 2 (BAML deep audit) revealed that `uv run baml-cli generate --from ./baml_src`
is currently failing in the recovered tree. The 333 `.baml` files contain
many stub functions with syntax (multi-line `catch_all`, Python-style
type annotations, undefined client references) that BAML 0.226 no longer
parses cleanly.

The original Phase 16-29 work (lost in the git-filter-repo disaster)
replaced these stubs with real BAML functions referencing the canonical
clients + return types. Re-applying that work is outside Plan 2's scope.

This change documents the current state + adds regression detection so
future work can detect when:
- baml-cli version drifts from the baml-py lib version
- The 300+ .baml files regress (inventory changes unexpectedly)
- baml-cli generate starts working again (the broken-stub files were fixed)

## What Changes

### 1. Skill version bump
- `.agents/skills/baml/SKILL.md`: v0.223.0 → v0.226.1 (matches installed)
- New "⚠️ CURRENT STATUS" section documenting what's broken and what's
  needed to fully restore BAML compilation

### 2. BAML health tests
- `tests/baml/__init__.py`: new test package
- `tests/baml/test_baml_health.py`: 4 tests
  - `test_baml_cli_available`: baml-cli binary runs (accepts 0.223-0.226)
  - `test_baml_src_inventory`: 300+ .baml files + 4 canonical client files
  - `test_templates_separated_from_compilable`: templates dir documented
  - `test_baml_generation_known_to_fail`: emits a warning if baml-cli
    generate starts working (currently expected to fail)

## What Does NOT Change

- ❌ No BAML source files modified
- ❌ No baml-cli invocation scripts modified
- ❌ The 60+ broken stub files NOT fixed (out of scope — requires
  re-applying Phase 19/21/22 work)
- ❌ Templates in `baml_src/_shared/templates/` NOT moved (still valid
  per the bulk-replace stubs pattern)

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: sister changes `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1`
  (the jurisdiction orchestrators that consume baml_client functions)

## Cross-links

- Skill: `.agents/skills/baml/SKILL.md`
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
- Monitor: `docs/firecrawl/monitors/upstream_packages/dlthub_blog.yml`
  (auto-scrapes dlt + BAML ecosystem changes)
