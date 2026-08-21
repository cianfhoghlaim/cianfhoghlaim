"""
Curriculum search tools for Tuath.

Search Celtic language curriculum content from Ireland, Scotland, and Wales.
Uses LanceDB for vector search with BGE-M3 embeddings.

NOTE: Tuath consumes curriculum data from oideachais (the authoritative source)
rather than maintaining duplicate ingestion pipelines.
"""

import os
from pathlib import Path

import lancedb
from pydantic import BaseModel


class CurriculumResult(BaseModel):
    """A curriculum search result."""

    id: str
    title: str
    content: str
    nation: str
    language: str
    level: str
    subject: str
    learning_outcomes: list[str]
    score: float


class CurriculumSearchResults(BaseModel):
    """Results from curriculum search."""

    query: str
    results: list[CurriculumResult]
    total: int


class LearningOutcome(BaseModel):
    """A curriculum learning outcome."""

    id: str
    description: str
    subject: str
    level: str
    nation: str
    prerequisites: list[str]
    related_topics: list[str]


# Path to oideachais data (shared storage) - same as curriculum_assets.py
OIDEACHAIS_DATA_PATH = Path(os.environ.get("OIDEACHAIS_DATA_PATH", "../oideachais/storage/data"))
OIDEACHAIS_LANCEDB_PATH = OIDEACHAIS_DATA_PATH / "lancedb"

# LanceDB connection
_db: lancedb.DBConnection | None = None


def _get_db() -> lancedb.DBConnection:
    """Get LanceDB connection to oideachais curriculum data."""
    global _db
    if _db is None:
        lancedb_path = str(OIDEACHAIS_LANCEDB_PATH)
        if not Path(lancedb_path).exists():
            # Fall back to local storage if oideachais not available
            lancedb_path = "/Users/cliste/dev/cianfhoghlaim/sruth/tuath/storage/lance"
        _db = lancedb.connect(lancedb_path)
    return _db


async def search_curriculum(
    query: str,
    nation: str | None = None,
    language: str | None = None,
    level: str | None = None,
    subject: str | None = None,
    limit: int = 10,
) -> CurriculumSearchResults:
    """
    Search Celtic curriculum content.

    Args:
        query: Search query text
        nation: Filter by nation (ireland, scotland, wales)
        language: Filter by language code (ga, gd, cy, en)
        level: Filter by education level (primary, secondary, higher)
        subject: Filter by subject area
        limit: Maximum results to return

    Returns:
        CurriculumSearchResults with matching content
    """
    try:
        db = _get_db()

        # Check if table exists
        if "celtic_curriculum" not in db.table_names():
            return CurriculumSearchResults(query=query, results=[], total=0)

        table = db.open_table("celtic_curriculum")

        # Build filter conditions
        filters = []
        if nation:
            filters.append(f"nation = '{nation}'")
        if language:
            filters.append(f"language = '{language}'")
        if level:
            filters.append(f"level = '{level}'")
        if subject:
            filters.append(f"subject = '{subject}'")

        filter_str = " AND ".join(filters) if filters else None

        # Vector search
        results = table.search(query).where(filter_str).limit(limit).to_pandas()

        # Convert to results
        curriculum_results = []
        for _, row in results.iterrows():
            curriculum_results.append(
                CurriculumResult(
                    id=row.get("id", ""),
                    title=row.get("title", ""),
                    content=row.get("content", ""),
                    nation=row.get("nation", ""),
                    language=row.get("language", ""),
                    level=row.get("level", ""),
                    subject=row.get("subject", ""),
                    learning_outcomes=row.get("learning_outcomes", []),
                    score=float(row.get("_distance", 0)),
                )
            )

        return CurriculumSearchResults(
            query=query,
            results=curriculum_results,
            total=len(curriculum_results),
        )

    except Exception as e:
        # Return empty results on error
        return CurriculumSearchResults(query=query, results=[], total=0)


async def get_learning_outcomes(
    topic: str,
    nation: str | None = None,
    level: str | None = None,
) -> list[LearningOutcome]:
    """
    Get curriculum learning outcomes for a topic.

    Args:
        topic: Topic to find outcomes for
        nation: Filter by nation
        level: Filter by education level

    Returns:
        List of relevant learning outcomes
    """
    try:
        db = _get_db()

        if "learning_outcomes" not in db.table_names():
            return []

        table = db.open_table("learning_outcomes")

        # Build filter
        filters = []
        if nation:
            filters.append(f"nation = '{nation}'")
        if level:
            filters.append(f"level = '{level}'")

        filter_str = " AND ".join(filters) if filters else None

        # Search for outcomes
        results = table.search(topic).where(filter_str).limit(10).to_pandas()

        outcomes = []
        for _, row in results.iterrows():
            outcomes.append(
                LearningOutcome(
                    id=row.get("id", ""),
                    description=row.get("description", ""),
                    subject=row.get("subject", ""),
                    level=row.get("level", ""),
                    nation=row.get("nation", ""),
                    prerequisites=row.get("prerequisites", []),
                    related_topics=row.get("related_topics", []),
                )
            )

        return outcomes

    except Exception:
        return []


# Subject mapping for Celtic curriculum
CELTIC_SUBJECTS = {
    "ga": {
        "teanga": "Irish Language",
        "litríocht": "Irish Literature",
        "gramadach": "Grammar",
        "stair": "History",
        "béaloideas": "Folklore",
    },
    "gd": {
        "gàidhlig": "Scottish Gaelic",
        "litreachas": "Gaelic Literature",
        "gràmar": "Grammar",
        "eachdraidh": "History",
        "beul-aithris": "Oral Tradition",
    },
    "cy": {
        "cymraeg": "Welsh Language",
        "llenyddiaeth": "Welsh Literature",
        "gramadeg": "Grammar",
        "hanes": "History",
        "chwedloniaeth": "Mythology",
    },
}


# Level mapping
EDUCATION_LEVELS = {
    "ireland": {
        "primary": [
            "junior_infants",
            "senior_infants",
            "1st_class",
            "2nd_class",
            "3rd_class",
            "4th_class",
            "5th_class",
            "6th_class",
        ],
        "secondary": [
            "1st_year",
            "2nd_year",
            "3rd_year",
            "transition_year",
            "5th_year",
            "6th_year",
        ],
        "higher": ["undergraduate", "postgraduate"],
    },
    "scotland": {
        "primary": ["p1", "p2", "p3", "p4", "p5", "p6", "p7"],
        "secondary": ["s1", "s2", "s3", "s4", "s5", "s6"],
        "higher": ["undergraduate", "postgraduate"],
    },
    "wales": {
        "primary": ["foundation", "ks1", "ks2"],
        "secondary": ["ks3", "ks4", "ks5"],
        "higher": ["undergraduate", "postgraduate"],
    },
}
