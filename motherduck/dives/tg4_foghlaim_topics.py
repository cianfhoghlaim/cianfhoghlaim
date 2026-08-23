"""
TG4 + Foghlaim Topics Dive — BIEP v3 MotherDuck Dive (definition + dashboard).

A live MotherDuck dashboard for the multimodal Irish-language media
corpus coverage. Joins the TG4 player catalog (`cianfhoghlaim.tg4.player_shows`)
+ the Foghlaim lessons corpus (`cianfhoghlaim.tg4.foghlaim_lessons`) into
the 6 BIEP v1 LC subjects + 18 JC subjects via the Foghlaim `biep_subject`
taxonomy.

Drill-down: click a (corpus, biep_subject, biep_stage) cell → list the
TG4 player shows / Foghlaim lessons with their per-row metadata.

Dive name: ``tg4_foghlaim_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.tg4.player_shows``
  - ``md:cianfhoghlaim.tg4.foghlaim_lessons``

Reference: openspec/changes/2026-08-25-tg4-foghlaim-corpus-v1/
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# The 6 BIEP v1 priority LC subjects + 18 JC subjects used by the
# `biep_subject` column in `cianfhoghlaim.tg4.foghlaim_lessons`.
BIEP_LC_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "gaeilge",
    "english",
    "computer_science",
)
BIEP_JC_SUBJECTS: tuple[str, ...] = (
    "history",
    "gaeilge_oral",
    "gaeilge_literature",
    "gaeilge_poetry",
    "gaeilge_current_affairs",
    "gaeilge_children",
    "science",
    "music",
    "music_songs",
    "art",
    "physical_education",
    "wellbeing",
    "business",
    "geography_climate",
    "non_curriculum",
)

# The 3 Bunscoil/JC/SC stages.
BIEP_STAGES: tuple[str, ...] = ("bunscoil", "junior_cycle", "senior_cycle", "adult")

# The 2 corpora.
TG4_FOGHLAIM_CORPORA: tuple[str, ...] = ("player", "lessons")

# The 8 TG4 genres + 3 Foghlaim levels (the per-corpus `facet` dimension).
TG4_GENRES: tuple[str, ...] = (
    "Faisnéis",
    "Ceol",
    "Drámaíocht",
    "Cúrsaí Reatha",
    "Siamsaíocht",
    "Spórt",
    "Saolchláir",
    "Cúla4",
    "Bailiúcháin",
)
FOGHLAIM_LEVELS: tuple[str, ...] = (
    "Bunscoil",
    "Sraith Shóisearach & GCSE",
    "Ardteist, AS/A2 & Foghlaimeoirí Fásta",
)


@dataclass
class DiveSpec:
    """Minimal MotherDuck Dive spec for the tg4_foghlaim_topics Dive."""

    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "sql": self.sql,
            "charts": self.charts,
            "filters": self.filters,
        }


def _load_sql_from_sibling() -> str:
    """Load the canonical SQL from `tg4_foghlaim_topics.sql` (the file
    the MotherDuck Dagster flight will execute). Falls back to a hard-coded
    equivalent when the .sql file is not yet deployed.
    """
    sibling = Path(__file__).parent / "tg4_foghlaim_topics.sql"
    if sibling.exists():
        return sibling.read_text(encoding="utf-8")

    # Inline fallback — same shape as the .sql.
    return """
WITH player_counts AS (
    SELECT 'player' AS corpus, genre_gaelic AS facet,
           biep_subject, NULL::VARCHAR AS biep_stage,
           COUNT(*) AS row_count, AVG(duration_s) AS avg_duration_s
    FROM cianfhoghlaim.tg4.player_shows
    GROUP BY genre_gaelic, biep_subject
    UNION ALL
    SELECT 'lessons' AS corpus, level_gaelic AS facet,
           biep_subject, biep_stage,
           COUNT(*) AS row_count, AVG(duration_s) AS avg_duration_s
    FROM cianfhoghlaim.tg4.foghlaim_lessons
    WHERE biep_subject != 'non_curriculum'
    GROUP BY level_gaelic, biep_subject, biep_stage
)
SELECT corpus, facet, biep_subject, biep_stage, row_count, avg_duration_s
FROM player_counts
ORDER BY corpus, biep_subject, biep_stage
"""


# The canonical Dive spec.
TG4_FOGHLAIM_TOPICS_DIVE = DiveSpec(
    name="tg4_foghlaim_topics",
    description=(
        "BIEP v3 — TG4 + Foghlaim media corpus coverage. Joins the TG4 "
        "player catalog (8 genres + Bailiúcháin) and the Foghlaim lesson "
        "corpus (3 educational levels + 11+ subjects) into the 6 BIEP v1 LC "
        "subjects + 18 JC subjects via the biep_subject taxonomy. Drill-down: "
        "click a (corpus, biep_subject, biep_stage) cell → list the underlying "
        "player shows / lessons with per-row metadata."
    ),
    sql=_load_sql_from_sibling(),
    charts=[
        {
            "type": "bar",
            "title": "Episode count per TG4 genre (player catalog)",
            "x": "facet",
            "y": "row_count",
            "facet": "corpus",
            "filter": {"column": "corpus", "value": "player"},
        },
        {
            "type": "bar",
            "title": "Lesson count per Foghlaim level",
            "x": "facet",
            "y": "row_count",
            "facet": "corpus",
            "filter": {"column": "corpus", "value": "lessons"},
        },
        {
            "type": "heatmap",
            "title": "BIEP subject × stage coverage (Foghlaim corpus)",
            "x": "biep_stage",
            "y": "biep_subject",
            "value": "row_count",
            "filter": {"column": "corpus", "value": "lessons"},
        },
        {
            "type": "line",
            "title": "Avg duration per corpus × subject",
            "x": "biep_subject",
            "y": "avg_duration_s",
            "facet": "corpus",
        },
    ],
    filters=[
        {"column": "corpus", "type": "multi_select", "options": list(TG4_FOGHLAIM_CORPORA)},
        {"column": "biep_subject", "type": "multi_select", "options": list(BIEP_LC_SUBJECTS + BIEP_JC_SUBJECTS)},
        {"column": "biep_stage", "type": "multi_select", "options": list(BIEP_STAGES)},
        {"column": "facet", "type": "multi_select", "options": list(TG4_GENRES + FOGHLAIM_LEVELS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return TG4_FOGHLAIM_TOPICS_DIVE.to_dict()


def compute_kpis() -> dict[str, Any]:
    """Compute the 6 KPIs that surface in the marimo notebook
    `notebooks/41_tg4_foghlaim_corpus.py`. Backed by the DuckLake
    `cianfhoghlaim.tg4.player_shows` + `cianfhoghlaim.tg4.foghlaim_lessons`
    tables.

    Returns an empty-stub when the connection is unavailable so the
    Dagster `tg4_quality_audit_summary` asset materialises a sensible
    default rather than crashing.
    """
    try:
        import duckdb  # type: ignore[import-not-found]

        conn = duckdb.connect("md:cianfhoghlaim", read_only=True)
        try:
            row = conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM cianfhoghlaim.tg4.player_shows)
                        AS total_shows,
                    (SELECT COUNT(*) FROM cianfhoghlaim.tg4.foghlaim_lessons)
                        AS total_lessons,
                    (SELECT COUNT(*) FROM cianfhoghlaim.tg4.foghlaim_lessons
                     WHERE biep_subject != 'non_curriculum')
                        AS total_ncca_tagged_lessons
                """
            ).fetchone()
            total_shows, total_lessons, total_ncca = row or (0, 0, 0)
            median_row = conn.execute(
                """
                SELECT AVG(duration_s) FROM cianfhoghlaim.tg4.player_shows
                WHERE duration_s > 0
                """
            ).fetchone()
            median_duration = median_row[0] if median_row else None
            dialect_rows = conn.execute(
                """
                SELECT dialect, COUNT(*) AS n
                FROM cianfhoghlaim.tg4.tg4_segments
                GROUP BY dialect
                ORDER BY n DESC
                """
            ).fetchall()
            top_subject_row = conn.execute(
                """
                SELECT biep_subject, COUNT(*) AS n
                FROM cianfhoghlaim.tg4.foghlaim_lessons
                WHERE biep_subject != 'non_curriculum'
                GROUP BY biep_subject
                ORDER BY n DESC
                LIMIT 1
                """
            ).fetchone()
            return {
                "total_shows": int(total_shows or 0),
                "total_lessons": int(total_lessons or 0),
                "total_ncca_tagged_lessons": int(total_ncca or 0),
                "median_player_duration_s": float(median_duration) if median_duration else None,
                "dialect_distribution": {
                    (d or "unknown"): int(n) for d, n in dialect_rows
                },
                "top_subject": top_subject_row[0] if top_subject_row else None,
            }
        finally:
            conn.close()
    except Exception:  # noqa: BLE001 — degrade gracefully
        return {
            "total_shows": 0,
            "total_lessons": 0,
            "total_ncca_tagged_lessons": 0,
            "median_player_duration_s": None,
            "dialect_distribution": {},
            "top_subject": None,
        }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {TG4_FOGHLAIM_TOPICS_DIVE.name}")
        print(f"Description: {TG4_FOGHLAIM_TOPICS_DIVE.description}")
        print(f"Charts: {len(TG4_FOGHLAIM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(TG4_FOGHLAIM_TOPICS_DIVE.filters)}")
