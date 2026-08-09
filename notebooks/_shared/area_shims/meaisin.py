"""Meaisin (12-agent fleet) per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 6 per-tab overview helpers for the
`notebooks/meaisin_ops_console.py` grouped dashboard, which
consolidates:
- `60_meaisin_ireland_ops.py`
- `61_meaisin_england_ops.py`
- `62_meaisin_extraction_progress.py`
- `63_meaisin_eval_dashboard.py`
- `64_meaisin_bilingual_curriculum.py`

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — `mo.md` rendering.
- centralized-registry (per `.agents/skills/centralized-registry/SKILL.md`)
  — `model_for()` for the LLM.
"""
from __future__ import annotations

from typing import Any


def meaisin_fleet_overview() -> str:
    """Return the 12-agent fleet overview markdown."""
    return """
    ## 🤖 Meaisin 12-Agent Fleet

    | # | Agent | Domain |
    |--:|:--|:--|
    | 1 | root | Orchestrator (the canonical entrypoint) |
    | 2 | curriculum | NCCA/BIEP curriculum specialist |
    | 3 | translation | EN↔GA↔CY↔GD bilingual translation |
    | 4 | corpus | Leabharlann corpus specialist |
    | 5 | research | arXiv + OpenAlex research |
    | 6 | education_research | LC/JC exam papers + marking schemes |
    | 7 | bunchloch_research | Local bunchloch workload specialist |
    | 8 | geospatial | Heritage sites + Gaeltacht regions |
    | 9 | statistics | Statistical methods for education research |
    | 10 | curriculum_comparison | EN vs GA curriculum diff |
    | 11 | agui_curriculum | AGUI chat surface for curriculum Q&A |
    | 12 | mcp_curriculum | MCP server for the 12-agent fleet |

    **Surfaces**: openclaw + openchamber + hermes + ocr-router (4 surfaces)
    **Backbone**: LiteLLM proxy → llama-swap (local) OR minimax-m3 token plan API
    """


def ireland_cohort_overview() -> str:
    """Return the Ireland cohort overview (from 60_meaisin_ireland_ops)."""
    return """
    ## 🇮🇪 Ireland LC + JC Cohorts (164 expected)

    Per-cohort extraction completion %, lifecycle state, bilingual coverage
    (≥95% gate), missing-subject audit.

    Run `mise run agents:smoke` for the agent fleet smoke test.
    Run `mise run agents:audit` for the registry audit.
    """


def england_cohort_overview() -> str:
    """Return the England cohort overview (from 61_meaisin_england_ops)."""
    return """
    ## 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England A-Level + GCSE Cohorts (276 expected)

    Per-board (AQA + OCR + Edexcel) per-(subject, level) extraction status,
    bilingual coverage, missing-subject audit.

    Run `mise run agents:audit` for the registry audit.
    """


def extraction_progress_overview() -> str:
    """Return the extraction progress overview (from 62_meaisin_extraction_progress)."""
    return """
    ## 🔄 Per-cohort Extraction Progress

    Filter by jurisdiction + stage + subject + board + language.
    Shows completion_pct, en_extracted/ga_extracted, lifecycle_state,
    expected_extractions.

    Per-cohort drill-down generalisable to all 8 jurisdictions.
    """


def eval_regression_overview() -> str:
    """Return the RAGAS eval overview (from 63_meaisin_eval_dashboard)."""
    return """
    ## 📊 Per-cohort RAGAS History + Regression Alerts

    Plan 1 RAGAS (≥95% gate) + Plan 3 regression detection.

    Per-cohort RAGAS score trend (faithfulness / answer_relevancy /
    context_precision / context_recall / composite).
    Threshold-compliance matrix (≥95% per-subject gate).
    Regression alerts (Plan 3 RegressionDiffer output).
    """


def bilingual_coverage_overview() -> str:
    """Return the bilingual coverage overview (from 64_meaisin_bilingual_curriculum)."""
    return """
    ## 🌐 Bilingual EN↔GA Curriculum Coverage

    Per-cohort visibility:
    - EN coverage % (topics with EN extraction)
    - GA coverage % (topics with GA extraction)
    - bilingual_pairs_found (count of EN↔GA pairs in the registry)
    - gap_topics (topics missing either EN or GA coverage)
    - passed_threshold (≥95% per-subject gate)

    Generalisable: same pattern works for Wales (EN/CY) + Scotland (EN/GD)
    via the LanguagePair enum.
    """


# The canonical 6 tabs for the meaisin_ops_console grouped dashboard
MEAISIN_OVERVIEW_TABS = [
    ("Overview", meaisin_fleet_overview),
    ("Ireland", ireland_cohort_overview),
    ("England", england_cohort_overview),
    ("Extraction Progress", extraction_progress_overview),
    ("RAGAS Eval", eval_regression_overview),
    ("Bilingual Coverage", bilingual_coverage_overview),
]


__all__ = [
    "meaisin_fleet_overview",
    "ireland_cohort_overview",
    "england_cohort_overview",
    "extraction_progress_overview",
    "eval_regression_overview",
    "bilingual_coverage_overview",
    "MEAISIN_OVERVIEW_TABS",
]