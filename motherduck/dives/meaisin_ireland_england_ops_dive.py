"""MotherDuck Dive: meaisin Ireland + England ops dashboard.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5).

The canonical saved-shareable MotherDuck Dive combining the 4 meaisinfoghlaim
ops notebooks (60 / 61 / 62 / 63 + 64) into a single dashboard.

Generalisable: same Dive pattern works for Scotland / Wales / NI /
Jersey / Guernsey / IoM rollouts.

Deploy with: mise run motherduck:create-dive
Or directly: python -m motherduck.dives.meaisin_ireland_england_ops_dive
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def render_dive_definition() -> dict:
    """Render the canonical MotherDuck Dive definition.

    Consumed by ``motherduck:create-dive`` + the operator dashboard.
    """
    return {
        "name": "meaisin_ireland_england_ops",
        "title": "meaisinfoghlaim Ireland + England Ops Dashboard",
        "description": (
            "The canonical operator-facing dashboard for the Ireland + "
            "England education pipeline. Combines: extraction progress "
            "(notebook 62), RAGAS eval history (notebook 63), bilingual "
            "coverage (notebook 64), Ireland ops (notebook 60), "
            "England ops (notebook 61)."
        ),
        "tags": ["meaisinfoghlaim", "ireland", "england", "biiep_v3", "education"],
        "kpis": [
            {"label": "Total Ireland cohorts", "query": "SELECT COUNT(*) FROM meaisinfoghlaim.cohorts WHERE jurisdiction='ireland'"},
            {"label": "Total England cohorts", "query": "SELECT COUNT(*) FROM meaisinfoghlaim.cohorts WHERE jurisdiction='england'"},
            {"label": "EN extraction rate", "query": "SELECT AVG(en_extracted::int) * 100 FROM meaisinfoghlaim.cohorts"},
            {"label": "GA extraction rate", "query": "SELECT AVG(ga_extracted::int) * 100 FROM meaisinfoghlaim.cohorts WHERE language_pair IS NOT NULL"},
            {"label": "Bilingual coverage (>= 95% gate)", "query": "SELECT 100.0 * SUM(CASE WHEN en_extracted AND ga_extracted THEN 1 ELSE 0 END)::float / COUNT(*) FROM meaisinfoghlaim.cohorts WHERE language_pair IS NOT NULL"},
            {"label": "Cross-qual coverage vs milestones", "query": "SELECT 100.0 * (SELECT COUNT(DISTINCT (jurisdiction, stage, subject)) FROM meaisinfoghlaim.cohorts WHERE jurisdiction IN ('ireland', 'england')) / 276.0"},
        ],
        "charts": [
            {
                "title": "Per-jurisdiction extraction progress",
                "type": "bar",
                "x": "jurisdiction",
                "y": "AVG(en_extraction_count + ga_extraction_count)::float / NULLIF(expected_extractions, 0) * 100",
                "query": "SELECT jurisdiction, AVG(en_extraction_count + ga_extraction_count)::float / NULLIF(expected_extractions, 0) * 100 AS pct FROM meaisinfoghlaim.cohorts GROUP BY jurisdiction",
            },
            {
                "title": "Bilingual coverage gate (Ireland only)",
                "type": "bar",
                "x": "subject",
                "y": "en_extracted::int + ga_extracted::int",
                "query": "SELECT subject, (en_extracted::int + ga_extracted::int) AS both_extracted FROM meaisinfoghlaim.cohorts WHERE language_pair IS NOT NULL AND jurisdiction='ireland'",
            },
            {
                "title": "Lifecycle state distribution",
                "type": "pie",
                "query": "SELECT lifecycle_state, COUNT(*) FROM meaisinfoghlaim.cohorts GROUP BY lifecycle_state",
            },
            {
                "title": "Cross-qual coverage (Ireland vs England)",
                "type": "bar",
                "x": "stage",
                "y": "COUNT(DISTINCT subject)",
                "query": "SELECT stage, COUNT(DISTINCT subject) AS subject_count FROM meaisinfoghlaim.cohorts WHERE jurisdiction IN ('ireland', 'england') GROUP BY stage ORDER BY stage",
            },
        ],
    }


def get_dive_definition() -> dict:
    """The canonical entrypoint for the operator + the MotherDuck create-dive CLI."""
    return render_dive_definition()


__all__ = ["render_dive_definition", "get_dive_definition"]
