"""LanceDB Search Module.

Provides vector, full-text, and hybrid search capabilities for code and documentation.
Follows patterns from dlt_lance.py example.

Search Types:
- Vector Search: Semantic similarity using embeddings
- FTS (Full-Text Search): BM25-based keyword matching
- Hybrid Search: Combines vector and FTS with reranking
"""

import math
from dataclasses import dataclass
from typing import Any, Literal

import lancedb
from lancedb.table import Table

from cocoindex.embeddings import EmbeddingFunction


@dataclass
class SearchResult:
    """Represents a search result."""
    filename: str
    location: str
    code: str
    language: str
    score: float
    search_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "location": self.location,
            "code": self.code,
            "language": self.language,
            "score": self.score,
            "search_type": self.search_type,
        }


class LanceDBSearch:
    """LanceDB search interface with vector, FTS, and hybrid search.

    Provides multiple search strategies:
    - vector: Semantic similarity using cosine distance
    - fts: Full-text search using BM25
    - hybrid: Combination of vector and FTS with optional reranking

    Example:
        search = LanceDBSearch("./data/github_intelligence.lancedb", "dlt_code")
        results = search.hybrid_search("how to create a pipeline", limit=10)
    """

    def __init__(
        self,
        db_uri: str,
        table_name: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """Initialize LanceDB search.

        Args:
            db_uri: Path to LanceDB database
            table_name: Name of the table to search
            embedding_model: Model for generating query embeddings
        """
        self.db_uri = db_uri
        self.table_name = table_name
        self.embedding_fn = EmbeddingFunction(embedding_model)
        self._db = None
        self._table = None

    @property
    def db(self) -> lancedb.DBConnection:
        """Lazy-load database connection."""
        if self._db is None:
            self._db = lancedb.connect(self.db_uri)
        return self._db

    @property
    def table(self) -> Table:
        """Lazy-load table."""
        if self._table is None:
            self._table = self.db.open_table(self.table_name)
        return self._table

    def vector_search(
        self,
        query: str,
        limit: int = 10,
        filter_expr: str | None = None,
    ) -> list[SearchResult]:
        """Perform vector similarity search.

        Uses cosine similarity to find semantically similar code chunks.

        Args:
            query: Search query
            limit: Maximum results to return
            filter_expr: Optional SQL filter expression (e.g., "language = 'python'")

        Returns:
            List of SearchResult objects
        """
        query_embedding = self.embedding_fn.embed_query(query)

        search = self.table.search(query_embedding).limit(limit)

        if filter_expr:
            search = search.where(filter_expr)

        results = search.to_list()

        return [
            SearchResult(
                filename=r["filename"],
                location=r["location"],
                code=r["code"],
                language=r.get("language", ""),
                score=1.0 - r.get("_distance", 0),  # Convert distance to similarity
                search_type="vector",
            )
            for r in results
        ]

    def fts_search(
        self,
        query: str,
        limit: int = 10,
        filter_expr: str | None = None,
    ) -> list[SearchResult]:
        """Perform full-text search using BM25.

        Uses keyword matching with BM25 scoring.

        Args:
            query: Search query
            limit: Maximum results to return
            filter_expr: Optional SQL filter expression

        Returns:
            List of SearchResult objects
        """
        # Create FTS index if needed
        try:
            self.table.create_fts_index("code", replace=False)
        except Exception:
            pass  # Index may already exist

        search = self.table.search(query, query_type="fts").limit(limit)

        if filter_expr:
            search = search.where(filter_expr)

        results = search.to_list()

        return [
            SearchResult(
                filename=r["filename"],
                location=r["location"],
                code=r["code"],
                language=r.get("language", ""),
                score=r.get("_score", 0),
                search_type="fts",
            )
            for r in results
        ]

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        filter_expr: str | None = None,
        reranker: Literal["rrf", "cross_encoder", "colbert", None] = "rrf",
    ) -> list[SearchResult]:
        """Perform hybrid search combining vector and FTS.

        Runs both vector and full-text search, then combines results
        using a reranking strategy.

        Args:
            query: Search query
            limit: Maximum results to return
            filter_expr: Optional SQL filter expression
            reranker: Reranking strategy ("rrf", "cross_encoder", "colbert", or None)

        Returns:
            List of SearchResult objects
        """
        query_embedding = self.embedding_fn.embed_query(query)

        # Create FTS index if needed
        try:
            self.table.create_fts_index("code", replace=False)
        except Exception:
            pass

        # Build hybrid search
        search = self.table.search(query_type="hybrid").vector(query_embedding).text(query).limit(limit)

        if filter_expr:
            search = search.where(filter_expr)

        # Apply reranker
        if reranker:
            reranker_obj = self._get_reranker(reranker)
            if reranker_obj:
                search = search.rerank(reranker=reranker_obj)

        results = search.to_list()

        return [
            SearchResult(
                filename=r["filename"],
                location=r["location"],
                code=r["code"],
                language=r.get("language", ""),
                score=r.get("_relevance_score", r.get("_score", 0)),
                search_type="hybrid",
            )
            for r in results
        ]

    def _get_reranker(self, reranker_type: str):
        """Get a reranker instance.

        Available rerankers:
        - rrf: Reciprocal Rank Fusion (fast, no model needed)
        - cross_encoder: Cross-encoder model (more accurate, slower)
        - colbert: ColBERT late interaction (good balance)
        """
        try:
            from lancedb.rerankers import RRFReranker, CrossEncoderReranker, ColbertReranker

            if reranker_type == "rrf":
                return RRFReranker()
            elif reranker_type == "cross_encoder":
                return CrossEncoderReranker()
            elif reranker_type == "colbert":
                return ColbertReranker()
        except ImportError:
            print(f"Warning: Reranker '{reranker_type}' not available. Install lancedb[rerankers].")
            return None

        return None

    def search(
        self,
        query: str,
        search_type: Literal["vector", "fts", "hybrid"] = "hybrid",
        limit: int = 10,
        filter_language: str | None = None,
        **kwargs,
    ) -> list[SearchResult]:
        """Unified search interface.

        Args:
            query: Search query
            search_type: Type of search to perform
            limit: Maximum results
            filter_language: Optional language filter
            **kwargs: Additional arguments passed to specific search method

        Returns:
            List of SearchResult objects
        """
        filter_expr = f"language = '{filter_language}'" if filter_language else None

        if search_type == "vector":
            return self.vector_search(query, limit, filter_expr)
        elif search_type == "fts":
            return self.fts_search(query, limit, filter_expr)
        else:
            return self.hybrid_search(query, limit, filter_expr, **kwargs)

    def get_table_info(self) -> dict[str, Any]:
        """Get information about the search table.

        Returns:
            Dictionary with table statistics
        """
        schema = self.table.schema
        count = self.table.count_rows()

        return {
            "table_name": self.table_name,
            "row_count": count,
            "columns": [f.name for f in schema],
            "db_uri": self.db_uri,
        }


def compare_search_strategies(
    db_uri: str,
    table_name: str,
    query: str,
    limit: int = 5,
) -> dict[str, list[SearchResult]]:
    """Compare different search strategies.

    Useful for understanding the strengths and weaknesses of each approach.

    Args:
        db_uri: Path to LanceDB database
        table_name: Table to search
        query: Search query
        limit: Results per strategy

    Returns:
        Dictionary mapping strategy names to results
    """
    search = LanceDBSearch(db_uri, table_name)

    return {
        "vector": search.vector_search(query, limit),
        "fts": search.fts_search(query, limit),
        "hybrid_rrf": search.hybrid_search(query, limit, reranker="rrf"),
    }


# DLT LanceDB adapter pattern (from dlt_lance.py)
def create_dlt_lancedb_pipeline(
    pipeline_name: str,
    table_name: str,
    embed_cols: list[str],
    lancedb_dir: str = "./data/lancedb",
):
    """Create a DLT pipeline with LanceDB destination.

    Follows the pattern from dlt_lance.py for embedding at ingestion time.

    Args:
        pipeline_name: Name of the pipeline
        table_name: LanceDB table name
        embed_cols: Columns to embed
        lancedb_dir: Path to LanceDB directory

    Returns:
        Configured DLT pipeline
    """
    import os
    import dlt
    from dlt.destinations.adapters import lancedb_adapter

    os.environ["DESTINATION__LANCEDB__LANCE_URI"] = lancedb_dir
    os.environ["DESTINATION__LANCEDB__EMBEDDING_MODEL"] = "sentence-transformers/all-MiniLM-L6-v2"
    os.environ["DESTINATION__LANCEDB__EMBEDDING_MODEL_PROVIDER"] = "sentence-transformers"

    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="lancedb",
        dataset_name=table_name,
        progress="log",
    )

    return pipeline, lancedb_adapter
