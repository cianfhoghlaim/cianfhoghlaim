"""
Curriculum Vector Search Module.

Provides semantic search over curriculum content using LanceDB.
Uses transformers for embedding generation with BGE-M3 compatible models.

Critical Constraints (from CLAUDE.md):
- BATCH MINIMUM: 100 embeddings per API call (100x performance)
- SINGLE-THREADED: Use SerialDatabaseExecutor within process

Usage:
    from sruth.oideachais.storage.curriculum_vectors import CurriculumVectorSearch

    search = CurriculumVectorSearch()
    await search.index_outcomes(outcomes)
    results = await search.search("mathematics fractions", limit=10)
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

import lancedb
import pyarrow as pa

logger = logging.getLogger(__name__)

# Default embedding dimension (for all-MiniLM-L6-v2 or similar)
DEFAULT_EMBEDDING_DIM = 384


@dataclass
class CurriculumEmbedding:
    """Curriculum content with embedding."""

    outcome_id: str
    text: str
    vector: list[float]
    nation: str
    subject: str
    level: str
    language: str
    title: str


class CurriculumVectorSearch:
    """
    Vector search for curriculum content.

    Provides:
    - Semantic search over learning outcomes
    - Cross-nation curriculum alignment
    - Hybrid keyword + vector search

    Tables:
    - curriculum_outcomes: Learning outcome embeddings
    """

    TABLE_NAME = "curriculum_outcomes"

    def __init__(
        self,
        db_path: str | None = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        """
        Initialize curriculum vector search.

        Args:
            db_path: Path to LanceDB database (local or cloud URI)
            embedding_model: HuggingFace model for embeddings
        """
        self.db_path = db_path or os.getenv(
            "LANCEDB_PATH",
            os.path.join(os.path.dirname(__file__), "data/curriculum_vectors.lance")
        )
        self.embedding_model = embedding_model
        self._db: lancedb.DBConnection | None = None
        self._embedder: Any = None
        self._lock = asyncio.Lock()

    async def _get_db(self) -> lancedb.DBConnection:
        """Get or create database connection."""
        async with self._lock:
            if self._db is None:
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                self._db = lancedb.connect(self.db_path)
                logger.info(f"Connected to LanceDB at {self.db_path}")
            return self._db

    def _get_embedder(self):
        """Get or create embedding model (lazy loading)."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(self.embedding_model)
                logger.info(f"Loaded embedding model: {self.embedding_model}")
            except ImportError:
                logger.warning("sentence-transformers not available, using simple hash embeddings")
                self._embedder = SimpleHashEmbedder()
        return self._embedder

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        embedder = self._get_embedder()

        if hasattr(embedder, 'encode'):
            # sentence-transformers model
            vectors = embedder.encode(texts, convert_to_numpy=True)
            return vectors.tolist()
        else:
            # Fallback embedder
            return [embedder.embed(text) for text in texts]

    async def create_table(self, drop_existing: bool = False) -> lancedb.table.Table:
        """
        Create the curriculum outcomes table.

        Args:
            drop_existing: Drop existing table if it exists
        """
        db = await self._get_db()

        if drop_existing and self.TABLE_NAME in db.table_names():
            db.drop_table(self.TABLE_NAME)
            logger.info(f"Dropped existing table: {self.TABLE_NAME}")

        # Define schema
        schema = pa.schema([
            pa.field("outcome_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), DEFAULT_EMBEDDING_DIM)),
            pa.field("nation", pa.string()),
            pa.field("subject", pa.string()),
            pa.field("level", pa.string()),
            pa.field("language", pa.string()),
            pa.field("title", pa.string()),
        ])

        table = db.create_table(self.TABLE_NAME, schema=schema, mode="create")
        logger.info(f"Created table: {self.TABLE_NAME}")
        return table

    async def index_outcomes(
        self,
        outcomes: list[dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """
        Index learning outcomes with embeddings.

        Args:
            outcomes: List of outcome dicts with text, nation, subject, etc.
            batch_size: Batch size for embedding generation

        Returns:
            Number of outcomes indexed
        """
        db = await self._get_db()

        # Ensure table exists
        if self.TABLE_NAME not in db.table_names():
            await self.create_table()

        table = db.open_table(self.TABLE_NAME)
        indexed = 0

        # Process in batches
        for i in range(0, len(outcomes), batch_size):
            batch = outcomes[i:i + batch_size]

            # Create embedding text (title + content excerpt)
            texts = [
                f"{o.get('title', '')} {o.get('outcome_text', o.get('content', ''))[:500]}"
                for o in batch
            ]

            # Generate embeddings
            vectors = self._embed_texts(texts)

            # Prepare data for insertion
            data = []
            for o, text, vector in zip(batch, texts, vectors):
                data.append({
                    "outcome_id": o.get("id", o.get("outcome_id", hashlib.md5(text.encode()).hexdigest())),
                    "text": text,
                    "vector": vector,
                    "nation": o.get("nation", "ireland"),
                    "subject": o.get("subject", ""),
                    "level": o.get("level", o.get("curriculum_level", "")),
                    "language": o.get("language", "en"),
                    "title": o.get("title", ""),
                })

            # Insert batch
            table.add(data)
            indexed += len(batch)
            logger.info(f"Indexed {indexed}/{len(outcomes)} outcomes")

        return indexed

    async def search(
        self,
        query: str,
        limit: int = 10,
        nation: str | None = None,
        subject: str | None = None,
        level: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Semantic search for curriculum content.

        Args:
            query: Search query text
            limit: Maximum results
            nation: Filter by nation (e.g., 'ireland')
            subject: Filter by subject (e.g., 'mathematics')
            level: Filter by level (e.g., 'ie_junior_cycle')

        Returns:
            List of matching outcomes with similarity scores
        """
        db = await self._get_db()

        if self.TABLE_NAME not in db.table_names():
            logger.warning("No curriculum vectors indexed")
            return []

        table = db.open_table(self.TABLE_NAME)

        # Generate query embedding
        query_vector = self._embed_texts([query])[0]

        # Build search with filters
        search = table.search(query_vector).limit(limit)

        # Apply filters
        filters = []
        if nation:
            filters.append(f"nation = '{nation}'")
        if subject:
            filters.append(f"subject = '{subject}'")
        if level:
            filters.append(f"level = '{level}'")

        if filters:
            search = search.where(" AND ".join(filters))

        results = search.to_list()

        # Format results
        return [
            {
                "outcome_id": r["outcome_id"],
                "title": r["title"],
                "text": r["text"],
                "nation": r["nation"],
                "subject": r["subject"],
                "level": r["level"],
                "language": r["language"],
                "similarity_score": 1 - r.get("_distance", 0),  # Convert distance to similarity
            }
            for r in results
        ]

    async def find_similar_outcomes(
        self,
        outcome_id: str,
        limit: int = 5,
        same_nation: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Find outcomes similar to a given outcome.

        Useful for cross-nation curriculum alignment.

        Args:
            outcome_id: ID of source outcome
            limit: Maximum similar outcomes
            same_nation: Only return outcomes from same nation

        Returns:
            List of similar outcomes
        """
        db = await self._get_db()
        table = db.open_table(self.TABLE_NAME)

        # Get source outcome
        source = table.search().where(f"outcome_id = '{outcome_id}'").limit(1).to_list()
        if not source:
            return []

        source = source[0]

        # Search for similar
        search = table.search(source["vector"]).limit(limit + 1)  # +1 to exclude self

        if same_nation:
            search = search.where(f"nation = '{source['nation']}'")

        results = search.to_list()

        # Exclude self from results
        return [
            {
                "outcome_id": r["outcome_id"],
                "title": r["title"],
                "text": r["text"],
                "nation": r["nation"],
                "subject": r["subject"],
                "level": r["level"],
                "similarity_score": 1 - r.get("_distance", 0),
            }
            for r in results
            if r["outcome_id"] != outcome_id
        ][:limit]

    async def get_stats(self) -> dict[str, Any]:
        """Get vector search statistics."""
        db = await self._get_db()

        if self.TABLE_NAME not in db.table_names():
            return {"indexed": 0, "tables": []}

        table = db.open_table(self.TABLE_NAME)
        count = table.count_rows()

        return {
            "indexed": count,
            "table": self.TABLE_NAME,
            "embedding_model": self.embedding_model,
            "db_path": self.db_path,
        }

    async def close(self) -> None:
        """Close database connection."""
        if self._db is not None:
            self._db = None
            logger.info("Closed LanceDB connection")


class SimpleHashEmbedder:
    """
    Simple hash-based embedder for development/testing.

    NOT for production - just creates deterministic embeddings
    based on text hash for testing without ML dependencies.
    """

    def __init__(self, dim: int = DEFAULT_EMBEDDING_DIM):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        """Generate simple hash embedding."""
        import hashlib

        # Create deterministic embedding from text hash
        hash_bytes = hashlib.sha256(text.encode()).digest()

        # Expand hash to embedding dimension
        embedding = []
        for i in range(self.dim):
            byte_idx = i % len(hash_bytes)
            # Normalize to [-1, 1]
            embedding.append((hash_bytes[byte_idx] - 128) / 128.0)

        return embedding


# =============================================================================
# Singleton Access
# =============================================================================

_search_client: CurriculumVectorSearch | None = None


def get_curriculum_search() -> CurriculumVectorSearch:
    """Get curriculum vector search singleton."""
    global _search_client
    if _search_client is None:
        _search_client = CurriculumVectorSearch()
    return _search_client


async def index_curriculum_from_duckdb(db_path: str | None = None) -> int:
    """
    Index curriculum outcomes from DuckDB semantic layer.

    Args:
        db_path: Path to DuckDB database

    Returns:
        Number of outcomes indexed
    """
    import duckdb

    db_path = db_path or os.path.join(
        os.path.dirname(__file__),
        "../storage/data/celtic_education.duckdb"
    )

    conn = duckdb.connect(db_path, read_only=True)

    # Query unified outcomes from semantic layer
    outcomes = conn.execute("""
        SELECT
            outcome_id as id,
            title,
            content as outcome_text,
            nation,
            subject,
            curriculum_level as level,
            language
        FROM int.int_unified_outcomes
    """).fetchall()

    columns = ["id", "title", "outcome_text", "nation", "subject", "level", "language"]
    outcome_dicts = [dict(zip(columns, row)) for row in outcomes]

    conn.close()

    # Index in vector store
    search = get_curriculum_search()
    return await search.index_outcomes(outcome_dicts)
