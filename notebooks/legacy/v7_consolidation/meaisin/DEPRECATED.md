# DEPRECATED — Migrated to `notebooks/meaisin_ops_console.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 5 meaisin ops sub-notebooks have been consolidated
into the single grouped marimo dashboard
[`notebooks/meaisin_ops_console.py`](../../meaisin_ops_console.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `60_meaisin_ireland_ops.py` | Ireland |
| `61_meaisin_england_ops.py` | England |
| `62_meaisin_extraction_progress.py` | Extraction Progress |
| `63_meaisin_eval_dashboard.py` | RAGAS Eval |
| `64_meaisin_bilingual_curriculum.py` | Bilingual Coverage |

## How to run

```bash
marimo edit notebooks/meaisin_ops_console.py
python notebooks/meaisin_ops_console.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.