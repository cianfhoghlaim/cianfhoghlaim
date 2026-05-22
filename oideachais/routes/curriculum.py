"""
Curriculum API Routes.

Provides curriculum data endpoints with AG-UI streaming:
    POST /api/agent - AG-UI streaming agent endpoint
    GET /api/curriculum - List curriculum pages
    GET /api/curriculum/outcomes - List learning outcomes
    GET /api/curriculum/compare - Compare across nations
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import duckdb
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["curriculum"])

# Database path
DB_PATH = os.environ.get(
    "DUCKDB_PATH",
    os.path.join(os.path.dirname(__file__), "../../storage/data/celtic_education.duckdb")
)


# =============================================================================
# Pydantic Models
# =============================================================================

class CurriculumPage(BaseModel):
    """Curriculum page response."""
    id: str
    url: str | None = None
    title: str
    content: str
    source: str | None = None
    language: str = "en"
    subject: str | None = None
    level: str | None = None
    crawled_at: datetime | None = None


class LearningOutcome(BaseModel):
    """Learning outcome response."""
    id: str
    subject: str
    strand: str | None = None
    strand_unit: str | None = None
    outcome_text: str
    outcome_text_ga: str | None = None
    level: str | None = None
    class_group: str | None = None


class ComparisonResult(BaseModel):
    """Curriculum comparison result."""
    source_nation: str
    target_nation: str
    source_outcome: str
    target_outcome: str
    similarity_score: float
    alignment_type: str  # exact, partial, related


class AGUIRequest(BaseModel):
    """AG-UI agent request."""
    thread_id: str | None = None
    run_id: str | None = None
    messages: list[dict[str, Any]]
    state: dict[str, Any] | None = None


# =============================================================================
# Database Helpers
# =============================================================================

def get_db_connection():
    """Get DuckDB connection."""
    return duckdb.connect(DB_PATH, read_only=True)


def query_curriculum_pages(
    subject: str | None = None,
    level: str | None = None,
    language: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Query curriculum pages from semantic layer."""
    conn = get_db_connection()

    # Query from semantic layer fact table with dimension joins
    query = """
        SELECT
            f.outcome_id as id,
            f.source_url as url,
            f.title,
            f.content,
            f.source,
            l.language_code as language,
            s.subject_code as subject,
            lv.level_name as level,
            f.indexed_at as crawled_at,
            f.content_hash
        FROM marts.fact_learning_outcome f
        LEFT JOIN marts.dim_subject s ON f.subject_id = s.subject_id
        LEFT JOIN marts.dim_language l ON f.language_id = l.language_id
        LEFT JOIN marts.dim_level lv ON f.level_id = lv.mapping_id
        WHERE 1=1
    """
    params = []

    if subject:
        query += " AND s.subject_code = ?"
        params.append(subject.lower())
    if level:
        query += " AND lv.level_code = ?"
        params.append(level.lower())
    if language:
        query += " AND l.language_code = ?"
        params.append(language.lower())

    query += f" LIMIT {limit}"

    try:
        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        # Fallback to raw table if semantic layer fails
        return query_curriculum_pages_raw(subject, level, language, limit, conn)
    finally:
        conn.close()


def query_curriculum_pages_raw(
    subject: str | None,
    level: str | None,
    language: str | None,
    limit: int,
    conn,
) -> list[dict]:
    """Fallback to raw education tables."""
    query = "SELECT * FROM education.curriculum_pages WHERE 1=1"
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject.lower())
    if level:
        query += " AND level = ?"
        params.append(level.lower())
    if language:
        query += " AND language = ?"
        params.append(language.lower())

    query += f" LIMIT {limit}"

    try:
        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Fallback query error: {e}")
        return []


def query_learning_outcomes(
    subject: str | None = None,
    level: str | None = None,
    strand: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Query learning outcomes from semantic layer."""
    conn = get_db_connection()

    # Use semantic layer with unified outcomes
    query = """
        SELECT
            u.outcome_id as id,
            u.subject,
            NULL as strand,
            NULL as strand_unit,
            u.title as outcome_text,
            NULL as outcome_text_ga,
            u.curriculum_level as level,
            NULL as class_group,
            n.nation_name as nation,
            u.is_celtic_medium
        FROM int.int_unified_outcomes u
        LEFT JOIN marts.dim_nation n ON u.nation = n.nation_code
        WHERE 1=1
    """
    params = []

    if subject:
        query += " AND u.subject = ?"
        params.append(subject.lower())
    if level:
        query += " AND u.curriculum_level ILIKE ?"
        params.append(f"%{level}%")
    if strand:
        query += " AND u.title ILIKE ?"
        params.append(f"%{strand}%")

    query += f" LIMIT {limit}"

    try:
        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        # Fallback to raw education.learning_outcomes
        return query_learning_outcomes_raw(subject, level, strand, limit)
    finally:
        conn.close()


def query_learning_outcomes_raw(
    subject: str | None,
    level: str | None,
    strand: str | None,
    limit: int,
) -> list[dict]:
    """Fallback to raw learning_outcomes table."""
    conn = get_db_connection()
    query = "SELECT * FROM education.learning_outcomes WHERE 1=1"
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject.lower())
    if level:
        query += " AND level = ?"
        params.append(level.lower())
    if strand:
        query += " AND strand ILIKE ?"
        params.append(f"%{strand}%")

    query += f" LIMIT {limit}"

    try:
        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Fallback query error: {e}")
        return []
    finally:
        conn.close()


def search_outcomes(query_text: str, limit: int = 10) -> list[dict]:
    """Search learning outcomes by text."""
    conn = get_db_connection()

    sql = """
        SELECT * FROM education.learning_outcomes
        WHERE outcome_text ILIKE ? OR strand ILIKE ? OR subject ILIKE ?
        LIMIT ?
    """
    pattern = f"%{query_text}%"

    try:
        result = conn.execute(sql, [pattern, pattern, pattern, limit]).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []
    finally:
        conn.close()


# =============================================================================
# AG-UI Streaming Implementation
# =============================================================================

async def generate_agui_stream(
    user_message: str,
    thread_id: str,
    run_id: str,
) -> AsyncGenerator[str, None]:
    """Generate AG-UI SSE event stream."""

    # RUN_STARTED
    yield "event: RUN_STARTED\n"
    yield f"data: {json.dumps({'run_id': run_id, 'thread_id': thread_id})}\n\n"

    await asyncio.sleep(0.05)

    # Parse user intent and search
    user_lower = user_message.lower()

    # Determine search strategy
    search_results = []
    comparison_mode = False

    if any(word in user_lower for word in ["compare", "comparison", "difference", "versus", "vs"]):
        comparison_mode = True

    # Extract subject keywords
    subjects = []
    for subject in ["mathematics", "maths", "math", "english", "science", "history", "gaeilge", "irish"]:
        if subject in user_lower:
            # Normalize subject name
            normalized = "mathematics" if subject in ["maths", "math"] else subject
            normalized = "gaeilge" if subject == "irish" and "gaeilge" not in user_lower else normalized
            subjects.append(normalized)

    # Search for outcomes
    if subjects:
        for subject in subjects[:2]:  # Limit to 2 subjects
            outcomes = query_learning_outcomes(subject=subject, limit=5)
            search_results.extend(outcomes)
    else:
        # General search
        search_results = search_outcomes(user_message, limit=8)

    # TOOL_CALL_START (if searching)
    if search_results:
        tool_call_id = str(uuid.uuid4())
        yield "event: TOOL_CALL_START\n"
        yield f"data: {json.dumps({'tool_call_id': tool_call_id, 'name': 'search_curriculum'})}\n\n"

        await asyncio.sleep(0.1)

        # TOOL_CALL_END
        yield "event: TOOL_CALL_END\n"
        yield f"data: {json.dumps({'tool_call_id': tool_call_id, 'name': 'search_curriculum'})}\n\n"

    # STATE_SNAPSHOT with results
    state = {
        "selected_nations": ["ireland"],
        "selected_subjects": subjects if subjects else [],
        "search_results": [
            {
                "id": r.get("id", ""),
                "subject": r.get("subject", ""),
                "outcome_text": r.get("outcome_text", ""),
                "outcome_text_ga": r.get("outcome_text_ga"),
                "level": r.get("level", ""),
                "strand": r.get("strand", ""),
            }
            for r in search_results[:10]
        ],
        "comparison_results": [],
        "pending_translations": [],
    }

    yield "event: STATE_SNAPSHOT\n"
    yield f"data: {json.dumps({'snapshot': state})}\n\n"

    await asyncio.sleep(0.05)

    # TEXT_MESSAGE_START
    message_id = str(uuid.uuid4())
    yield "event: TEXT_MESSAGE_START\n"
    yield f"data: {json.dumps({'message_id': message_id, 'role': 'assistant'})}\n\n"

    # Generate response
    if search_results:
        if comparison_mode and len(subjects) >= 2:
            response = generate_comparison_response(subjects, search_results)
        else:
            response = generate_search_response(subjects, search_results, user_message)
    else:
        response = generate_help_response()

    # Stream response in chunks
    chunk_size = 30
    for i in range(0, len(response), chunk_size):
        chunk = response[i:i + chunk_size]
        yield "event: TEXT_MESSAGE_CONTENT\n"
        yield f"data: {json.dumps({'message_id': message_id, 'delta': chunk})}\n\n"
        await asyncio.sleep(0.02)

    # TEXT_MESSAGE_END
    yield "event: TEXT_MESSAGE_END\n"
    yield f"data: {json.dumps({'message_id': message_id})}\n\n"

    # RUN_FINISHED
    yield "event: RUN_FINISHED\n"
    yield f"data: {json.dumps({'run_id': run_id, 'status': 'success'})}\n\n"


def generate_search_response(subjects: list[str], results: list[dict], query: str) -> str:
    """Generate response for search results."""
    if not results:
        return f"I couldn't find specific curriculum content matching '{query}'. Try searching for a specific subject like Mathematics, English, Science, or History."

    subject_str = ", ".join(s.title() for s in subjects) if subjects else "curriculum"

    response = f"I found {len(results)} learning outcomes for {subject_str} in the Junior Cycle curriculum.\n\n"

    # Group by strand
    strands = {}
    for r in results:
        strand = r.get("strand", "General")
        if strand not in strands:
            strands[strand] = []
        strands[strand].append(r)

    for strand, outcomes in list(strands.items())[:3]:
        response += f"**{strand}:**\n"
        for outcome in outcomes[:3]:
            text = outcome.get("outcome_text", "")
            ga_text = outcome.get("outcome_text_ga")
            response += f"- {text}\n"
            if ga_text:
                response += f"  (as Gaeilge: {ga_text})\n"
        response += "\n"

    return response


def generate_comparison_response(subjects: list[str], results: list[dict]) -> str:
    """Generate comparison response."""
    response = f"Comparing curriculum content for {', '.join(s.title() for s in subjects)}:\n\n"

    for subject in subjects[:2]:
        subject_results = [r for r in results if r.get("subject", "").lower() == subject.lower()]
        response += f"**{subject.title()}** ({len(subject_results)} outcomes found):\n"
        for r in subject_results[:3]:
            response += f"- {r.get('outcome_text', '')[:100]}...\n"
        response += "\n"

    response += "\n*Note: Cross-nation comparison (Ireland vs England/Scotland/Wales) is available in the Compare page.*"
    return response


def generate_help_response() -> str:
    """Generate help response."""
    return """Welcome to the Celtic Curriculum Assistant! I can help you with:

**Search Curriculum Content:**
- "Show me Junior Cycle Mathematics outcomes"
- "What are the learning outcomes for Science?"
- "Find History content about World War I"

**Compare Curricula:**
- "Compare Mathematics and English curricula"
- "Show differences between Junior Cycle subjects"

**Celtic Language Support:**
- Learning outcomes are available in Irish (Gaeilge)
- Try: "Show Gaeilge curriculum"

**Subjects Available:**
Mathematics, English, Science, History, Gaeilge

What would you like to explore?"""


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/api/agent")
async def agent_stream(request: Request) -> StreamingResponse:
    """
    AG-UI streaming agent endpoint.

    Receives messages and streams AG-UI events back via SSE.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Extract request parameters
    messages = body.get("messages", [])
    thread_id = body.get("thread_id") or str(uuid.uuid4())
    run_id = body.get("run_id") or str(uuid.uuid4())

    # Get latest user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    if not user_message:
        user_message = "Hello"

    return StreamingResponse(
        generate_agui_stream(user_message, thread_id, run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/api/curriculum/pages", response_model=list[CurriculumPage])
async def list_curriculum_pages(
    subject: str | None = Query(None, description="Filter by subject"),
    level: str | None = Query(None, description="Filter by level (e.g., junior_cycle)"),
    language: str | None = Query(None, description="Filter by language (en, ga)"),
    limit: int = Query(20, ge=1, le=100),
) -> list[CurriculumPage]:
    """List curriculum pages with optional filters."""
    results = query_curriculum_pages(
        subject=subject,
        level=level,
        language=language,
        limit=limit,
    )

    return [
        CurriculumPage(
            id=r.get("id", ""),
            url=r.get("url"),
            title=r.get("title", "Untitled"),
            content=r.get("content", "")[:500] + "..." if len(r.get("content", "")) > 500 else r.get("content", ""),
            source=r.get("source"),
            language=r.get("language", "en"),
            subject=r.get("subject"),
            level=r.get("level"),
            crawled_at=r.get("crawled_at"),
        )
        for r in results
    ]


@router.get("/api/curriculum/outcomes", response_model=list[LearningOutcome])
async def list_learning_outcomes(
    subject: str | None = Query(None, description="Filter by subject"),
    level: str | None = Query(None, description="Filter by level"),
    strand: str | None = Query(None, description="Filter by strand"),
    limit: int = Query(50, ge=1, le=200),
) -> list[LearningOutcome]:
    """List learning outcomes with optional filters."""
    results = query_learning_outcomes(
        subject=subject,
        level=level,
        strand=strand,
        limit=limit,
    )

    return [
        LearningOutcome(
            id=r.get("id", ""),
            subject=r.get("subject", ""),
            strand=r.get("strand"),
            strand_unit=r.get("strand_unit"),
            outcome_text=r.get("outcome_text", ""),
            outcome_text_ga=r.get("outcome_text_ga"),
            level=r.get("level"),
            class_group=r.get("class_group"),
        )
        for r in results
    ]


@router.get("/api/curriculum/subjects")
async def list_subjects() -> list[dict[str, Any]]:
    """List available subjects with outcome counts from semantic layer."""
    conn = get_db_connection()

    try:
        # Use semantic layer dim_subject
        result = conn.execute("""
            SELECT
                subject_code as subject,
                subject_name,
                subject_area,
                is_celtic_subject,
                outcome_count
            FROM marts.dim_subject
            ORDER BY outcome_count DESC
        """).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        # Fallback to raw table
        try:
            result = conn.execute("""
                SELECT subject, COUNT(*) as outcome_count
                FROM education.learning_outcomes
                GROUP BY subject
                ORDER BY outcome_count DESC
            """).fetchall()
            return [{"subject": row[0], "outcome_count": row[1]} for row in result]
        except Exception:
            return []
    finally:
        conn.close()


@router.get("/api/curriculum/stats")
async def curriculum_stats() -> dict[str, Any]:
    """Get curriculum statistics from semantic layer."""
    conn = get_db_connection()

    try:
        # Use semantic layer aggregates
        metrics = conn.execute("""
            SELECT * FROM marts.agg_comparison_metrics
        """).fetchall()
        metrics_cols = [desc[0] for desc in conn.description]
        metrics_data = [dict(zip(metrics_cols, row)) for row in metrics]

        # Get nations from dimension
        nations = conn.execute("""
            SELECT nation_code, nation_name, nation_name_native
            FROM marts.dim_nation
        """).fetchall()

        # Get languages from dimension
        languages = conn.execute("""
            SELECT language_code, language_name, is_celtic
            FROM marts.dim_language
        """).fetchall()

        # Get levels from dimension
        levels = conn.execute("""
            SELECT DISTINCT level_code, level_name, nation
            FROM marts.dim_level
            ORDER BY nation, age_range_start
        """).fetchall()

        return {
            "semantic_layer": True,
            "metrics_by_nation": metrics_data,
            "nations": [{"code": n[0], "name": n[1], "native_name": n[2]} for n in nations],
            "languages": [{"code": l[0], "name": l[1], "is_celtic": l[2]} for l in languages],
            "levels": [{"code": l[0], "name": l[1], "nation": l[2]} for l in levels],
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        # Fallback to raw tables
        try:
            page_count = conn.execute("SELECT COUNT(*) FROM education.curriculum_pages").fetchone()[0]
            outcome_count = conn.execute("SELECT COUNT(*) FROM education.learning_outcomes").fetchone()[0]
            subjects = conn.execute("SELECT DISTINCT subject FROM education.learning_outcomes WHERE subject IS NOT NULL").fetchall()
            return {
                "semantic_layer": False,
                "curriculum_pages": page_count,
                "learning_outcomes": outcome_count,
                "subjects": [s[0] for s in subjects],
                "nations": ["ireland"],
                "languages": ["en", "ga"],
            }
        except Exception:
            return {"error": str(e)}
    finally:
        conn.close()


@router.get("/api/curriculum/comparison")
async def comparison_metrics() -> dict[str, Any]:
    """Get cross-nation comparison metrics from semantic layer."""
    conn = get_db_connection()

    try:
        # Get aggregate metrics
        metrics = conn.execute("""
            SELECT * FROM marts.agg_comparison_metrics
        """).fetchall()
        metrics_cols = [desc[0] for desc in conn.description]
        metrics_data = [dict(zip(metrics_cols, row)) for row in metrics]

        # Get level equivalences
        equivalences = conn.execute("""
            SELECT
                level_code,
                level_name,
                nation,
                equivalent_ireland,
                equivalent_england,
                equivalent_scotland,
                equivalent_wales,
                equivalent_ni
            FROM marts.dim_level
            WHERE nation = 'ireland'
            ORDER BY age_range_start
        """).fetchall()
        equiv_cols = [desc[0] for desc in conn.description]
        equiv_data = [dict(zip(equiv_cols, row)) for row in equivalences]

        return {
            "metrics": metrics_data,
            "level_equivalences": equiv_data,
            "nations_available": ["ireland"],  # Will expand as data is added
        }
    except Exception as e:
        logger.error(f"Error getting comparison metrics: {e}")
        return {"error": str(e), "metrics": [], "level_equivalences": []}
    finally:
        conn.close()


@router.get("/api/health")
async def curriculum_health() -> dict[str, Any]:
    """Health check for curriculum API."""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {e}"

    # Check vector search status
    try:
        from storage.curriculum_vectors import get_curriculum_search
        search = get_curriculum_search()
        vector_stats = await search.get_stats()
        vector_status = "healthy" if vector_stats.get("indexed", 0) > 0 else "no_data"
    except Exception as e:
        vector_status = f"error: {e}"
        vector_stats = {}

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "vector_search": vector_status,
        "vector_stats": vector_stats,
        "ag_ui": "enabled",
    }


# =============================================================================
# Vector Search Endpoints
# =============================================================================


@router.get("/api/curriculum/search/semantic")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    nation: str | None = Query(None, description="Filter by nation"),
    subject: str | None = Query(None, description="Filter by subject"),
    level: str | None = Query(None, description="Filter by level"),
) -> dict[str, Any]:
    """
    Semantic search over curriculum content.

    Uses vector embeddings to find semantically similar learning outcomes.
    """
    try:
        from storage.curriculum_vectors import get_curriculum_search

        search = get_curriculum_search()
        results = await search.search(
            query=q,
            limit=limit,
            nation=nation,
            subject=subject,
            level=level,
        )

        return {
            "query": q,
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return {"query": q, "count": 0, "results": [], "error": str(e)}


@router.get("/api/curriculum/search/similar/{outcome_id}")
async def find_similar(
    outcome_id: str,
    limit: int = Query(5, ge=1, le=20),
    same_nation: bool = Query(False, description="Only return from same nation"),
) -> dict[str, Any]:
    """
    Find outcomes similar to a given outcome.

    Useful for cross-nation curriculum alignment.
    """
    try:
        from storage.curriculum_vectors import get_curriculum_search

        search = get_curriculum_search()
        results = await search.find_similar_outcomes(
            outcome_id=outcome_id,
            limit=limit,
            same_nation=same_nation,
        )

        return {
            "source_outcome_id": outcome_id,
            "count": len(results),
            "similar": results,
        }
    except Exception as e:
        logger.error(f"Similar search error: {e}")
        return {"source_outcome_id": outcome_id, "count": 0, "similar": [], "error": str(e)}


@router.post("/api/curriculum/search/index")
async def index_vectors() -> dict[str, Any]:
    """
    Index curriculum outcomes into vector store.

    Reads from DuckDB semantic layer and creates embeddings.
    """
    try:
        from storage.curriculum_vectors import index_curriculum_from_duckdb

        count = await index_curriculum_from_duckdb(DB_PATH)
        return {
            "status": "success",
            "indexed": count,
            "message": f"Indexed {count} curriculum outcomes",
        }
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        return {"status": "error", "indexed": 0, "error": str(e)}


@router.get("/api/curriculum/search/stats")
async def vector_stats() -> dict[str, Any]:
    """Get vector search statistics."""
    try:
        from storage.curriculum_vectors import get_curriculum_search

        search = get_curriculum_search()
        stats = await search.get_stats()
        return {"status": "ok", **stats}
    except Exception as e:
        logger.error(f"Vector stats error: {e}")
        return {"status": "error", "error": str(e)}
