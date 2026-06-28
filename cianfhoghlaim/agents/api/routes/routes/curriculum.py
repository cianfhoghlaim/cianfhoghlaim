"""
Curriculum API Routes.

Search and retrieve Celtic language curriculum content.
Uses LanceDB for vector search with BGE-M3 multilingual embeddings.
"""

import os

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel

from ..services.curriculum_service import CurriculumService
from .payments import check_payment_or_free, create_402_response

router = APIRouter()

# Initialize curriculum service with LanceDB
_curriculum_service: CurriculumService | None = None


def get_curriculum_service() -> CurriculumService:
    """Get or create curriculum service singleton."""
    global _curriculum_service
    if _curriculum_service is None:
        lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")
        _curriculum_service = CurriculumService(uri=lance_uri)
    return _curriculum_service


class CurriculumSearchResult(BaseModel):
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


class CurriculumSearchResponse(BaseModel):
    """Response from curriculum search."""

    query: str
    results: list[CurriculumSearchResult]
    total: int
    filters: dict


class LearningOutcome(BaseModel):
    """A learning outcome from curriculum."""

    id: str
    description: str
    subject: str
    level: str
    nation: str
    prerequisites: list[str]
    related_topics: list[str]


@router.get("/search", response_model=CurriculumSearchResponse)
async def search_curriculum(
    query: str,
    nation: str | None = Query(None, description="Filter by nation (ireland, scotland, wales)"),
    language: str | None = Query(None, description="Filter by language (ga, gd, cy, en)"),
    level: str | None = Query(None, description="Filter by level (primary, secondary, higher)"),
    limit: int = Query(10, ge=1, le=50),
    x_session_id: str | None = Header(None),
    x_payment_id: str | None = Header(None),
):
    """
    Search Celtic curriculum content.

    Uses vector search with BGE-M3 multilingual embeddings via LanceDB.
    """
    # Check payment or free usage
    if not check_payment_or_free(x_session_id, "knowledge_search", x_payment_id):
        return create_402_response("knowledge_search")

    # Use LanceDB curriculum service
    service = get_curriculum_service()
    db_results = await service.search_curriculum(
        query=query,
        nation=nation,
        level=level,
        subject=None,  # Subject filter can be added if needed
        limit=limit,
    )

    # Convert service results to response model
    results = []
    for r in db_results:
        # Map nation to language code
        language_map = {"ireland": "ga", "scotland": "gd", "wales": "cy"}
        lang_code = language_map.get(r.get("nation", ""), "en")

        results.append(
            CurriculumSearchResult(
                id=r.get("id", ""),
                title=r.get("metadata", {}).get("strand", "") or r.get("subject", ""),
                content=r.get("text", ""),
                nation=r.get("nation", ""),
                language=r.get("metadata", {}).get("language", lang_code),
                level=r.get("level", ""),
                subject=r.get("subject", ""),
                learning_outcomes=[r.get("learning_outcome", "")] if r.get("learning_outcome") else [],
                score=r.get("score", 0.0),
            )
        )

    # Apply language filter if provided (not in service)
    if language:
        results = [r for r in results if r.language == language]

    # If no results from LanceDB, provide fallback sample data
    if not results:
        fallback_results = [
            CurriculumSearchResult(
                id="curriculum_ga_001",
                title="Basic Irish Greetings",
                content="Dia duit (Hello) is the standard greeting in Irish. The response is 'Dia is Muire duit' (God and Mary to you).",
                nation="ireland",
                language="ga",
                level="primary",
                subject="Irish Language",
                learning_outcomes=["Greet others in Irish", "Respond to greetings appropriately"],
                score=0.95,
            ),
            CurriculumSearchResult(
                id="curriculum_ga_002",
                title="Irish Verb Conjugation - An Aimsir Láithreach",
                content="The present tense (An Aimsir Láithreach) in Irish follows specific patterns.",
                nation="ireland",
                language="ga",
                level="primary",
                subject="Irish Grammar",
                learning_outcomes=["Conjugate regular verbs in present tense"],
                score=0.88,
            ),
            CurriculumSearchResult(
                id="curriculum_cy_001",
                title="Welsh Mutations - Treiglad Meddal",
                content="The soft mutation (treiglad meddal) is the most common mutation in Welsh.",
                nation="wales",
                language="cy",
                level="primary",
                subject="Welsh Grammar",
                learning_outcomes=["Identify when soft mutation applies"],
                score=0.82,
            ),
        ]
        # Apply filters to fallback
        if nation:
            fallback_results = [r for r in fallback_results if r.nation == nation]
        if language:
            fallback_results = [r for r in fallback_results if r.language == language]
        if level:
            fallback_results = [r for r in fallback_results if r.level == level]
        results = fallback_results[:limit]

    return CurriculumSearchResponse(
        query=query,
        results=results[:limit],
        total=len(results),
        filters={
            "nation": nation,
            "language": language,
            "level": level,
        },
    )


@router.get("/outcomes")
async def get_learning_outcomes(
    topic: str | None = Query(None),
    nation: str | None = Query(None),
    level: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Get curriculum learning outcomes."""
    outcomes = [
        LearningOutcome(
            id="lo_ga_speak_001",
            description="Engage in simple conversations using everyday vocabulary",
            subject="Irish Language",
            level="primary",
            nation="ireland",
            prerequisites=["Basic greetings", "Numbers 1-10"],
            related_topics=["Greetings", "Self-introduction", "Daily activities"],
        ),
        LearningOutcome(
            id="lo_ga_read_001",
            description="Read and understand simple texts in Irish",
            subject="Irish Language",
            level="primary",
            nation="ireland",
            prerequisites=["Alphabet recognition", "Basic vocabulary"],
            related_topics=["Short stories", "Signs", "Simple instructions"],
        ),
        LearningOutcome(
            id="lo_gd_speak_001",
            description="Use basic Gaelic phrases in everyday situations",
            subject="Scottish Gaelic",
            level="primary",
            nation="scotland",
            prerequisites=["Greetings", "Basic nouns"],
            related_topics=["Weather", "Family", "School"],
        ),
        LearningOutcome(
            id="lo_cy_speak_001",
            description="Communicate in Welsh about familiar topics",
            subject="Welsh Language",
            level="primary",
            nation="wales",
            prerequisites=["Greetings", "Mutations basics"],
            related_topics=["Home", "School", "Hobbies"],
        ),
    ]

    # Apply filters
    if topic:
        topic_lower = topic.lower()
        outcomes = [o for o in outcomes if topic_lower in o.description.lower() or
                    any(topic_lower in t.lower() for t in o.related_topics)]
    if nation:
        outcomes = [o for o in outcomes if o.nation == nation]
    if level:
        outcomes = [o for o in outcomes if o.level == level]

    return {
        "outcomes": outcomes[:limit],
        "total": len(outcomes),
    }


@router.get("/nations")
async def get_supported_nations():
    """Get list of supported nations and their curriculum info."""
    return {
        "nations": [
            {
                "id": "ireland",
                "name": "Ireland",
                "native_name": "Éire",
                "languages": [
                    {"code": "ga", "name": "Irish", "native_name": "Gaeilge"}
                ],
                "curriculum_authority": "NCCA (National Council for Curriculum and Assessment)",
                "levels": ["primary", "secondary", "higher"],
            },
            {
                "id": "scotland",
                "name": "Scotland",
                "native_name": "Alba",
                "languages": [
                    {"code": "gd", "name": "Scottish Gaelic", "native_name": "Gàidhlig"}
                ],
                "curriculum_authority": "SQA (Scottish Qualifications Authority)",
                "levels": ["primary", "secondary", "higher"],
            },
            {
                "id": "wales",
                "name": "Wales",
                "native_name": "Cymru",
                "languages": [
                    {"code": "cy", "name": "Welsh", "native_name": "Cymraeg"}
                ],
                "curriculum_authority": "Qualifications Wales",
                "levels": ["primary", "secondary", "higher"],
            },
        ],
    }


@router.get("/subjects/{nation}")
async def get_subjects_by_nation(nation: str):
    """Get curriculum subjects for a nation."""
    subjects = {
        "ireland": [
            {"id": "irish_language", "name": "Irish Language", "native_name": "Gaeilge"},
            {"id": "irish_literature", "name": "Irish Literature", "native_name": "Litríocht na Gaeilge"},
            {"id": "irish_history", "name": "Irish History", "native_name": "Stair na hÉireann"},
            {"id": "irish_folklore", "name": "Irish Folklore", "native_name": "Béaloideas"},
        ],
        "scotland": [
            {"id": "gaelic_language", "name": "Scottish Gaelic", "native_name": "Gàidhlig"},
            {"id": "gaelic_literature", "name": "Gaelic Literature", "native_name": "Litreachas Gàidhlig"},
            {"id": "scottish_history", "name": "Scottish History", "native_name": "Eachdraidh na h-Alba"},
        ],
        "wales": [
            {"id": "welsh_language", "name": "Welsh Language", "native_name": "Cymraeg"},
            {"id": "welsh_literature", "name": "Welsh Literature", "native_name": "Llenyddiaeth Gymraeg"},
            {"id": "welsh_history", "name": "Welsh History", "native_name": "Hanes Cymru"},
        ],
    }

    if nation not in subjects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nation '{nation}' not found",
        )

    return {
        "nation": nation,
        "subjects": subjects[nation],
    }
