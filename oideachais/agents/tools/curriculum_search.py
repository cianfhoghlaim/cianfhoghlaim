"""
Curriculum Search Tools for ADK Agents.

Provides LanceDB-based semantic search across curriculum content.
Uses the shared CurriculumVectorSearch module for consistent access.
"""

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Import shared vector search
try:
    from google.adk.tools import ToolContext
except ImportError:
    ToolContext = Any  # Type stub for non-ADK usage

# Storage paths (fallback)
DATA_DIR = Path(__file__).parent.parent.parent / "storage" / "data"
LANCEDB_URI = str(DATA_DIR / "lance" / "curriculum")


class CurriculumSearchResult(BaseModel):
    """Result from curriculum search."""

    text: str
    nation: str
    subject: str
    language: str
    score: float
    learning_outcome_code: str | None = None


class CurriculumComparison(BaseModel):
    """Comparison of curriculum content across nations."""

    query: str
    results_by_nation: dict[str, list[CurriculumSearchResult]]
    similarities: list[str]
    differences: list[str]


async def search_curriculum(
    query: str = Field(description="Search query (multilingual supported)"),
    nation: str | None = Field(default=None, description="Filter by nation"),
    subject: str | None = Field(default=None, description="Filter by subject"),
    language: str | None = Field(default=None, description="Filter by language code (en, cy, ga, gd)"),
    limit: int = Field(default=10, description="Maximum results"),
    tool_context: ToolContext = None,
) -> list[CurriculumSearchResult]:
    """
    Search curriculum content using semantic similarity.

    Supports multilingual queries in English and Celtic languages.
    Uses the shared CurriculumVectorSearch module with consistent embedding.

    Examples:
    - search_curriculum("quadratic equations")
    - search_curriculum("cothromóid chearnach", language="ga")  # Irish
    - search_curriculum("climate change", nation="scotland", subject="science")
    """
    try:
        # Use shared vector search module
        from storage.curriculum_vectors import get_curriculum_search

        search = get_curriculum_search()
        results = await search.search(
            query=query,
            nation=nation,
            subject=subject,
            level=None,  # Language filtering not directly supported, filter post-search
            limit=limit * 2 if language else limit,  # Get more results if filtering
        )

        # Convert to CurriculumSearchResult and filter by language if needed
        output = []
        for r in results:
            if language and r.get("language", "en") != language:
                continue

            output.append(
                CurriculumSearchResult(
                    text=r.get("text", r.get("title", "")),
                    nation=r.get("nation", "unknown"),
                    subject=r.get("subject", "unknown"),
                    language=r.get("language", "en"),
                    score=r.get("similarity_score", 0.0),
                    learning_outcome_code=r.get("outcome_id"),
                )
            )

            if len(output) >= limit:
                break

        return output

    except ImportError:
        logger.warning("storage.curriculum_vectors not available, using fallback")
        return await _search_curriculum_fallback(query, nation, subject, language, limit)
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


async def _search_curriculum_fallback(
    query: str,
    nation: str | None,
    subject: str | None,
    language: str | None,
    limit: int,
) -> list[CurriculumSearchResult]:
    """Fallback search using direct LanceDB access."""
    import lancedb

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        query_embedding = model.encode(query).tolist()
    except ImportError:
        logger.warning("sentence-transformers not available")
        return []

    try:
        db = lancedb.connect(LANCEDB_URI)
        table = db.open_table("curriculum_embeddings")

        # Build filter
        filter_conditions = []
        if nation:
            filter_conditions.append(f"nation = '{nation}'")
        if subject:
            filter_conditions.append(f"subject = '{subject}'")
        if language:
            filter_conditions.append(f"language = '{language}'")

        filter_str = " AND ".join(filter_conditions) if filter_conditions else None

        search = table.search(query_embedding)
        if filter_str:
            search = search.where(filter_str)

        results = search.limit(limit).to_list()

        return [
            CurriculumSearchResult(
                text=r.get("text", ""),
                nation=r.get("nation", "unknown"),
                subject=r.get("subject", "unknown"),
                language=r.get("language", "en"),
                score=1.0 - r.get("_distance", 1.0),
                learning_outcome_code=r.get("code"),
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"Fallback search error: {e}")
        return []


async def find_similar_content(
    text: str = Field(description="Source text to find similar content for"),
    source_nation: str = Field(description="Nation of source text"),
    target_nations: list[str] | None = Field(
        default=None,
        description="Nations to search (default: all except source)",
    ),
    limit_per_nation: int = Field(default=3, description="Results per nation"),
    tool_context: ToolContext = None,
) -> dict[str, list[CurriculumSearchResult]]:
    """
    Find similar curriculum content across nations.

    Useful for curriculum comparison - find equivalent learning outcomes
    or topics in different national curricula.

    Examples:
    - find_similar_content("Students learn about photosynthesis", "england")
    - find_similar_content("LO 1.1: Understand fractions", "ireland", ["scotland", "wales"])
    """
    if target_nations is None:
        all_nations = ["england", "scotland", "wales", "northern_ireland", "ireland"]
        target_nations = [n for n in all_nations if n != source_nation]

    results = {}
    for nation in target_nations:
        nation_results = await search_curriculum(
            query=text,
            nation=nation,
            limit=limit_per_nation,
        )
        results[nation] = nation_results

    return results


async def compare_curricula(
    topic: str = Field(description="Topic to compare across nations"),
    subject: str | None = Field(default=None, description="Subject filter"),
    nations: list[str] | None = Field(
        default=None,
        description="Nations to compare (default: all main nations)",
    ),
    tool_context: ToolContext = None,
) -> CurriculumComparison:
    """
    Compare how a topic is covered across national curricula.

    Searches for the topic in each nation's curriculum and
    identifies similarities and differences.

    Examples:
    - compare_curricula("climate change", subject="science")
    - compare_curricula("algebra", nations=["england", "ireland"])
    """
    if nations is None:
        nations = ["england", "scotland", "wales", "northern_ireland", "ireland"]

    results_by_nation = {}
    for nation in nations:
        results = await search_curriculum(
            query=topic,
            nation=nation,
            subject=subject,
            limit=5,
        )
        results_by_nation[nation] = results

    # Analyze similarities and differences
    similarities = []
    differences = []

    # Check which nations cover the topic
    nations_with_content = [n for n, r in results_by_nation.items() if r]
    nations_without = [n for n in nations if n not in nations_with_content]

    if len(nations_with_content) == len(nations):
        similarities.append(f"Topic '{topic}' is covered in all {len(nations)} nations")
    elif nations_without:
        differences.append(
            f"Topic appears less prominent in: {', '.join(nations_without)}"
        )

    # Compare average relevance scores
    avg_scores = {}
    for nation, results in results_by_nation.items():
        if results:
            avg_scores[nation] = sum(r.score for r in results) / len(results)

    if avg_scores:
        max_nation = max(avg_scores, key=avg_scores.get)
        min_nation = min(avg_scores, key=avg_scores.get)

        if avg_scores[max_nation] - avg_scores[min_nation] > 0.1:
            differences.append(
                f"Strongest coverage in {max_nation}, weakest in {min_nation}"
            )

    return CurriculumComparison(
        query=topic,
        results_by_nation=results_by_nation,
        similarities=similarities,
        differences=differences,
    )


async def get_learning_outcomes(
    nation: str = Field(description="Nation code"),
    subject: str = Field(description="Subject name"),
    stage: str | None = Field(default=None, description="Education stage filter"),
    tool_context: ToolContext = None,
) -> list[dict]:
    """
    Get learning outcomes for a subject in a nation.

    Retrieves structured learning outcomes from curriculum specifications.
    """
    import lancedb

    db = lancedb.connect(LANCEDB_URI)

    try:
        table = db.open_table("curriculum_embeddings")

        # Filter for learning outcomes
        filter_str = f"nation = '{nation}' AND subject = '{subject}' AND chunk_type = 'learning_outcome'"
        if stage:
            filter_str += f" AND stage = '{stage}'"

        results = (
            table.search()
            .where(filter_str)
            .limit(100)
            .to_list()
        )

        return [
            {
                "code": r.get("code"),
                "text": r["text"],
                "stage": r.get("stage"),
                "strand": r.get("strand"),
            }
            for r in results
        ]

    except Exception:
        return []
