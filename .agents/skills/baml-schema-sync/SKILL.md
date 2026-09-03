---
name: baml-schema-sync
description: "Layer 7 of the knowledge-sync-loop — the BAML schema surface validator. Use when the user asks 'are the BAML schemas healthy', 'is the baml-cli test passing', 'what BAML functions exist', 'is the baml_schemas Cognee cluster populated', 'how many BAML clients do we have', or 'what does sync:baml do'. Per the 2026-08-15-baml-sync-loop-v1 change. Triggers: 'sync:baml', 'sync:baml-drift', 'sync:baml-ccc', 'sync:baml-cognee', 'sync:baml-test', 'sync:baml-lint', 'baml_schemas', 'baml-function-search', 'baml_client', 'minimax-m3', 'clients.baml', 'clients_biep_v3.py'."
---

# BAML Schema Sync (Layer 7 of the knowledge-sync-loop)

> **The Layer 7 of the 6-layer pull-based sync architecture from `2026-08-15-knowledge-sync-loop-v1`. Validates the 320 .baml files (558 functions + 838 classes + 288 enums + 33 LLM clients) + closes the biggest remaining gap in the sync loop.**

## Why Layer 7?

The 6-layer architecture from `2026-08-15-knowledge-sync-loop-v1` (extended by
`2026-08-15-retroactive-pre-v7-cleanup-v1` to include Layer 6 — Dagster) covered 9
of the 14 knowledge surfaces identified in the reconnaissance. The biggest
remaining gap was the **BAML extraction schema surface** — the 320 .baml files
that are the schema source for every extraction function in the platform.

BAML drift is silent (no test catches `baml-cli generate` drift), and the
schema is the backbone of the data pipeline. Drift in `.baml` files propagates
to every downstream consumer (DLT sources, Dagster assets, agents). Layer 7
closes this gap.

## What Layer 7 covers

`bash scripts/sync/baml.sh` walks the 7 BAML clusters + the 3 top-level BAML
files + produces a per-cluster report to `stedding/sync-reports/baml-{date}.md` with:
- `.baml` file count per cluster (american_nations + british_isles + celtic +
  commonwealth + european_nations + european_union + processing)
- `function` / `class` / `enum` / `client<llm>` / `test` counts per cluster
- The top-level BAML files (clients.baml + clients_llama_swap.baml +
  clients_ocr_ensemble.baml + clients_biep_v3.py + baml.toml + README.md)
- Drift detection (gemma-3-4b-it + gemma-3-27b-it should be 0 after the
  model-registry cleanup)

The orchestrator `mise run sync:baml` runs all 5 sub-layers + writes a unified
report to `stedding/sync-reports/baml-all-{date}.md`.

## The 5 sub-layers

| Sub-layer | Task | What it does |
|:--|:--|:--|
| 1 | `sync:baml-drift` | Detects reference + syntax drift (historical Gemma 3 refs, duplicate names) |
| 2 | `sync:baml-ccc` | Appends the 22nd CCC concept guide (baml-function-search) + reindex |
| 3 | `sync:baml-cognee` | Ingests the 320 .baml files into the 11th Cognee cluster (baml_schemas) |
| 4 | `sync:baml-test` | Runs `baml-cli test` on the 11 test blocks |
| 5 | `sync:baml-lint` | BAML lint gate (client references + model drift) |

## The new artifacts

| Artifact | File | Purpose |
|:--|:--|:--|
| `baml-schema-sync` skill | `.agents/skills/baml-schema-sync/SKILL.md` | this file |
| 22nd CCC concept guide | `.cocoindex_code/guides.yml` | `baml-function-search` |
| 11th Cognee cluster | `baml_schemas` | the 320 .baml files |
| `baml_sync_health` asset | `orchestration/defs/sync_assets.py` | Dagster asset |
| `scripts/cognee_ingest_baml_schemas.py` | the canonical ingestor |
| `notebooks/sync_health.py` (BAML tab) | the Layer 7 dashboard |

## BAML evolution feedback loop

The system grows its knowledge surface over time via the BAML evolution
feedback loop:

```
.baml file modified
  → sync:baml-cognee detects the change (via file mtime)
  → re-cognifies the modified file into the baml_schemas cluster
  → sync:baml-ccc updates the 22nd concept guide
  → The deployment control panel (notebook 24) surfaces the change
```

## Quick routing

| If you want to... | Do this |
|:--|:--|
| Check the BAML schema health | `mise run sync:baml` |
| See the per-cluster breakdown | `cat stedding/sync-reports/baml-$(date +%Y-%m-%d).md` |
| Add a new BAML function | Create the .baml file with `function` + `client X` + run `sync:baml` |
| Fix a BAML drift | `sync:baml` will show the broken file; fix + re-run |
| See the BAML sync dashboard | Open `notebooks/sync_health.py` (BAML tab) |
| Run the BAML tests | `mise run baml:test` (the canonical entry point) |

## Cross-references

- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (this change)
- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/` (Layer 6 extension)
- `baml_src/` (the 320 .baml files)
- `baml_src/clients.baml` (the canonical 33 LLM clients)
- `baml_src/clients_biep_v3.py` (the Python spec for the BIEP v3 clients)
- `scripts/sync/` (the 8 sync scripts)
- `.agents/skills/knowledge-sync-loop/SKILL.md` (the parent sync loop skill)
- `.agents/skills/dagster-asset-sync/SKILL.md` (the Layer 6 skill)