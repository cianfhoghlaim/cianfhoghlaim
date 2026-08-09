# DEPRECATED — Migrated to `notebooks/sync_health.py`

Per the **2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1**
OpenSpec change, the 10 sync layer sub-notebooks have been consolidated
into the single grouped marimo dashboard
[`notebooks/sync_health.py`](../../sync_health.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `14_dev_env_tools_05_openspec_list.py` | (consolidated into Overview) |
| `14_dev_env_tools_06_mise_lint_skills.py` | Skills |
| `14_dev_env_tools_07_model_registry.py` | (consolidated into Overview) |
| `14_dev_env_tools_08_registry_drift_watch.py` | Drift Docs |
| `14_dev_env_tools_09_registry_drift_history.py` | Drift Docs |
| `14_dev_env_tools_10_deployment_choice_editor.py` | (consolidated into Overview) |
| `15_observability_01_baml_drift_audit.py` | BAML |
| `15_observability_02_irish_extraction_quality.py` | Dagster |
| `15_observability_03_cognee_knowledge_graph.py` | Cognee |
| `25_dagster_sync_dashboard.py` | Dagster |
| `26_baml_sync_dashboard.py` | BAML |
| `27_stacks_sync_dashboard.py` | Stacks |
| `28_dlt_sync_dashboard.py` | (consolidated into Dagster) |
| `29_agents_sync_dashboard.py` | Agents |
| `30_notebooks_sync_dashboard.py` | Notebooks |
| `24_deployment_control_panel.py` | (was the original 9-layer status — now superseded by `sync_health.py`'s 11-layer status grid) |

## How to run

```bash
marimo edit notebooks/sync_health.py
python notebooks/sync_health.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.