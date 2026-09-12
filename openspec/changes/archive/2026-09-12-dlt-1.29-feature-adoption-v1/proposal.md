# Change: DLT 1.28/1.29 Feature Adoption v1

## Why

The dlt dependency in `pyproject.toml` was pinned to `dlt[duckdb,motherduck,filesystem]>=1.28.1`
but the actual installed version was **dlt 1.29.1** (released Sep 2026). Several
features introduced in dlt 1.27–1.29 were not adopted:

1. **`dlt[hub]` plugin split (1.27.0)** — the `hub` extra was not in our dep,
   blocking `dlt dashboard`, `dlt pipeline ... show`, `dlt pipeline ... mcp`,
   and `dlthub ai` (renamed from `dlt ai` in 1.27+).
2. **`refresh` > `replace` (1.28.0)** — the `write_disposition='replace'`
   parameter was deprecated in favor of `refresh=`. 29 sources still used
   `replace` (all in safe-to-migrate categories).
3. **dlt 1.28+ verifier drift** — the `.agents/skills/dlt/SKILL.md` was
   last verified 2026-06-29 against dlt 1.28.1; newer 1.29.x features
   (Polars `LazyFrame` yield, Lance REST namespace, `dlt.Relation.join`)
   were not documented.
4. **No smoke tests** for the 22 curated sources — a single bad
   `__init__.py` would break the import chain for the entire CLI.

This change adopts all four items.

## What Changes

### 1. Adopt `dlt[hub]` extra
- Update `pyproject.toml`: `dlt[duckdb,motherduck,filesystem]>=1.28.1`
  → `dlt[duckdb,motherduck,filesystem,hub]>=1.28.1`
- New packages installed: `dlthub==0.29.0`, `dlthub-client==0.28.4`,
  `croniter`, `cron-descriptor`
- New CLI binaries available at `.venv/bin/`: `dlt`, `dlthub`

### 2. Migrate `write_disposition='replace'` → `refresh='drop'`
- 29 source files migrated (all safe-to-drop per the per-source guide
  in `.agents/skills/dlt/SKILL.md`)
- Categories touched: defi/crypto, statistics, filesystem, language,
  education source discovery, scotland benchmarking, github code search,
  portfolio

### 3. Update dlt skill + AGENTS.md
- `.agents/skills/dlt/SKILL.md`: updated to dlt 1.29.1, added the
  per-source migration guide, added `dlt[hub]` + verified-source-first rules
- `dlt_sources/AGENTS.md`: added dlt 1.29+ commands + the per-source
  migration guide

### 4. Add per-source smoke tests
- `tests/dlt/__init__.py`: new test package
- `tests/dlt/test_curated_sources.py`: 4 tests with 25+1+1 = 27
  test instances covering:
  - Path existence for each of 25 curated sources
  - Import smoke test for each
  - DLT_SOURCES ↔ CURATED_SOURCE_PATHS consistency
  - `write_disposition='replace'` regression guard (was xfail, now passes)

## What Does NOT Change

- ❌ DLT source content — none of the 22 sources had their extraction
  logic changed
- ❌ Destination dispatch — `dlt_sources/lakehouse/` is empty in the
  recovered tree; destination logic lives in `bonneagar/stacks/`
- ❌ The 22 curated source file paths — paths verified by tests
- ❌ Existing migrations — `dlt_sources/_shared/` migrations unchanged

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: `docs/cocoindex/examples/docs_to_knowledge_graph/` shows
  the upstream-blog → cocoindex → knowledge-graph pattern that's deferred
  to Phase 6 (firecrawl→cocoindex pipeline)

## Cross-links

- Skill: `.agents/skills/dlt/SKILL.md` (now 1.29.1)
- Monitor: `docs/firecrawl/monitors/upstream_packages/dlthub_blog.yml`
  (30-min cadence for dlt API change detection)
- Sister change: `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1`
  (the jurisdiction orchestrators that wrap these dlt sources)
