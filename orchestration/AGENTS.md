# `orchestration/` — Cianfhoghlaim Dagster Layer

> **The 5-layer Dagster Component Architecture for Cianfhoghlaim.** Houses `definitions.py` (the consolidated code-location) + the `defs/` tree (5 layers: Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations) + `automation/` (schedules + sensors) + the canonical `sync_health` asset.

## Routing

Load this AGENTS.md when:

- You need to add / modify a Dagster asset (5-layer model)
- You need to add / modify a Dagster schedule or sensor
- You need to run a Dagster asset or materialise the lakehouse
- You need to inspect the `sync_health` cron + Layer 6 drift reports

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run dagster:dev                 # Launch the consolidated Dagster UI on :3000
mise run sync:all                    # Run all 7 sync layers (paths + ccc + cognee + skills + mcp + drift-docs + dagster)
mise run sync:dagster                # Layer 6: validate ~190 Dagster assets via AST parsing + per-group breakdown
mise run lint:drift-docs             # Anti-drift lint (validates every AGENTS.md number claim)
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `orchestration/definitions.py` | The consolidated code-location entry-point (~190 assets across 192 `defs.yaml` files + 145 Python `@asset` decorators + 8 `@sensor` + 1 `@schedule` + 54 `@asset_check`; auto-detected by `mise run sync:dagster`) |
| `orchestration/defs/` | The 5-layer `defs/` tree (`1_ingestion/`, `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/`) — 192 defs.yaml files as of Wave 0 |
| `orchestration/defs/3_model_lifecycle/cocoindex_v1/` | 96 CocoIndex v1 defs.yaml files (the L3 layer). Module paths were repaired by the 2026-08-24-wave-0-cocoindex-module-path-repair-v1 change (was: 85/96 broken, now: 0 broken) |
| `orchestration/defs/sync_assets.py` | The `sync_health` asset + Layer 6 metadata emitter |
| `orchestration/automation/sync_schedules.py` | The `0 */4 * * *` cron that materialises `sync_health` |
| `orchestration/components/` | The 5 KCG Dagster Components (Declarative Automation + State-Backed) + the per-pipeline-kind handlers |
| `orchestration/dbt_translator.py` | The dbt-to-DuckLake bridge for BIEP v3 |

## Adjacent specs

- [`dagster-5-layer-component-architecture`](../openspec/specs/dagster-5-layer-component-architecture/spec.md) — the 5-layer model this package implements
- [`knowledge-sync-loop`](../openspec/specs/knowledge-sync-loop/spec.md) — Layer 6 (sync:dagster) + cron + stale-skill alert
- [`centralize-cross-cutting-docs`](../openspec/specs/centralize-cross-cutting-docs/spec.md) — the `lint:drift-docs` gate that audits this file

## DO NOT

- **Never** import raw `duckdb.connect()` in BIEP v3 paths — use `ibis.duckdb.connect("md:oideachais")` (the BIEP v3 contract is ibis-first).
- **Never** import `cianfhoghlaim.data_platform...` from within the data platform — always relative or local package imports.
- **Never** add a new asset without registering it in `orchestration/defs/<layer>/` (no top-level `orchestration/assets.py` file).

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`dagster`](../.agents/skills/dagster/SKILL.md) | Dagster 1.13+ Declarative Automation + KCG Components |
| [`ccc`](../.agents/skills/ccc/SKILL.md) | Semantic code search across the orchestration tree |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The single source of truth for models + schemas |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | MotherDuck storage pattern (the BIEP lakehouse sink) |

## Data platform router

> **The single router for the 5 per-area data platform docs** is at [`../dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md). Documents the 6 critical conventions (relative imports / `USE_LOCAL_SCRAPES` / zero absolute namespaces / R1-R4 conformance / MODEL_REGISTRY-only / factory pattern) that apply ACROSS all 5 sub-packages.

<!-- generated: 2026-07-29; do not hand-edit -->
