# `notebooks/` — Marimo Lakehouse Dashboards

> **The 108 active marimo notebooks for the British-Isles Education Pipeline (BIEP).** Each notebook is a reactive dashboard AND a standalone CLI script (dual-mode). The canonical entry-point is `notebooks/_shared/schema.py` (5 introspection helpers) + `00_control_panel.py` (the 5-tab deployment control panel that reads/writes `deployment-choice.yaml`).

## Routing

Load this AGENTS.md when:

- You need to add / modify a BIEP dashboard (per-subject, per-jurisdiction, per-language)
- You need to query the BIEP lakehouse via the 5 introspection helpers
- You need to regenerate the WASM-exported marimo bundles
- You need to inspect the deployment control panel state

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run notebook:control-panel     # Open the 5-tab deployment control panel (Models/Pipelines/Datasets/Stacks/Registry)
mise run notebook:list              # List all 108 active marimo notebooks
mise run notebook:smoke             # Smoke-test the canonical nb_utils helpers
mise run biep:v3:marimo:wasm:export # Export all 7 BIEP v3 jurisdiction dashboards to WebAssembly
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `notebooks/_shared/schema.py` | The 5 introspection helpers (`schema_introspect`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`, `list_tables`) |
| `notebooks/_shared/nb_utils.py` | The canonical BIEP helpers (`connect_biep_lakehouse`, `BIEP_SUBJECTS`, `lc_subject_query`) |
| `notebooks/00_control_panel.py` | The 5-tab marimo control panel (the operator's UI) |
| `notebooks/_marimo/` | The WASM-exported marimo bundles (per-jurisdiction) |
| `notebooks/cli.py` | The standalone CLI script entry-point |

## Adjacent specs

- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 spec that drives the dashboard layout
- [`centralize-cross-cutting-docs`](../openspec/specs/centralize-cross-cutting-docs/spec.md) — the `lint:drift-docs` gate that audits the in-notebook number claims
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the marimo notebook + web UI + CLI for `deployment-choice.yaml`

## DO NOT

- **Never** use raw `duckdb.connect()` — use `ibis.duckdb.connect("md:cianfhoghlaim")` (the BIEP v3 contract is ibis-first; prefer the canonical helper `notebooks/_shared/db.py:connect_md()` over the direct connection).
- **Never** hardcode a table name — resolve via `_shared/schema.py:list_tables()`.
- **Never** ship a notebook that doesn't run as a CLI script (`marimo edit` + `python notebooks/<name>.py` both modes).

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`marimo`](../.agents/skills/marimo/SKILL.md) | Marimo reactive Python notebooks (dual-mode + WASM export) |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | The MotherDuck / DuckLake lakehouse the notebooks query |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry (the control panel reads) |
| [`ibis`](../.agents/skills/ibis/SKILL.md) | The ibis-first contract (BIEP v3 mandate) |

<!-- generated: 2026-07-29; do not hand-edit -->
