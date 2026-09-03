# DEPRECATED — Migrated to `notebooks/irish_law.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 6 Irish law sub-notebooks have been consolidated
into the single grouped marimo dashboard
[`notebooks/irish_law.py`](../../irish_law.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `11_irish_law_01_personal_injury_journey.py` | Personal Injury |
| `11_irish_law_02_courts_index.py` | Courts Index |
| `11_irish_law_03_wrc_decision_search.py` | WRC Decisions |
| `11_irish_law_04_citizensinfo_rights.py` | Citizens Info |
| `11_irish_law_05_gov_ie_law_corpus.py` | Gov.ie Law |
| `11_irish_law_06_unified_cross_source_query.py` | Unified Search |

## How to run

```bash
marimo edit notebooks/irish_law.py
python notebooks/irish_law.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.