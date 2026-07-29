# 2026-08-15-retroactive-pre-v7-cleanup-v1

## Why

The `2026-08-15-knowledge-sync-loop-v1` change (just shipped)
established a 5-layer pull-based sync architecture. The very first
sync run (`sync:paths`) immediately surfaced **1959 pre-v7 path
drift occurrences** across the 8 target subdirectories:

| Pattern | Count | Auto-fixable? |
|:--|--:|:--|
| `cianfhoghlaim/dlt/` | 1896 | ❌ Manual review (mostly in .md docs) |
| `infrastructure/stacks/` | 27 | ✅ Safe (the IaC move) |
| `sruth/cianfhoghlaim/` | 19 | ✅ Safe (the pre-v7 repo rename) |
| `cianfhoghlaim/baml/` | 16 | ❌ Manual review (some are code) |
| `infrastructure/komodo/` | 1 | ✅ Safe (the IaC move) |
| `infrastructure/iac/dagster/` | 0 | ✅ Already clean |
| **Total** | **1959** | **47 auto-fixable + 1912 manual** |

The user's choice for this change (per the planning question) was
"Retroactive cleanup + extended sync loop" with "Detect + auto-fix
safe patterns" — so this change does the **3 things**:

1. **Cleans the 47 auto-fixable occurrences** via a safe `--fix`
   mode on `sync:paths` (no human-in-the-loop, no fuzzy matching,
   `ast.parse` validation per file post-rename)
2. **Produces per-directory diagnostic reports** for the 1912
   manual occurrences (the .md docs are historical; the .py code
   references are real)
3. **Extends the sync loop with Layer 6 — `sync:dagster`** to
   validate the ~833 Dagster assets (the biggest remaining gap in
   the sync architecture; not currently covered by the 5-layer
   design)

The 1912 manual occurrences are left as-is (per the user's choice on
open question #1 — they're historical context about the pre-v7
layout, valuable as documentation of the migration). The 210 BAML
files in `baml_src/european_nations/` are left for the BAML sync
loop follow-up (per the user's choice on open question #2).

## What changes

### Section A — Retroactive cleanup of the 47 auto-fixable occurrences

#### A.1 — The safe `--fix` mode on `sync:paths`

The existing `scripts/sync/paths.sh` task gets a `--fix` flag
that:
- Runs the normal pattern detection (Layer 1)
- For the 3 safe patterns (`sruth/cianfhoghlaim/`,
  `infrastructure/stacks/`, `infrastructure/komodo/`), applies
  the rename in-place via `scripts/sync_paths_fix.py`
- Re-runs `sync:paths` to verify the count drops to the
  expected baseline (the 47 auto-fixable occurrences)
- Writes a `fix-applied` report to
  `stedding/sync-reports/paths-fix-{date}.md`

The 3 safe rename patterns:

| Old pattern | New pattern | Count |
|:--|:--|--:|
| `sruth/cianfhoghlaim/` | `.` (or specific canonical replacement) | 19 |
| `infrastructure/stacks/` | `bonneagar/stacks/` | 27 |
| `infrastructure/komodo/` | `bonneagar/komodo/` | 1 |

#### A.2 — The safe auto-fix script (`scripts/sync_paths_fix.py`)

A new Python script that:
- Reads the latest `stedding/sync-reports/paths-{date}.md`
- Filters to the 3 safe patterns
- Generates per-file sed commands (skips files with `was sruth/...pre-v7`
  annotation — which marks them as intentionally historical)
- Applies the sed in a subprocess + validates the rename
  doesn't break any imports (via `ast.parse` after the rename)
- Writes a per-file report + a `fix-applied` summary

#### A.3 — Per-directory diagnostic reports for the 1912 manual occurrences

For the 1912 `cianfhoghlaim/dlt/` + 16 `cianfhoghlaim/baml/` occurrences
that can't be auto-fixed:
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/dlt/` —
  per-file breakdown
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/baml/` —
  per-file breakdown
- These reports are the diagnostic; the cleanup is a follow-up
  change (the spec delta says "this is the diagnostic, not the cleanup")

#### A.4 — Quality gate

The change's quality gate: `mise run sync:paths` reports 0
auto-fixable occurrences post-cleanup (the 1912 .md occurrences
are excluded by the existing sync:paths design).

### Section B — Extend the sync loop with sync:dagster (Layer 6)

#### B.1 — The new layer

Add `sync:dagster` as Layer 6 of the existing 5-layer architecture.
The new layer validates:
- All `@asset` decorators have working imports
- All sensors reference existing jobs
- All asset checks reference existing assets
- Group names match the 5-layer convention
  (`1_ingestion/...`, `2_materials/...`)
- No orphaned definitions (no `@asset` with no `@asset_check` for
  the same prefix)

#### B.2 — The new script (`scripts/sync/dagster.sh`)

Walks the 5-layer `defs/` tree + uses `ast` to parse each .py file +
produces a per-group report to
`stedding/sync-reports/dagster-{date}.md`. Validates the canonical
5 KCG Components + the 5-layer group_name convention + the
decorator types.

#### B.3 — The new Cognee cluster

`dagster_assets` — cluster of the ~833 Dagster asset definitions +
their parent resources + their sensor references. New ingest
script: `scripts/sync_dagster_assets_to_cognee.py`.

#### B.4 — The new CCC concept guide

`dagster-asset-graph` — 21st concept guide; surfaces the 5-layer
defs/ tree + the dependency graph + the canonical 5 KCG Components.

#### B.5 — The new Dagster asset

`dagster_sync_health` — Dagster asset at
`orchestration/defs/sync_assets.py` that emits metadata
(asset_count, sensor_count, group_count, broken_asset_count) +
fires on every `defs/` file change via the
`dagster_assets_sensor`.

#### B.6 — The new marimo notebook

`notebooks/25_dagster_sync_dashboard.py` — the Dagster sync dashboard
(the analog of notebook 24 for the knowledge surface).

#### B.7 — The new skill

`dagster-asset-sync` — documents the Layer 6 sync loop + the new
Cognee cluster + the new CCC guide.

### Section C — Safe auto-fix mode

#### C.1 — The `--fix` flag

The existing `sync:paths` task gets a `--fix` flag that:
- Runs the normal pattern detection
- For the 3 safe patterns, applies the rename in-place
- Re-runs sync:paths to verify the count drops
- Writes a `fix-applied` report

#### C.2 — The safety check

The safe auto-fix applies ONLY to:
- `.py` files (verified via `ast.parse` post-rename)
- Patterns that match the 3 canonical renames (no fuzzy matching)
- Files that don't contain the `was sruth/...pre-v7` annotation
  (which marks them as intentionally historical)

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1 (the sync loop is the foundation)
Blocked by (soft): none
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `mise run sync:paths --fix` reports 0 auto-fixable occurrences
  post-cleanup (the 47 occurrences dropped to 0)
- `git diff --stat` shows the cleanup touched the expected 47
  files + 0 unexpected files
- `mise run sync:paths` reports the 1912 manual occurrences
  (with per-directory breakdown in the 2 reports)
- `mise run sync:dagster` produces a per-group report listing
  the ~833 assets
- `mise run sync:all` runs all 6 layers + produces a unified
  6-layer report
- `mise run lint:skills` reports 55 skills pass
  (53 + knowledge-sync-loop + dagster-asset-sync)
- `bash scripts/bring-up-smoke-test.sh` reports "All 7
  bring-up steps work" (the new sync:dagster step is added)
- `openspec validate 2026-08-15-retroactive-pre-v7-cleanup-v1
  --strict` passes

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `scripts/sync/` (the 6 sync scripts)
- `.agents/skills/knowledge-sync-loop/SKILL.md` (the doc for the sync loop pattern)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (the model-registry change that consumes the deployment control panel)
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/` (the per-directory diagnostic reports)

## Estimated effort

~2 days (1 day per the 2-day rollout).