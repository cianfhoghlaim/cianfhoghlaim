"""
Curriculum Embedding Flow.

Creates vector embeddings for Celtic curriculum content with MANDATORY batching.

Embedding Pipeline:
    Source (DuckDB) → Chunk → Embed (batched) → LanceDB (with HNSW index management)

CRITICAL CONSTRAINTS (from CLAUDE.md):
    - Embedding batching: MANDATORY minimum 100 per call (100x performance difference)
    - HNSW indexes: DROP before bulk inserts >50 rows, recreate after
    - DuckDB: Single-threaded only via SerialDatabaseProvider

Models:
    - multilingual-e5-large: Best for Celtic languages (1024d)
    - paraphrase-multilingual-MiniLM-L12-v2: Faster, smaller (384d)
    - ColPali: Document layout understanding (multimodal)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# CocoIndex imports (when available)
try:
    import cocoindex
    from cocoindex import DuckDBSource, LanceDBSink, Transform
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False

# LanceDB imports
try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

# MANDATORY: Minimum batch size for embeddings (100x performance difference)
MIN_EMBEDDING_BATCH_SIZE = 100

# MANDATORY: Drop HNSW index before bulk inserts >50 rows
HNSW_DROP_THRESHOLD = 50


@dataclass
class EmbeddingConfig:
    """Configuration for curriculum embedding flow."""

    # Source
    source_table: str = "education.curriculum_pages"
    duckdb_path: str = "./storage/data/celtic_education.duckdb"

    # Embedding
    model_name: str = "sentence-transformers/multilingual-e5-large"
    embedding_dim: int = 1024
    batch_size: int = 100  # MANDATORY: minimum 100

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 100
    min_chunk_length: int = 50

    # Output
    lancedb_path: str = "./storage/data/lancedb"
    output_table: str = "celtic_curriculum_embeddings"

    # Index
    index_type: str = "IVF_HNSW"
    metric_type: str = "cosine"

    # Filter by nation (optional)
    nations: list[str] = field(default_factory=lambda: [
        "ireland", "scotland", "wales", "england", "northern_ireland"
    ])

    # Celtic languages
    languages: list[str] = field(default_factory=lambda: [
        "en", "ga", "gd", "cy", "gv", "kw", "br"
    ])


# =============================================================================
# Chunking
# =============================================================================

class TextChunker:
    """Recursive text chunker for curriculum documents."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        min_chunk_length: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length

        # Separators in order of preference
        self.separators = [
            "\n\n\n",   # Triple newline (section break)
            "\n\n",     # Double newline (paragraph)
            "\n",       # Single newline
            ". ",       # Sentence
            ", ",       # Clause
            " ",        # Word
            "",         # Character (fallback)
        ]

    def split(self, text: str) -> list[dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Returns list of {text, start_char, end_char, chunk_index}
        """
        if not text or len(text) < self.min_chunk_length:
            return []

        chunks = self._recursive_split(text, self.separators)

        return [
            {
                "text": chunk,
                "start_char": text.find(chunk),
                "end_char": text.find(chunk) + len(chunk),
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
            if len(chunk) >= self.min_chunk_length
        ]

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using separators."""
        if not separators:
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator not in text or separator == "":
            if len(text) <= self.chunk_size:
                return [text]
            return self._recursive_split(text, remaining_separators)

        splits = text.split(separator)
        chunks = []
        current_chunk = ""

        for split in splits:
            potential_chunk = current_chunk + separator + split if current_chunk else split

            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                if len(split) > self.chunk_size:
                    sub_chunks = self._recursive_split(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


# =============================================================================
# Embedding Engine
# =============================================================================

class EmbeddingEngine:
    """
    Embedding engine with MANDATORY batching.

    CRITICAL: Batch minimum 100 embeddings per call for performance.
    Unbatched: ~100s for 1000 texts
    Batched:   ~1s for 1000 texts (100x faster)
    """

    def __init__(self, model_name: str = "sentence-transformers/multilingual-e5-large"):
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> Any:
        """Lazy-load embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info("embedding_model_loaded", model=self.model_name)
        return self._model

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = MIN_EMBEDDING_BATCH_SIZE,
    ) -> np.ndarray:
        """
        Embed texts in batches.

        MANDATORY: batch_size >= 100 for performance.

        Args:
            texts: List of texts to embed
            batch_size: Batch size (minimum 100)

        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        if batch_size < MIN_EMBEDDING_BATCH_SIZE:
            logger.warning(
                "embedding_batch_size_below_minimum",
                requested=batch_size,
                minimum=MIN_EMBEDDING_BATCH_SIZE,
            )
            batch_size = MIN_EMBEDDING_BATCH_SIZE

        model = self._load_model()

        start_time = time.time()
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            normalize_embeddings=True,  # For cosine similarity
        )
        elapsed = time.time() - start_time

        logger.info(
            "embedding_complete",
            count=len(texts),
            elapsed_s=round(elapsed, 2),
            throughput=round(len(texts) / elapsed, 1) if elapsed > 0 else 0,
        )

        return embeddings


# =============================================================================
# LanceDB Sink with HNSW Management
# =============================================================================

class LanceDBEmbeddingSink:
    """
    LanceDB sink with HNSW index management.

    MANDATORY: Drop HNSW index before bulk inserts >50 rows for 20x speedup.
    """

    def __init__(
        self,
        db_path: str,
        table_name: str,
        metric_type: str = "cosine",
    ):
        self.db_path = db_path
        self.table_name = table_name
        self.metric_type = metric_type
        self._db = None
        self._table = None

    def _connect(self) -> Any:
        """Connect to LanceDB."""
        if self._db is None:
            self._db = lancedb.connect(self.db_path)
        return self._db

    def _get_or_create_table(self, schema: dict[str, Any] | Any | None = None) -> Any:
        """Get or create table."""
        db = self._connect()

        if self.table_name in db.table_names():
            self._table = db.open_table(self.table_name)
        elif schema:
            # If schema is a PyArrow schema, use schema kwarg, else use data logic
            import pyarrow as pa
            if isinstance(schema, pa.Schema):
                self._table = db.create_table(self.table_name, schema=schema)
            else:
                self._table = db.create_table(self.table_name, data=[schema])
        else:
            raise ValueError(f"Table {self.table_name} does not exist and no schema provided")

        return self._table

    def insert_with_index_management(
        self,
        data: list[dict[str, Any]],
        schema: Any = None,
    ) -> int:
        """
        Insert data with HNSW index management.

        MANDATORY: For >50 rows, drops HNSW index before insert, recreates after.
        """
        table = self._get_or_create_table(schema if schema else data[0])
        need_index_management = len(data) > HNSW_DROP_THRESHOLD

        # Drop index before bulk insert
        if need_index_management:
            try:
                table.drop_index("vector_idx")
                logger.info("hnsw_index_dropped", row_count=len(data))
            except (ValueError, RuntimeError, OSError):
                pass  # Index might not exist

        # Insert data
        start_time = time.time()
        table.add(data)
        insert_time = time.time() - start_time

        logger.info("lancedb_insert_complete", row_count=len(data), elapsed_s=round(insert_time, 2))

        # Recreate index after bulk insert
        if need_index_management:
            start_time = time.time()
            table.create_index(
                "vector_idx",
                index_type="IVF_HNSW",
                metric=self.metric_type,
                num_partitions=256,
                num_sub_vectors=32,
            )
            index_time = time.time() - start_time
            logger.info("hnsw_index_recreated", elapsed_s=round(index_time, 2))

        return len(data)


# =============================================================================
# Embedding Flow
# =============================================================================

class CurriculumEmbeddingFlow:
    """
    Curriculum embedding flow with observability integration.

    Flow:
        1. Read curriculum from DuckDB (single-threaded)
        2. Chunk documents
        3. Embed in batches (min 100)
        4. Store in LanceDB (with HNSW management)
    """

    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            min_chunk_length=self.config.min_chunk_length,
        )
        self.embedder = EmbeddingEngine(self.config.model_name)
        self.sink = LanceDBEmbeddingSink(
            db_path=self.config.lancedb_path,
            table_name=self.config.output_table,
            metric_type=self.config.metric_type,
        )

    def read_documents(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Read documents from DuckDB.

        CONSTRAINT: Single-threaded access only.
        """
        import duckdb

        # Single-threaded connection
        conn = duckdb.connect(self.config.duckdb_path, read_only=True)

        try:
            query = f"""
                SELECT
                    id,
                    page_url,
                    title,
                    content,
                    language,
                    nation,
                    subject,
                    level,
                    source
                FROM {self.config.source_table}
                WHERE content IS NOT NULL
                  AND LENGTH(content) > {self.config.min_chunk_length}
                LIMIT {limit}
            """
            rows = conn.execute(query).fetchall()
            columns = ["id", "page_url", "title", "content", "language", "nation", "subject", "level", "source"]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def process_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Process documents: chunk and embed.

        Returns list of records ready for LanceDB.
        """
        # Chunk all documents
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.split(doc.get("content", ""))
            for chunk in chunks:
                all_chunks.append({
                    "doc_id": doc.get("id"),
                    "page_url": doc.get("page_url"),
                    "title": doc.get("title"),
                    "language": doc.get("language", "en"),
                    "nation": doc.get("nation"),
                    "subject": doc.get("subject"),
                    "level": doc.get("level"),
                    "source": doc.get("source"),
                    "text": chunk["text"],
                    "chunk_index": chunk["chunk_index"],
                    "start_char": chunk["start_char"],
                    "end_char": chunk["end_char"],
                })

        if not all_chunks:
            return []

        # Embed in batches (MANDATORY: min 100)
        texts = [c["text"] for c in all_chunks]
        embeddings = self.embedder.embed_batch(
            texts,
            batch_size=self.config.batch_size,
        )

        # Combine chunks with embeddings
        records = []
        for i, chunk in enumerate(all_chunks):
            chunk["vector"] = embeddings[i].tolist()
            records.append(chunk)

        return records

    def run(self, limit: int = 100) -> dict[str, Any]:
        """
        Run the embedding flow.

        Args:
            limit: Maximum documents to process

        Returns:
            Stats dict with documents, chunks, and timing
        """
        # Import observability if available
        try:
            from cianfhoghlaim.observability import log_agent_metrics, mlflow_run
            has_observability = True
        except ImportError:
            has_observability = False

        start_time = time.time()

        # Read documents (single-threaded)
        documents = self.read_documents(limit)
        read_time = time.time() - start_time

        if not documents:
            return {
                "documents": 0,
                "chunks": 0,
                "total_time_s": read_time,
            }

        # Process (chunk + embed)
        process_start = time.time()
        records = self.process_documents(documents)
        process_time = time.time() - process_start

        if not records:
            return {
                "documents": len(documents),
                "chunks": 0,
                "total_time_s": time.time() - start_time,
            }

        # Store in LanceDB (with HNSW management)
        store_start = time.time()
        inserted = self.sink.insert_with_index_management(records)
        store_time = time.time() - store_start

        total_time = time.time() - start_time

        stats = {
            "documents": len(documents),
            "chunks": len(records),
            "inserted": inserted,
            "read_time_s": read_time,
            "process_time_s": process_time,
            "store_time_s": store_time,
            "total_time_s": total_time,
            "throughput_chunks_per_s": len(records) / total_time if total_time > 0 else 0,
        }

        # Log to MLflow if available
        if has_observability:
            try:
                with mlflow_run("curriculum_embedding"):
                    log_agent_metrics(
                        agent_name="embedding_flow",
                        query=f"embed_{len(documents)}_docs",
                        response_length=len(records),
                        latency_ms=total_time * 1000,
                        token_count=sum(len(r["text"]) for r in records),
                    )
            except (ImportError, RuntimeError) as e:
                logger.warning("mlflow_logging_failed", error=str(e))

        return stats


# =============================================================================
# CocoIndex Flow Definition
# =============================================================================

def create_embedding_flow(config: EmbeddingConfig | None = None) -> Any:
    """
    Create CocoIndex flow for curriculum embedding.

    Flow:
        DuckDB → Chunk → Embed (batched) → LanceDB (HNSW managed)
    """
    if not COCOINDEX_AVAILABLE:
        raise ImportError("cocoindex not available - install with: pip install cocoindex")

    config = config or EmbeddingConfig()
    chunker = TextChunker(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    embedder = EmbeddingEngine(config.model_name)

    @cocoindex.flow(name="celtic_curriculum_embedding")
    def curriculum_embedding_flow():
        # Source: Read curriculum pages
        source = DuckDBSource(
            database=config.duckdb_path,
            query=f"""
                SELECT id, page_url, title, content, language, nation, subject, level
                FROM {config.source_table}
                WHERE content IS NOT NULL AND LENGTH(content) > 50
            """,
        )

        # Transform: Chunk documents
        chunked = source.transform(
            Transform(
                name="chunk_documents",
                fn=lambda rows: [
                    {**row, "chunks": chunker.split(row["content"])}
                    for row in rows
                ],
                batch_size=10,
            )
        )

        # Transform: Flatten chunks
        flattened = chunked.transform(
            Transform(
                name="flatten_chunks",
                fn=lambda rows: [
                    {
                        "doc_id": row["id"],
                        "page_url": row["page_url"],
                        "title": row["title"],
                        "language": row["language"],
                        "text": chunk["text"],
                        "chunk_index": chunk["chunk_index"],
                    }
                    for row in rows
                    for chunk in row.get("chunks", [])
                ],
            )
        )

        # Sink: LanceDB with embeddings
        flattened.sink(
            LanceDBSink(
                database=config.lancedb_path,
                table=config.output_table,
                embedding_column="text",
                embedding_model=config.model_name,
                # MANDATORY: Batch embeddings
                batch_size=config.batch_size,
            )
        )

    return curriculum_embedding_flow


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run curriculum embedding flow")
    parser.add_argument("--database", default="./storage/data/celtic_education.duckdb")
    parser.add_argument("--lancedb", default="./storage/data/lancedb")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()

    config = EmbeddingConfig(
        duckdb_path=args.database,
        lancedb_path=args.lancedb,
        batch_size=args.batch_size,
    )

    flow = CurriculumEmbeddingFlow(config)
    result = flow.run(limit=args.limit)

    print(f"Processed {result['documents']} documents")
    print(f"Created {result['chunks']} chunks")
    print(f"Total time: {result['total_time_s']:.2f}s")
    print(f"Throughput: {result['throughput_chunks_per_s']:.1f} chunks/s")
