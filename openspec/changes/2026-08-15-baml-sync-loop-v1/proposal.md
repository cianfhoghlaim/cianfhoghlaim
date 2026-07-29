# 2026-08-15-baml-sync-loop-v1

## Why

The 6-layer pull-based sync architecture from
`2026-08-15-knowledge-sync-loop-v1` (extended by
`2026-08-15-retroactive-pre-v7-cleanup-v1` to include Layer 6 —
Dagster) covers 9 of the 14 knowledge surfaces identified in the
reconnaissance:

| Layer | Task | Surface |
|:--|:--|:--|
| 1 | sync:paths | file paths |
| 2 | sync:ccc | code + openspec + skills (via 21st concept guide) |
| 3 | sync:cognee | 10 clusters |
| 4 | sync:skills | 56 skills |
| 5 | sync:mcp | 14 MCP servers |
| 6 | sync:dagster | 833 Dagster assets |

**Not yet covered** (4 surfaces):
- **BAML extraction schemas** (320 .baml files, 558 functions, 838
  classes, 288 enums, 33 LLM clients) — the **backbone of the data
  pipeline** but had no automated health validation
- DLT sources (928 sources)
- Agent definitions (12-agent fleet)
- Models (70+ models, covered by the model-registry change)

The BAML surface is the **most critical** of these — it's the
schema source for every extraction function in the platform. Drift
in `.baml` files (e.g. a renamed function, a deleted enum, a broken
client reference) propagates to every downstream consumer (DLT
sources, Dagster assets, agents).

This change extends the sync loop with **Layer 7 — `sync:baml`** that
validates the 320 .baml files + reports drift to the existing 5
sync surfaces (CCC, Cognee, skills, MCP, Dagster) + the deployment
control panel (notebook 24).

## What changes

### Section A — The Layer 7 sync loop (5 layers + orchestrator)

The pattern mirrors the existing 6-layer architecture:

#### A.1 — Layer 1: `sync:baml-drift` (path/syntax drift detection)

Detects pre-v7 path drift + syntax errors in the .baml files:

```bash
# Scans baml_src/**/*.baml for:
# - Reference to non-existent types/functions
# - Python type annotations not matching BAML output_type
# - Duplicate function names within the same file
# - Missing @description on output fields (the LLM contract)
# - Client references that don't exist in clients.baml
```

#### A.2 — Layer 2: `sync:baml-ccc` (CCC reindex)

Appends the **22nd concept guide** `baml-function-search` to
`.cocoindex_code/guides.yml` + runs `bun run ccc:index` for incremental
refresh.

#### A.3 — Layer 3: `sync:baml-cognee` (Cognee ingestion)

Ingests the 320 .baml files into the **11th Cognee cluster**
`baml_schemas`. New script: `scripts/sync_baml_schemas_to_cognee.py`.

#### A.4 — Layer 4: `sync:baml-test` (BAML test gate)

Runs `baml-cli test` on the 11 test blocks identified in Week 1
to validate the extraction functions work end-to-end.

#### A.5 — Layer 5: `sync:baml-lint` (BAML lint gate)

Runs the canonical BAML lint checks:
- All functions have a `client X` reference
- All clients route to canonical models (per `clients_biep_v3.py`)
- No leftover `gemma-3-4b-it` / `gemma-3-27b-it` references (the
  historical Gemma 3 model drift)

Plus the orchestrator: `sync:all` runs all 7 layers (was 6) in
sequence + writes a unified 7-layer report.

### Section B — The new artifacts

| Artifact | File | Purpose |
|:--|:--|:--|
| `sync:baml-drift` | `scripts/sync/baml-drift.sh` | Layer 1 |
| `sync:baml-ccc` | `scripts/sync/baml-ccc.sh` | Layer 2 |
| `sync:baml-cognee` | `scripts/sync/baml-cognee.sh` | Layer 3 |
| `sync:baml-test` | `scripts/sync/baml-test.sh` | Layer 4 |
| `sync:baml-lint` | `scripts/sync/baml-lint.sh` | Layer 5 |
| `sync:baml` | orchestrator | runs 1-5 in sequence |
| `baml-schema-sync` skill | `.agents/skills/baml-schema-sync/SKILL.md` | docs Layer 7 |
| 22nd CCC guide | `.cocoindex_code/guides.yml` | `baml-function-search` |
| 11th Cognee cluster | `baml_schemas` | the 320 .baml files |
| `baml_sync_health` asset | `orchestration/defs/sync_assets.py` | Dagster asset |
| `notebooks/26_baml_sync_dashboard.py` | dashboard | Layer 7 surface |
| `sync_dagster_assets_to_cognee.py` (updated) | ingest the baml_schemas cluster | |

### Section C — The 3 feedback loops (extended)

The existing 3 feedback loops (skill evolution + openspec evolution
+ MCP evolution) are preserved + extended:

- **BAML evolution loop**: When a `.baml` file is modified, the next
  `sync:baml-cognee` re-cognifies the modified file into the
  `baml_schemas` cluster + `sync:baml-ccc` updates the 22nd concept
  guide + the deployment control panel surfaces the change.

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1 (the foundation)
Blocked by (soft): 2026-08-15-retroactive-pre-v7-cleanup-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `bash scripts/sync/baml-drift.sh` reports 0 broken references
- `bun run ccc:index` succeeds + the 22nd concept guide is loaded
- `cognee-mcp` returns the 11 typed clusters (10 existing + baml_schemas)
- `mise run baml:test` runs the 11 test blocks cleanly
- `mise run sync:baml` runs all 5 layers + produces a unified report
- `mise run sync:all` runs all 7 layers (was 6) + produces a unified 7-layer report
- `mise run lint:skills` reports 57 skills pass (56 + baml-schema-sync)
- `bash scripts/bring-up-smoke-test.sh` reports "All 7 bring-up steps work"
  (updated Step 6 = sync:dagster + Step 7 = sync:baml)
- `openspec validate 2026-08-15-baml-sync-loop-v1 --strict` passes

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/` (Layer 6 extension)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (the model-registry change that consumes BAML clients)
- `baml_src/` (the 320 .baml files)
- `baml_src/clients.baml` (the canonical 33 LLM clients)
- `baml_src/clients_biep_v3.py` (the Python spec for the BIEP v3 clients)
- `scripts/sync/` (the existing 6 sync scripts)

## Estimated effort

~2 days (1 day per the 2-day rollout).