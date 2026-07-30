---
name: dlt-sync
description: "Layer 9 of the knowledge-sync-loop — the DLT source surface validator. Use when the user asks 'is my DLT source up to date', 'how many DLT sources do we have', 'does my DLT source use the canonical helpers', 'what does sync:dlt do', 'which DLT sources have drift'. Per the 2026-08-15-dlt-sync-loop-v1 change. Triggers: 'sync:dlt', 'dlt_sources', 'dlt-source-search', '@dlt.source', '@dlt.resource', 'dlt_sources/common', 'Layer 9'."
---

# DLT Source Sync (Layer 9 of the knowledge-sync-loop)

> **The Layer 9 of the 9-layer pull-based sync architecture from `2026-08-15-knowledge-sync-loop-v1` (extended by 4 follow-ups). Validates the 1903 .py files + 865 `@dlt.source` + 924 `@dlt.resource` across 13 jurisdiction subdirs at `dlt_sources/`.**

## Why Layer 9?

The 8-layer architecture from `2026-08-15-knowledge-sync-loop-v1` (extended by `2026-08-15-retroactive-pre-v7-cleanup-v1` for path drift + Layer 6 — Dagster, `2026-08-15-baml-sync-loop-v1` for Layer 7 — BAML, `2026-08-15-stacks-sync-loop-v1` for Layer 8 — IaC stacks) covered 11 of the 14 knowledge surfaces. The next-biggest remaining gap was the **DLT sources surface** — the 1903 .py files (865 `@dlt.source` + 924 `@dlt.resource`) in 13 jurisdiction subdirs.

DLT source drift is silent: when a developer adds a new `@dlt.resource(name=...)` but uses a stale `write_disposition="replace"` or references a destination that's no longer in the catalog, the breakage doesn't surface until the next pipeline run. The 13 subdirs each have their own patterns, and there's no canonical check that they all conform to the `dlt_sources/common/` helpers.

Layer 9 closes the DLT sources gap.

## What Layer 9 covers

`bash scripts/sync/dlt.sh` walks the 13 jurisdiction subdirs at `dlt_sources/` + produces a per-subdir report to `stedding/sync-reports/dlt-{date}.md` with:
- The per-subdir .py file counts
- The `@dlt.source` + `@dlt.resource` counts
- Drift detection (duplicate names + stale write_disposition)
- The canonical `dlt_sources/common/` helpers inventory

The orchestrator `mise run sync:dlt` runs all 5 sub-layers + writes a unified report to `stedding/sync-reports/dlt-all-{date}.md`.

## The 5 sub-layers

| Sub-layer | Task | What it does |
|:--|:--|:--|
| 1 | `sync:dlt-drift` | Detects duplicate `@dlt.source` / `@dlt.resource` names + stale `write_disposition="replace"` |
| 2 | `sync:dlt-ccc` | Appends the 24th CCC concept guide (`dlt-source-search`) + reindex |
| 3 | `sync:dlt-cognee` | Ingests the 1903 DLT sources into the 13th Cognee cluster (`dlt_sources`) |
| 4 | `sync:dlt-test` | Runs `dlt pipeline --dry-run` on a sampling of the 13 subdirs |
| 5 | `sync:dlt-lint` | Per-subdir stats (GOLD_STANDARD-style report) |

## The new artifacts

| Artifact | File | Purpose |
|:--|:--|:--|
| `dlt-sync` skill | `.agents/skills/dlt-sync/SKILL.md` | this file |
| 24th CCC guide | `dlt-source-search` | surfaces the 1903 DLT sources via CCC |
| 13th Cognee cluster | `dlt_sources` | the 1903 DLT source files |
| `dlt_sync_health` asset | `orchestration/defs/sync_assets.py` | Dagster asset |
| `scripts/cognee_ingest_dlt_sources.py` | ingestor | The canonical Cognee cluster ingestor |
| `notebooks/28_dlt_sync_dashboard.py` | dashboard | Layer 9 marimo surface |

## DLT evolution feedback loop

The system grows its knowledge surface over time via the DLT evolution feedback loop:

```
dlt source file modified
  → sync:dlt-cognee detects the change
  → re-cognifies the modified source into the dlt_sources cluster
  → sync:dlt-ccc updates the 24th concept guide
  → The deployment control panel (notebook 24) surfaces the change
```

## Quick routing

| If you want to... | Do this |
|:--|:--|
| Check the DLT source health | `mise run sync:dlt` |
| See the per-subdir breakdown | `cat stedding/sync-reports/dlt-$(date +%Y-%m-%d).md` |
| Add a new DLT source | Create the .py file in the right subdir + use the canonical `dlt_sources/common/` helpers + run `sync:dlt` |
| Fix a DLT drift | `sync:dlt-drift` will list the broken refs; fix + re-run |
| See the DLT dashboard | Open `notebooks/28_dlt_sync_dashboard.py` |
| Run the DLT pipeline dry-run | `uv run python -c "from dlt import pipeline; pipeline()"` |

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (Layer 7)
- `openspec/changes/2026-08-15-stacks-sync-loop-v1/` (Layer 8)
- `dlt_sources/` (the 1903 DLT source files)
- `dlt_sources/common/` (the canonical DLT helpers)
