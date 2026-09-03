# 2026-08-15-notebooks-sync-loop-v1

## Why

The 10-layer pull-based sync architecture (knowledge-sync-loop-v1 +
9 follow-ups for path drift, Dagster, BAML, stacks, DLT, agents)
covers 13 of the 14 knowledge surfaces identified in the
reconnaissance:

| Layer | Task | Surface |
|:--|:--|:--|
| 1 | sync:paths | file paths |
| 2 | sync:ccc | code + openspec + skills (via 21st concept guide) |
| 3 | sync:cognee | 14 clusters |
| 4 | sync:skills | 157 skills |
| 5 | sync:mcp | MCP servers |
| 6 | sync:dagster | Dagster assets |
| 7 | sync:baml | 320 .baml files |
| 8 | sync:stacks | 87 IaC stacks |
| 9 | sync:dlt | 1903 DLT sources |
| 10 | sync:agents | 188 agent files |

**Not yet covered** (1 surface):

- **Notebook files** (119 files at `notebooks/`, 20+ numeric prefixes,
  108 `@app.cell` decorators) — the **last** surface still without
  automated health validation.

The notebooks surface is **the most user-visible surface** — every
BIEP per-subject notebook + every marimo dashboard + every dev-env
demo + every educational stage notebook flows through this surface.
Notebook drift is silent: when a developer adds a new BIEP per-subdir
notebook but doesn't register it in `notebooks/cli.py` GROUPS tuple,
the `uv run python notebooks/cli.py list` command misses it. The 16
speedrun + 12 corpus + 7 educational stages + 6 dev env tools + 11
BIEP per-subdir + 7 official media + ... each have their own
patterns, and there's no canonical check that they all conform.

This change extends the sync loop with **Layer 11 — `sync:notebooks`**
that closes the notebooks gap.

## What changes

### Section A — The Layer 11 sync loop (5 sub-layers + orchestrator)

The pattern mirrors the existing 10-layer architecture:

#### A.1 — Layer 1: `sync:notebooks-drift` (registration drift)

Detects notebook registration drift across the 119 .py files:

```bash
# Scans notebooks/[0-9]*_*.py for:
# - Notebooks not registered in notebooks/cli.py GROUPS
# - Broken @app.cell decorators (AST parse failure)
# - Missing entry points
# - Stale schema references (md:oideachais after v7 rename)
```

#### A.2 — Layer 2: `sync:notebooks-ccc` (CCC reindex)

Appends the **26th concept guide** `notebook-search` to
`.cocoindex_code/guides.yml` + runs `bun run ccc:index` for incremental
refresh.

#### A.3 — Layer 3: `sync:notebooks-cognee` (Cognee ingestion)

Ingests the 119 notebook files into the **15th Cognee cluster**
`notebooks`. New script: `scripts/cognee_ingest_notebooks.py`.

#### A.4 — Layer 4: `sync:notebooks-test` (notebook import test)

Reports per-prefix notebook counts + documents the manual
`uv run python -c "import notebooks.X"` flow for import validation.

#### A.5 — Layer 5: `sync:notebooks-lint` (per-prefix stats)

Reports per-prefix .py file counts + `@app.cell` decorator counts +
the 3 canonical helpers (`notebooks/_shared`, `notebooks/cli.py`,
`notebooks/_shared/db.py`).

Plus the orchestrator: `sync:all` runs all 11 layers (was 10) in
sequence + writes a unified 11-layer report.

### Section B — The new artifacts

| Artifact | File | Purpose |
|:--|:--|:--|
| `sync:notebooks-drift` | `scripts/sync/notebooks-drift.sh` | Layer 1 |
| `sync:notebooks-ccc` | `scripts/sync/notebooks-ccc.sh` | Layer 2 |
| `sync:notebooks-cognee` | `scripts/sync/notebooks-cognee.sh` | Layer 3 |
| `sync:notebooks-test` | `scripts/sync/notebooks-test.sh` | Layer 4 |
| `sync:notebooks-lint` | `scripts/sync/notebooks-lint.sh` | Layer 5 |
| `sync:notebooks` | orchestrator | runs 1-5 in sequence |
| `notebooks-sync` skill | `.agents/skills/notebooks-sync/SKILL.md` | docs Layer 11 |
| 26th CCC guide | `.cocoindex_code/guides.yml` | `notebook-search` |
| 15th Cognee cluster | `notebooks` | the 119 notebook files |
| `notebooks_sync_health` asset | `orchestration/defs/sync_assets.py` | Dagster asset |
| `notebooks/30_notebooks_sync_dashboard.py` | dashboard | Layer 11 surface |
| `scripts/cognee_ingest_notebooks.py` | ingest the notebooks cluster | |
| `mise.toml` tasks | `sync:notebooks-drift`, `sync:notebooks-ccc`, … | the 6 orchestrator tasks |

### Section C — The feedback loops (extended)

The existing 3 feedback loops (skill evolution + openspec evolution
+ MCP evolution) are preserved + extended:

- **Notebooks evolution loop**: When a `notebooks/` file is
  modified, the next `sync:notebooks-cognee` re-cognifies the
  modified file into the `notebooks` cluster +
  `sync:notebooks-ccc` updates the 26th concept guide + the
  deployment control panel surfaces the change.

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1 (the foundation)
Blocked by (soft): 2026-08-15-agent-definitions-sync-loop-v1 (Layer 10)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `bash scripts/sync/notebooks-drift.sh` reports 0 drift occurrences
- `bun run ccc:index` succeeds + the 26th concept guide is loaded
- `cognee-mcp` returns the 15 typed clusters (14 existing + notebooks)
- `bash scripts/sync/notebooks-test.sh` reports the 119 notebook files
- `bash scripts/sync/notebooks.sh` runs all 5 layers + produces a
  unified report
- `bash scripts/sync/all.sh` runs all 11 layers (was 10) + produces
  a unified 11-layer report
- `mise run sync:notebooks` runs all 5 layers cleanly
- `mise run sync:all` runs all 11 layers cleanly
- `mise run lint:skills` reports 158 skills pass (157 + notebooks-sync)
- `bash scripts/bring-up-smoke-test.sh` reports the Layer 11 surface
  is registered
- `openspec validate 2026-08-15-notebooks-sync-loop-v1 --strict`
  passes

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-agent-definitions-sync-loop-v1/` (Layer 10)
- `openspec/changes/2026-08-15-dlt-sync-loop-v1/` (Layer 9)
- `openspec/changes/2026-08-15-stacks-sync-loop-v1/` (Layer 8)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (Layer 7)
- `notebooks/` (the 119 notebook files)
- `scripts/sync/` (the existing 10 sync scripts)

## Estimated effort

~2 days (1 day per the 2-day rollout).