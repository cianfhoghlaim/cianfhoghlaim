"""Celtic languages per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 7 per-tab overview helpers for the
`notebooks/celtic_languages.py` grouped dashboard, which consolidates:
- `06_celtic_languages_01_gaois_terminology_explorer.py`
- `06_celtic_languages_02_duchas_folklore_with_bboxes.py`
- `06_celtic_languages_03_heritage_sites_map.py`
- `06_celtic_languages_04_canuint_dialect_player.py`
- `06_celtic_languages_05_ud_celtic_treebank_viewer.py`
- `06_celtic_languages_06_local_documents_subject_viewer.py`
- `06_celtic_languages_07_celtic_curriculum_browser.py`
"""
from __future__ import annotations


def gaois_overview() -> str:
    """Gaois terminology explorer overview (from 06_01)."""
    return """
    ## 📚 Gaois Terminology Explorer

    Browse the Gaois (Irish Language Terminology) database. Search
    across 100,000+ Irish-language terms with translations + definitions.

    Per the `celtic-language-pipeline` capability — Gaois is the canonical
    authoritative source for standardised Irish-language terminology.
    """


def duchas_overview() -> str:
    """Dúchas folklore overview (from 06_02)."""
    return """
    ## 🏛️ Dúchas Folklore (with bboxes)

    Browse the Schools' Collection (Dúchas) folklore archive with
    geographic bounding boxes. Filter by county + decade + topic.

    Per the `celtic-language-pipeline` capability — Dúchas is the canonical
    historical Irish folklore archive (1937-1938).
    """


def heritage_sites_overview() -> str:
    """Heritage sites map overview (from 06_03)."""
    return """
    ## 🗺️ Heritage Sites Map (Logainm + Heritage Ireland)

    Browse Irish heritage sites (Gaeltacht regions, lighthouses, castles,
    monastic sites) with geographic coordinates. Filter by type +
    county + era.

    Per the `celtic-language-pipeline` + `ireland-primary-jc-dlt-baml`
    capabilities.
    """


def canuint_overview() -> str:
    """Canúint dialect player overview (from 06_04)."""
    return """
    ## 🎙️ Canúint Dialect Player

    Browse the Canúint (Ulster / Munster / Connacht dialects) audio archive
    with phonetic transcriptions. Filter by county + dialect + speaker.
    """


def ud_treebank_overview() -> str:
    """UD Celtic treebank viewer overview (from 06_05)."""
    return """
    ## 🌲 UD Celtic Treebank Viewer

    Browse the Universal Dependencies treebank for Irish + Welsh + Breton
    + Scottish Gaelic. View dependency parses + POS tags + lemmas.
    """


def local_documents_overview() -> str:
    """Local documents viewer overview (from 06_06)."""
    return """
    ## 📂 Local Documents Viewer

    Browse the local Irish-language documents corpus (per-subject
    organisation). Filter by subject + era + source.
    """


def celtic_curriculum_overview() -> str:
    """Celtic curriculum browser overview (from 06_07)."""
    return """
    ## 🎓 Celtic Curriculum Browser

    Browse the Celtic-language curricula (Irish, Welsh, Breton, Scottish
    Gaelic) across primary + secondary levels. Compare cross-linguistically.
    """


CELTIC_LANGUAGES_TABS = [
    ("Gaois", gaois_overview),
    ("Dúchas", duchas_overview),
    ("Heritage Sites", heritage_sites_overview),
    ("Canúint", canuint_overview),
    ("UD Treebank", ud_treebank_overview),
    ("Local Documents", local_documents_overview),
    ("Celtic Curriculum", celtic_curriculum_overview),
]


__all__ = [
    "gaois_overview",
    "duchas_overview",
    "heritage_sites_overview",
    "canuint_overview",
    "ud_treebank_overview",
    "local_documents_overview",
    "celtic_curriculum_overview",
    "CELTIC_LANGUAGES_TABS",
]