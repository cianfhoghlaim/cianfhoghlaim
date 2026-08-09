"""Irish law per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 6 per-tab overview helpers for the
`notebooks/irish_law.py` grouped dashboard, which consolidates:
- `11_irish_law_01_personal_injury_journey.py`
- `11_irish_law_02_courts_index.py`
- `11_irish_law_03_wrc_decision_search.py`
- `11_irish_law_04_citizensinfo_rights.py`
- `11_irish_law_05_gov_ie_law_corpus.py`
- `11_irish_law_06_unified_cross_source_query.py`
"""
from __future__ import annotations


def personal_injury_overview() -> str:
    """Personal injury journey overview (from 11_01)."""
    return """
    ## 🩹 Personal Injury Journey

    The canonical Irish personal injury claims journey:
    1. Initial injury (PIAB / Injuries Board Ireland)
    2. Medical assessment
    3. Settlement negotiation
    4. Court proceedings (if settlement fails)
    5. Appeal (Circuit Court / High Court / Supreme Court)

    Per the `ireland-primary-jc-dlt-baml` capability.
    """


def courts_index_overview() -> str:
    """Courts index overview (from 11_02)."""
    return """
    ## ⚖️ Courts Index

    The Irish courts hierarchy:
    - District Court (lowest)
    - Circuit Court (middle)
    - High Court (highest)
    - Supreme Court (final appeal)
    - Court of Appeal (intermediate)
    - Specialised courts (WRC, CIRCUIT, etc.)
    """


def wrc_overview() -> str:
    """WRC decision search overview (from 11_03)."""
    return """
    ## 📋 WRC Decision Search

    Search the Workplace Relations Commission (WRC) decision database —
    50,000+ decisions across employment rights, equality, industrial
    relations.
    """


def citizensinfo_overview() -> str:
    """Citizens Info rights overview (from 11_04)."""
    return """
    ## 🏛️ Citizens Info Rights

    Browse Irish citizen rights per the Citizens Information Board:
    - Social welfare
    - Employment
    - Health
    - Education
    - Housing
    - Family
    - Consumer rights
    """


def gov_ie_law_overview() -> str:
    """Gov.ie law corpus overview (from 11_05)."""
    return """
    ## 📜 Gov.ie Law Corpus

    Browse the canonical gov.ie law corpus — statutes + statutory
    instruments + ministerial orders + government circulars.
    """


def unified_search_overview() -> str:
    """Unified cross-source query overview (from 11_06)."""
    return """
    ## 🔍 Unified Cross-Source Query

    Query across all 5 Irish law sources in one call:
    - Personal Injury cases
    - Court decisions (District / Circuit / High / Supreme)
    - WRC decisions
    - Citizens Info rights
    - Gov.ie law corpus

    Unified RAG-powered search with cross-source citations.
    """


IRISH_LAW_TABS = [
    ("Personal Injury", personal_injury_overview),
    ("Courts Index", courts_index_overview),
    ("WRC Decisions", wrc_overview),
    ("Citizens Info", citizensinfo_overview),
    ("Gov.ie Law", gov_ie_law_overview),
    ("Unified Search", unified_search_overview),
]


__all__ = [
    "personal_injury_overview",
    "courts_index_overview",
    "wrc_overview",
    "citizensinfo_overview",
    "gov_ie_law_overview",
    "unified_search_overview",
    "IRISH_LAW_TABS",
]