"""
Hybrid Search API Routes.

Provides unified search across curriculum and mythology content
using vector similarity and knowledge graph traversal.
"""

from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

# Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
# (Phase 1 §2.2): the legacy `from ...knowledge_graph import
# HybridSearchConfig` import pointed at a non-existent module. Route
# through the canonical MemoryRouter instead (the Cognee + LanceDB +
# Graphiti RRF hybrid search).
try:
    from agents.meaisinfhoghlaim.firecrawl_mcp.memory.router import MemoryRouter
except ImportError:
    MemoryRouter = None  # type: ignore[assignment]

router = APIRouter()


class SearchRequest(BaseModel):
    """Search request parameters."""
    query: str = Field(..., min_length=1, max_length=1000)
    mode: Literal["vector", "graph", "hybrid"] = "hybrid"
    content_types: list[str] | None = None
    limit: int = Field(default=20, ge=1, le=100)
    vector_weight: float = Field(default=0.6, ge=0, le=1)
    graph_weight: float = Field(default=0.4, ge=0, le=1)
    include_relationships: bool = True


class SearchResultItem(BaseModel):
    """Individual search result."""
    id: str
    content_type: str
    title: str
    content: str
    score: float
    source: str
    metadata: dict = Field(default_factory=dict)
    related_entities: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    mode: str
    total: int
    results: list[SearchResultItem]


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Perform hybrid search across curriculum and mythology.

    Modes:
    - vector: Pure semantic similarity using BGE-M3 embeddings
    - graph: Knowledge graph traversal for relationship queries
    - hybrid: Combined vector + graph with reciprocal rank fusion

    Content types:
    - curriculum: Educational content from NCCA, WJEC, SQA
    - character: Mythological characters (gods, heroes, monsters)
    - story: Tales, sagas, and cycles
    - location: Mythological and sacred sites
    - mythology: All mythology content
    """
    engine = get_search_engine()

    config = HybridSearchConfig(
        vector_weight=request.vector_weight,
        graph_weight=request.graph_weight,
        max_results=request.limit,
        include_relationships=request.include_relationships,
    )

    results = await engine.search(
        query=request.query,
        mode=SearchMode(request.mode),
        content_types=request.content_types,
        config=config,
    )

    return SearchResponse(
        query=request.query,
        mode=request.mode,
        total=len(results),
        results=[
            SearchResultItem(
                id=r.id,
                content_type=r.content_type,
                title=r.title,
                content=r.content,
                score=r.score,
                source=r.source,
                metadata=r.metadata,
                related_entities=r.related_entities,
            )
            for r in results
        ],
    )


@router.get("/curriculum")
async def search_curriculum(
    query: str = Query(..., min_length=1),
    nation: str | None = None,
    level: str | None = None,
    subject: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Search Celtic curriculum content.

    Nations: ireland, wales, scotland, cornwall, brittany, isle_of_man
    Levels: Varies by nation (e.g., junior_cycle, leaving_cert for Ireland)
    Subjects: language, literature, culture, history, geography
    """
    engine = get_search_engine()

    results = await engine.search_curriculum(
        query=query,
        nation=nation,
        level=level,
        subject=subject,
        limit=limit,
    )

    return {
        "query": query,
        "filters": {"nation": nation, "level": level, "subject": subject},
        "total": len(results),
        "results": [r.model_dump() for r in results],
    }


@router.get("/mythology")
async def search_mythology(
    query: str = Query(..., min_length=1),
    tradition: str | None = None,
    cycle: str | None = None,
    content_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Search Celtic mythology content.

    Traditions: irish_mythology, welsh_mythology, scottish_folklore, etc.
    Cycles: mythological_cycle, ulster_cycle, fenian_cycle, mabinogion, etc.
    Content types: character, story, location
    """
    engine = get_search_engine()

    results = await engine.search_mythology(
        query=query,
        tradition=tradition,
        cycle=cycle,
        content_type=content_type,
        limit=limit,
    )

    return {
        "query": query,
        "filters": {"tradition": tradition, "cycle": cycle, "content_type": content_type},
        "total": len(results),
        "results": [r.model_dump() for r in results],
    }


@router.get("/related/{content_type}/{entity_id}")
async def find_related(
    content_type: str,
    entity_id: str,
    max_depth: int = Query(default=2, ge=1, le=5),
):
    """
    Find content related to a specific entity.

    Uses knowledge graph traversal to find:
    - Related characters (family, allies, enemies)
    - Related stories (shared characters, locations)
    - Related curriculum (teaching the same concepts)
    """
    engine = get_search_engine()

    results = await engine.find_related_content(
        entity_id=entity_id,
        content_type=content_type,
        max_depth=max_depth,
    )

    return {
        "entity_id": entity_id,
        "content_type": content_type,
        "total": len(results),
        "related": [r.model_dump() for r in results],
    }


@router.get("/suggest")
async def suggest_queries(
    partial: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=5, ge=1, le=20),
):
    """
    Get search query suggestions based on partial input.

    Returns popular and relevant completions.
    """
    # Common Celtic mythology terms
    suggestions = [
        "Cú Chulainn",
        "Tuatha Dé Danann",
        "Fionn mac Cumhaill",
        "Táin Bó Cúailnge",
        "Mabinogion",
        "Irish greetings",
        "Welsh mutations",
        "Scottish Gaelic vocabulary",
        "Celtic gods",
        "Fenian Cycle",
        "Ulster Cycle",
        "Tír na nÓg",
    ]

    # Filter by partial match
    partial_lower = partial.lower()
    matches = [
        s for s in suggestions
        if partial_lower in s.lower()
    ]

    return {
        "partial": partial,
        "suggestions": matches[:limit],
    }
