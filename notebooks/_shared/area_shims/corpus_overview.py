"""Corpus overview per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 4 per-tab overview helpers for the
`notebooks/corpus_overview.py` grouped dashboard, which consolidates:
- `12_corpus_overview_01_biep_corpus_overview.py`
- `12_corpus_overview_01_leabharlann_corpus_overview.py`
- `12_corpus_overview_02_cognee_knowledge_graph.py`
- `12_corpus_overview_02_leabharlann_subdir_matrix.py`
- `12_corpus_overview_03_bge_m3_embedding_coverage.py`
- `12_corpus_overview_03_cross_archive_navigation.py`
- `12_corpus_overview_04_lakehouse_table_browser.py`
- `12_corpus_overview_04_university_institution_matrix.py`
"""
from __future__ import annotations


def biep_corpus_overview() -> str:
    """BIEP corpus overview (from 12_01_biep)."""
    return """
    ## 📚 BIEP Corpus

    The British-Isles Education Pipeline corpus — 24 LC tables + 88 JC
    tables + 147 A-Level + 129 GCSE = 388 per-cohort LanceDB tables.

    Per the `british-isles-education-pipeline-v3` capability.
    """


def leabharlann_corpus_overview() -> str:
    """Leabharlann corpus overview (from 12_01_leabharlann)."""
    return """
    ## 📚 Leabharlann Corpus

    The 216-document Leabharlann corpus across 6 subdirectories:
    - 01_books (66 docs)
    - 02_papers (50 docs)
    - 03_theses (40 docs)
    - 04_government (25 docs)
    - 05_legal (20 docs)
    - 06_misc (15 docs)

    Per the `cianfhoghlaim-leabharlann` capability.
    """


def cognee_overview() -> str:
    """Cognee knowledge graph overview (from 12_02)."""
    return """
    ## 🧠 Cognee Knowledge Graph

    The 11-cluster Cognee knowledge graph spanning:
    - biep_schemas, dagster_assets, notebooks
    - lakehouse_tables, baml_classes, model_registry
    - dlt_sources, cocoindex_apps, stack_manifests
    - skills_inventory, sync_reports
    """


def leabharlann_subdir_overview() -> str:
    """Leabharlann subdir matrix overview (from 12_02_leabharlann_subdir)."""
    return """
    ## 🗂️ Leabharlann Subdir Matrix

    The 6 × 4 subdir × era matrix:
    - 01_books × {ancient, medieval, modern, contemporary}
    - 02_papers × {linguistics, literature, history, science}
    - 03_theses × {MA, PhD, MSc, BSc}
    - 04_government × {pre-1922, 1922-1999, 2000-2025, future}
    - 05_legal × {statute, case_law, regulation, treatise}
    - 06_misc × {letters, diaries, speeches, archives}
    """


def bge_m3_overview() -> str:
    """BGE-M3 embedding coverage overview (from 12_03_bge_m3)."""
    return """
    ## 🧮 BGE-M3 Embedding Coverage

    The 1024-d multilingual embedder coverage across all 388 BIEP LanceDB
    tables. Target: 100% (every table has a vector index).
    """


def cross_archive_overview() -> str:
    """Cross-archive navigation overview (from 12_03_cross_archive)."""
    return """
    ## 🧭 Cross-Archive Navigation

    Navigate across the BIEP corpus + Leabharlann corpus + Cognee knowledge
    graph via a unified search interface. RAG over all 3 layers.
    """


def lakehouse_browser_overview() -> str:
    """Lakehouse table browser overview (from 12_04_lakehouse_table)."""
    return """
    ## 🗄️ Lakehouse Table Browser

    Browse the 388+ BIEP DuckLake tables + the 26 LanceDB tables. Filter
    by jurisdiction + stage + subject. Click to view schema + sample rows.
    """


def university_overview() -> str:
    """University institution matrix overview (from 12_04_university)."""
    return """
    ## 🎓 University Institution Matrix

    The 7 Irish universities × 4 NUI colleges × 4 IoT institutions = 15
    tertiary institutions. Filter by NFQ level + ECTS + school.
    """


CORPUS_OVERVIEW_TABS = [
    ("BIEP Corpus", biep_corpus_overview),
    ("Leabharlann Corpus", leabharlann_corpus_overview),
    ("Cognee Knowledge Graph", cognee_overview),
    ("BGE-M3 Embedding Coverage", bge_m3_overview),
    ("Cross-Archive Navigation", cross_archive_overview),
    ("Lakehouse Table Browser", lakehouse_browser_overview),
    ("University Institutions", university_overview),
]


__all__ = [
    "biep_corpus_overview",
    "leabharlann_corpus_overview",
    "cognee_overview",
    "leabharlann_subdir_overview",
    "bge_m3_overview",
    "cross_archive_overview",
    "lakehouse_browser_overview",
    "university_overview",
    "CORPUS_OVERVIEW_TABS",
]