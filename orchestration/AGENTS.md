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
mise run sync:dagster                # Layer 6: validate ~833 Dagster assets via AST parsing
mise run lint:drift-docs             # Anti-drift lint (validates every AGENTS.md number claim)
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `orchestration/definitions.py` | The consolidated code-location entry-point (199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks) |
| `orchestration/defs/` | The 5-layer `defs/` tree (`1_ingestion/`, `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/`) |
| `orchestration/defs/sync_assets.py` | The `sync_health` asset + Layer 6 metadata emitter |
| `orchestration/automation/sync_schedules.py` | The `0 */4 * * *` cron that materialises `sync_health` |
| `orchestration/components/` | The 5 KCG Dagster Components (Declarative Automation + State-Backed) |
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

<!-- generated: 2026-07-29; do not hand-edit -->
