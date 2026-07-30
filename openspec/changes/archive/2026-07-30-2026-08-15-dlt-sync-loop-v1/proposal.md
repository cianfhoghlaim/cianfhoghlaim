# 2026-08-15-dlt-sync-loop-v1

## Why

The 8-layer pull-based sync architecture (knowledge-sync-loop-v1 +
3 follow-ups for path drift, Dagster, BAML, stacks) covers 11 of
the 14 knowledge surfaces. The next-biggest remaining gap is the
**DLT sources surface** — the 928 DLT source files (`@dlt.source`
+ `@dlt.resource`) in 13 jurisdiction subdirs at `dlt_sources/`.

DLT source drift is silent: when a developer adds a new
`@dlt.resource(name=...)` but uses a stale `write_disposition` or
references a destination that's no longer in the catalog, the
breakage doesn't surface until the next pipeline run. The 13
subdirs each have their own patterns, and there's no canonical
check that they all conform to the `dlt_sources/common/` helpers.

This change extends the sync loop with **Layer 9 - sync:dlt** that
closes the DLT sources gap: detects drift + extracts source
metadata + cognifies into Cognee + indexes in CCC + adds a new
Dagster asset + a new marimo notebook + a new skill.

## What changes

### Section A - The Layer 9 sync loop (5 layers + orchestrator)

#### A.1 - Layer 1: sync:dlt-drift (drift detection)

Detects DLT source drift across the 928 files:
- @dlt.source(name=...) duplicates (same name in 2+ files)
- @dlt.resource(name=...) duplicates
- Stale write_disposition="replace" (should be merge)
- Stale destination references

#### A.2 - Layer 2: sync:dlt-ccc (CCC reindex)

Appends the 24th concept guide dlt-source-search to
.cocoindex_code/guides.yml + runs bun run ccc:index.

#### A.3 - Layer 3: sync:dlt-cognee (Cognee ingestion)

Ingests the 928 DLT source files into the 13th Cognee cluster
dlt_sources. New script: scripts/cognee_ingest_dlt_sources.py.

#### A.4 - Layer 4: sync:dlt-test (DLT dry-run)

Runs dlt pipeline ... --dry-run on a sampling of the 13
subdirs to validate the pipeline definitions.

#### A.5 - Layer 5: sync:dlt-lint (DLT lint gate)

Reports per-jurisdiction stats + the canonical dlt_sources/common/
helpers + the 13 subdir coverage.

Plus the orchestrator: sync:all runs all 9 layers.

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1 (the foundation)
Blocked by (soft): 2026-08-15-stacks-sync-loop-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- bash scripts/sync/dlt-drift.sh reports 0 criticals
- bun run ccc:index succeeds + the 24th concept guide is loaded
- cognee-mcp returns the 13 typed clusters (12 existing + dlt_sources)
- bash scripts/sync/dlt-test.sh reports the dlt pipeline dry-run
- bash scripts/sync/dlt-lint.sh reports per-jurisdiction stats
- mise run sync:dlt runs all 5 sub-layers + produces a unified report
- mise run sync:all runs all 9 layers + produces a unified 9-layer report
- mise run lint:skills reports 59 skills pass (58 + dlt-sync)
- bash scripts/bring-up-smoke-test.sh reports "All 8 bring-up steps work"
- openspec validate 2026-08-15-dlt-sync-loop-v1 --strict passes
