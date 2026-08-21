"""
Semantic Search API Routes.

Unified search across all domains:
- Curriculum content (Ireland, UK, all nations)
- Folklore and cultural content (Dúchas)
- Terminology (Téarma)
- Pronunciation (Canuint)

Endpoints:
    POST /search/curriculum - Search curriculum content
    POST /search/folklore - Search folklore content
    POST /search/terminology - Search terminology
    POST /search/unified - Search across all domains
    GET /search/similar/{id} - Find similar content
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/search", tags=["search"])


# ============================================================================
# Models
# ============================================================================

class SearchDomain(str, Enum):
    """Available search domains."""

    CURRICULUM = "curriculum"
    FOLKLORE = "folklore"
    TERMINOLOGY = "terminology"
    PRONUNCIATION = "pronunciation"
    ALL = "all"


class LanguageFilter(str, Enum):
    """Language filter options."""

    EN = "en"
    GA = "ga"
    GD = "gd"
    CY = "cy"
    GV = "gv"
    KW = "kw"
    BR = "br"
    ALL = "all"


class NationFilter(str, Enum):
    """Nation filter options."""

    IRELAND = "ireland"
    ENGLAND = "england"
    SCOTLAND = "scotland"
    WALES = "wales"
    NORTHERN_IRELAND = "northern_ireland"
    ISLE_OF_MAN = "isle_of_man"
    ALL = "all"


class SearchRequest(BaseModel):
    """Search request body."""

    query: str = Field(..., min_length=2, max_length=1000, description="Search query text")
    domain: SearchDomain = Field(default=SearchDomain.ALL, description="Domain to search")
    language: LanguageFilter = Field(default=LanguageFilter.ALL, description="Filter by language")
    nation: NationFilter = Field(default=NationFilter.ALL, description="Filter by nation")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Results offset for pagination")
    include_translations: bool = Field(default=False, description="Include translated versions")


class SearchResult(BaseModel):
    """Individual search result."""

    id: str
    title: str | None = None
    content: str
    domain: str
    language: str | None = None
    nation: str | None = None
    source: str | None = None
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response."""

    query: str
    domain: str
    total_results: int
    results: list[SearchResult]
    facets: dict[str, dict[str, int]] = Field(default_factory=dict)


class SimilarRequest(BaseModel):
    """Similar content request."""

    source_id: str = Field(..., description="Source document ID")
    domain: SearchDomain = Field(default=SearchDomain.ALL)
    limit: int = Field(default=10, ge=1, le=50)


# ============================================================================
# Search Implementation
# ============================================================================

class SemanticSearcher:
    """
    Semantic search across LanceDB tables.
    """

    def __init__(self, lancedb_path: str = "./storage/data/lancedb"):
        self.lancedb_path = lancedb_path
        self._db = None
        self._model = None

    def _get_db(self):
        """Lazy-load LanceDB connection."""
        if self._db is None:
            import lancedb
            self._db = lancedb.connect(self.lancedb_path)
        return self._db

    def _get_model(self):
        """Lazy-load embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        return self._model

    def _get_tables_for_domain(self, domain: SearchDomain) -> list[str]:
        """Get LanceDB tables for a domain."""
        table_mapping = {
            SearchDomain.CURRICULUM: ["oideachas.curriculum", "oileain.curriculum"],
            SearchDomain.FOLKLORE: ["teanga.folklore"],
            SearchDomain.TERMINOLOGY: ["teanga.terminology"],
            SearchDomain.PRONUNCIATION: ["teanga.pronunciation"],
            SearchDomain.ALL: [
                "oideachas.curriculum",
                "oileain.curriculum",
                "teanga.folklore",
                "teanga.terminology",
            ],
        }
        return table_mapping.get(domain, [])

    def search(
        self,
        query: str,
        domain: SearchDomain = SearchDomain.ALL,
        language: str | None = None,
        nation: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Execute semantic search.

        Returns (results, total_count).
        """
        db = self._get_db()
        model = self._get_model()

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        tables = self._get_tables_for_domain(domain)
        all_results = []

        for table_name in tables:
            if table_name not in db.table_names():
                continue

            table = db.open_table(table_name)

            # Build filter string
            filters = []
            if language and language != "all":
                filters.append(f"language = '{language}'")
            if nation and nation != "all":
                filters.append(f"nation = '{nation}'")

            filter_str = " AND ".join(filters) if filters else None

            # Execute search
            try:
                search_query = table.search(query_embedding).limit(limit + offset)
                if filter_str:
                    search_query = search_query.where(filter_str)

                results = search_query.to_list()

                for r in results:
                    all_results.append({
                        "id": r.get("id", f"{table_name}_{hash(r.get('text', ''))}"),
                        "title": r.get("title"),
                        "content": r.get("text", "")[:500],
                        "domain": table_name.split(".")[0],
                        "language": r.get("language"),
                        "nation": r.get("nation"),
                        "source": r.get("source"),
                        "score": float(r.get("_distance", 0)),
                        "metadata": {
                            k: v for k, v in r.items()
                            if k not in ["id", "title", "text", "vector", "_distance"]
                        },
                    })
            except Exception:
                continue

        # Sort by score (lower distance = better)
        all_results.sort(key=lambda x: x["score"])

        # Apply offset and limit
        total = len(all_results)
        results = all_results[offset:offset + limit]

        return results, total

    def find_similar(
        self,
        source_id: str,
        domain: SearchDomain = SearchDomain.ALL,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Find content similar to a given document.
        """
        db = self._get_db()
        tables = self._get_tables_for_domain(domain)

        # Find the source document
        source_doc = None
        source_table = None

        for table_name in tables:
            if table_name not in db.table_names():
                continue

            table = db.open_table(table_name)
            try:
                results = table.search().where(f"id = '{source_id}'").limit(1).to_list()
                if results:
                    source_doc = results[0]
                    source_table = table_name
                    break
            except Exception:
                continue

        if not source_doc:
            return []

        # Use the source document's embedding for similarity search
        source_vector = source_doc.get("vector")
        if not source_vector:
            return []

        all_results = []

        for table_name in tables:
            if table_name not in db.table_names():
                continue

            table = db.open_table(table_name)

            try:
                results = table.search(source_vector).limit(limit + 1).to_list()

                for r in results:
                    # Skip the source document itself
                    if r.get("id") == source_id:
                        continue

                    all_results.append({
                        "id": r.get("id", f"{table_name}_{hash(r.get('text', ''))}"),
                        "title": r.get("title"),
                        "content": r.get("text", "")[:500],
                        "domain": table_name.split(".")[0],
                        "score": float(r.get("_distance", 0)),
                    })
            except Exception:
                continue

        all_results.sort(key=lambda x: x["score"])
        return all_results[:limit]


# Global searcher instance
_searcher: SemanticSearcher | None = None


def get_searcher() -> SemanticSearcher:
    """Get or create searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = SemanticSearcher()
    return _searcher


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/curriculum", response_model=SearchResponse)
async def search_curriculum(request: SearchRequest) -> SearchResponse:
    """
    Search curriculum content across all nations.

    Searches Irish and UK curriculum specifications, learning outcomes,
    and educational content.
    """
    searcher = get_searcher()

    results, total = searcher.search(
        query=request.query,
        domain=SearchDomain.CURRICULUM,
        language=request.language.value if request.language != LanguageFilter.ALL else None,
        nation=request.nation.value if request.nation != NationFilter.ALL else None,
        limit=request.limit,
        offset=request.offset,
    )

    return SearchResponse(
        query=request.query,
        domain="curriculum",
        total_results=total,
        results=[SearchResult(**r) for r in results],
    )


@router.post("/folklore", response_model=SearchResponse)
async def search_folklore(request: SearchRequest) -> SearchResponse:
    """
    Search folklore and cultural content.

    Searches Dúchas National Folklore Collection.
    """
    searcher = get_searcher()

    results, total = searcher.search(
        query=request.query,
        domain=SearchDomain.FOLKLORE,
        language=request.language.value if request.language != LanguageFilter.ALL else None,
        limit=request.limit,
        offset=request.offset,
    )

    return SearchResponse(
        query=request.query,
        domain="folklore",
        total_results=total,
        results=[SearchResult(**r) for r in results],
    )


@router.post("/terminology", response_model=SearchResponse)
async def search_terminology(request: SearchRequest) -> SearchResponse:
    """
    Search Irish terminology database.

    Searches Téarma.ie for Irish/English term equivalents.
    """
    searcher = get_searcher()

    results, total = searcher.search(
        query=request.query,
        domain=SearchDomain.TERMINOLOGY,
        limit=request.limit,
        offset=request.offset,
    )

    return SearchResponse(
        query=request.query,
        domain="terminology",
        total_results=total,
        results=[SearchResult(**r) for r in results],
    )


@router.post("/unified", response_model=SearchResponse)
async def search_unified(request: SearchRequest) -> SearchResponse:
    """
    Search across all domains.

    Unified search across curriculum, folklore, terminology, and more.
    """
    searcher = get_searcher()

    results, total = searcher.search(
        query=request.query,
        domain=SearchDomain.ALL,
        language=request.language.value if request.language != LanguageFilter.ALL else None,
        nation=request.nation.value if request.nation != NationFilter.ALL else None,
        limit=request.limit,
        offset=request.offset,
    )

    # Calculate facets
    facets = {
        "domain": {},
        "language": {},
        "nation": {},
    }
    for r in results:
        domain = r.get("domain", "unknown")
        facets["domain"][domain] = facets["domain"].get(domain, 0) + 1

        lang = r.get("language") or "unknown"
        facets["language"][lang] = facets["language"].get(lang, 0) + 1

        nation = r.get("nation") or "unknown"
        facets["nation"][nation] = facets["nation"].get(nation, 0) + 1

    return SearchResponse(
        query=request.query,
        domain="all",
        total_results=total,
        results=[SearchResult(**r) for r in results],
        facets=facets,
    )


@router.get("/similar/{source_id}")
async def find_similar(
    source_id: str,
    domain: SearchDomain = Query(default=SearchDomain.ALL),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[SearchResult]:
    """
    Find content similar to a given document.
    """
    searcher = get_searcher()

    results = searcher.find_similar(
        source_id=source_id,
        domain=domain,
        limit=limit,
    )

    if not results:
        raise HTTPException(status_code=404, detail=f"Source document not found: {source_id}")

    return [SearchResult(**r) for r in results]
