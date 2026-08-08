# DEPRECATED — Migrated to `notebooks/corpus_overview.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 8 corpus overview sub-notebooks + the shared file
have been consolidated into the single grouped marimo dashboard
[`notebooks/corpus_overview.py`](../../corpus_overview.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `12_corpus_overview_01_biep_corpus_overview.py` | BIEP Corpus |
| `12_corpus_overview_01_leabharlann_corpus_overview.py` | Leabharlann Corpus |
| `12_corpus_overview_02_cognee_knowledge_graph.py` | Cognee KG |
| `12_corpus_overview_02_leabharlann_subdir_matrix.py` | Leabharlann Subdir |
| `12_corpus_overview_03_bge_m3_embedding_coverage.py` | BGE-M3 Coverage |
| `12_corpus_overview_03_cross_archive_navigation.py` | Cross-Archive |
| `12_corpus_overview_04_lakehouse_table_browser.py` | Lakehouse Browser |
| `12_corpus_overview_04_university_institution_matrix.py` | Universities |
| `12_corpus_overview__shared.py` | (shared helpers — now in `_shared/`) |

## How to run

```bash
marimo edit notebooks/corpus_overview.py
python notebooks/corpus_overview.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.