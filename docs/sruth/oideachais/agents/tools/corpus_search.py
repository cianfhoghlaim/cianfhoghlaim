"""
Corpus Search Tools for Celtic Language Agents.

Provides LanceDB vector search and structured queries for Celtic corpora:
- Semantic search across all corpora
- Dúchas folklore collection search
- Teanglann dictionary lookup
- Corpus statistics
"""
from __future__ import annotations

import logging
import os
from typing import Optional, List, Literal, Any

import duckdb
import lancedb
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


# Pydantic models for tool outputs
class SearchResult(BaseModel):
    """A single corpus search result."""

    text: str = Field(description="Matching text content")
    source: str = Field(description="Source collection (duchas, canuint, ud, gaois)")
    language: str = Field(description="Language code")
    score: float = Field(description="Relevance score (0-1)")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    url: Optional[str] = Field(default=None, description="Source URL if available")


class CorpusStats(BaseModel):
    """Statistics about the Celtic corpus."""

    total_documents: int
    by_language: dict[str, int]
    by_source: dict[str, int]
    total_tokens: int


class DictionaryEntry(BaseModel):
    """A dictionary lookup result."""

    headword: str = Field(description="Dictionary headword")
    language: str = Field(description="Language code")
    part_of_speech: Optional[str] = Field(default=None, description="Part of speech")
    definition_ga: Optional[str] = Field(default=None, description="Irish definition")
    definition_en: Optional[str] = Field(default=None, description="English definition")
    examples: List[str] = Field(default_factory=list, description="Example sentences")
    etymology: Optional[str] = Field(default=None, description="Etymology if available")
    related_words: List[str] = Field(default_factory=list, description="Related words")


# Configuration defaults
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_LANCEDB_PATH = "./storage/data/lancedb"
DEFAULT_DUCKDB_PATH = "./storage/data/celtic_education.duckdb"


# Global model cache
_embedding_model: Optional[SentenceTransformer] = None


def _get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        model_name = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        logger.info(f"Loading embedding model: {model_name}")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def _get_lancedb_connection() -> lancedb.DBConnection:
    """Get LanceDB connection."""
    lancedb_path = os.getenv("LANCEDB_PATH", DEFAULT_LANCEDB_PATH)
    return lancedb.connect(lancedb_path)


def _get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Get DuckDB connection."""
    duckdb_path = os.getenv("DUCKDB_PATH", DEFAULT_DUCKDB_PATH)
    return duckdb.connect(duckdb_path, read_only=True)


async def search_corpus_lancedb(
    query: str,
    languages: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    limit: int = 10,
    min_score: float = 0.5,
) -> List[SearchResult]:
    """
    Search Celtic corpora using LanceDB vector similarity.

    Uses BGE-M3 embeddings for multilingual semantic search across
    all indexed Celtic language texts.

    Args:
        query: Natural language search query
        languages: Filter by language codes (ga, gd, cy, etc.)
        sources: Filter by sources (duchas, canuint, ud, gaois)
        limit: Maximum results to return
        min_score: Minimum similarity score (0-1)

    Returns:
        List of SearchResult with matching texts and metadata
    """
    try:
        db = _get_lancedb_connection()
        model = _get_embedding_model()

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        # Search the celtic_texts table
        table = db.open_table("celtic_texts")

        # Build search with optional filters
        search = table.search(query_embedding).limit(limit * 2)  # Over-fetch for filtering

        # Execute search
        results = search.to_pandas()

        # Apply filters
        if languages:
            results = results[results["language"].isin(languages)]
        if sources:
            results = results[results["source"].isin(sources)]

        # Convert to SearchResult objects
        search_results = []
        for _, row in results.head(limit).iterrows():
            score = 1.0 - row.get("_distance", 0.5)  # Convert distance to similarity
            if score >= min_score:
                search_results.append(
                    SearchResult(
                        text=row.get("text", ""),
                        source=row.get("source", "unknown"),
                        language=row.get("language", ""),
                        score=score,
                        metadata={
                            "doc_id": row.get("doc_id"),
                            "title": row.get("title"),
                            "date": row.get("date"),
                        },
                        url=row.get("url"),
                    )
                )

        logger.info(f"Found {len(search_results)} results for query: {query[:50]}...")
        return search_results

    except Exception as e:
        logger.error(f"Corpus search error: {e}")
        return []


async def search_duchas_collection(
    query: str,
    collection: Literal["cbe", "cbes", "cbeg", "cbef"] = "cbes",
    county: Optional[str] = None,
    school: Optional[str] = None,
    limit: int = 10,
) -> List[SearchResult]:
    """
    Search the Dúchas.ie National Folklore Collection.

    Collections:
    - cbes: Schools' Collection (1937-1939)
    - cbe: Main Manuscript Collection
    - cbeg: Photographic Collection
    - cbef: Audio Collection

    Args:
        query: Search query (semantic or keyword)
        collection: Dúchas collection to search
        county: Filter by Irish county name
        school: Filter by school name (for cbes)
        limit: Maximum results

    Returns:
        List of SearchResult with folklore texts
    """
    try:
        db = _get_lancedb_connection()
        model = _get_embedding_model()

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        # Open collection-specific table
        table_name = f"duchas_{collection}"
        try:
            table = db.open_table(table_name)
        except Exception:
            # Fall back to main celtic_texts table with source filter
            table = db.open_table("celtic_texts")

        # Search
        results = table.search(query_embedding).limit(limit * 2).to_pandas()

        # Filter by collection if using main table
        results = results[results.get("collection", results.get("source", "")) == collection]

        # Apply optional filters
        if county:
            results = results[results["county"].str.contains(county, case=False, na=False)]
        if school and collection == "cbes":
            results = results[results["school"].str.contains(school, case=False, na=False)]

        # Convert to SearchResult
        search_results = []
        for _, row in results.head(limit).iterrows():
            search_results.append(
                SearchResult(
                    text=row.get("text", row.get("transcription", "")),
                    source="duchas",
                    language="ga",
                    score=1.0 - row.get("_distance", 0.5),
                    metadata={
                        "collection": collection,
                        "volume_id": row.get("volume_id"),
                        "page": row.get("page"),
                        "county": row.get("county"),
                        "school": row.get("school"),
                        "collector": row.get("collector"),
                        "informant": row.get("informant"),
                    },
                    url=row.get("url", f"https://www.duchas.ie/en/{collection}/{row.get('id', '')}"),
                )
            )

        return search_results

    except Exception as e:
        logger.error(f"Dúchas search error: {e}")
        return []


async def search_teanglann(
    word: str,
    language: str = "ga",
    include_examples: bool = True,
    include_etymology: bool = False,
) -> List[DictionaryEntry]:
    """
    Search Teanglann.ie Irish dictionary.

    Provides definitions, examples, and grammatical information
    from the authoritative Irish dictionary.

    Args:
        word: Word to look up
        language: Language code (ga for Irish)
        include_examples: Include example sentences
        include_etymology: Include etymology from eDIL

    Returns:
        List of DictionaryEntry results
    """
    try:
        conn = _get_duckdb_connection()

        # Search dictionary table
        query = """
            SELECT
                headword,
                language,
                part_of_speech,
                definition_ga,
                definition_en,
                examples,
                etymology,
                related_words
            FROM dictionary_entries
            WHERE language = ?
              AND (headword = ? OR headword LIKE ? || '%')
            ORDER BY
                CASE WHEN headword = ? THEN 0 ELSE 1 END,
                headword
            LIMIT 10
        """

        result = conn.execute(query, [language, word, word, word]).fetchall()

        entries = []
        for row in result:
            entries.append(
                DictionaryEntry(
                    headword=row[0],
                    language=row[1],
                    part_of_speech=row[2],
                    definition_ga=row[3],
                    definition_en=row[4],
                    examples=row[5] if include_examples and row[5] else [],
                    etymology=row[6] if include_etymology else None,
                    related_words=row[7] if row[7] else [],
                )
            )

        return entries

    except Exception as e:
        logger.error(f"Dictionary search error: {e}")
        return []


async def get_corpus_stats() -> CorpusStats:
    """
    Get statistics about the Celtic corpus.

    Returns document counts by language and source,
    and total token count across all corpora.
    """
    try:
        conn = _get_duckdb_connection()

        # Total documents
        total = conn.execute("SELECT COUNT(*) FROM celtic_documents").fetchone()[0]

        # By language
        by_lang = conn.execute("""
            SELECT language, COUNT(*) as count
            FROM celtic_documents
            GROUP BY language
        """).fetchall()
        by_language = {row[0]: row[1] for row in by_lang}

        # By source
        by_src = conn.execute("""
            SELECT source, COUNT(*) as count
            FROM celtic_documents
            GROUP BY source
        """).fetchall()
        by_source = {row[0]: row[1] for row in by_src}

        # Total tokens
        total_tokens = conn.execute("""
            SELECT COALESCE(SUM(token_count), 0)
            FROM celtic_documents
        """).fetchone()[0]

        return CorpusStats(
            total_documents=total,
            by_language=by_language,
            by_source=by_source,
            total_tokens=total_tokens,
        )

    except Exception as e:
        logger.error(f"Stats query error: {e}")
        return CorpusStats(
            total_documents=0,
            by_language={},
            by_source={},
            total_tokens=0,
        )
