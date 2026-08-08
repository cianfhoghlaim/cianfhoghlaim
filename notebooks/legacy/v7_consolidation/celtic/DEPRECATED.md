# DEPRECATED — Migrated to `notebooks/celtic_languages.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 7 Celtic languages sub-notebooks + the shared
file have been consolidated into the single grouped marimo dashboard
[`notebooks/celtic_languages.py`](../../celtic_languages.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `06_celtic_languages_01_gaois_terminology_explorer.py` | Gaois |
| `06_celtic_languages_02_duchas_folklore_with_bboxes.py` | Dúchas |
| `06_celtic_languages_03_heritage_sites_map.py` | Heritage Sites |
| `06_celtic_languages_04_canuint_dialect_player.py` | Canúint |
| `06_celtic_languages_05_ud_celtic_treebank_viewer.py` | UD Treebank |
| `06_celtic_languages_06_local_documents_subject_viewer.py` | Local Documents |
| `06_celtic_languages_07_celtic_curriculum_browser.py` | Celtic Curriculum |
| `06_celtic_languages__shared.py` | (shared helpers — now in `_shared/`) |

## How to run

```bash
marimo edit notebooks/celtic_languages.py
python notebooks/celtic_languages.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.