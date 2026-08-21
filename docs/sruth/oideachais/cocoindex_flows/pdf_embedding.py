"""
PDF Embedding Flow.

Creates vector embeddings for curriculum PDF documents with MANDATORY batching.

Embedding Pipeline:
    Source (DuckDB pdf_extracted_text) → Chunk → Embed (batched) → LanceDB (with HNSW management)

CRITICAL CONSTRAINTS (from CLAUDE.md):
    - Embedding batching: MANDATORY minimum 100 per call (100x performance difference)
    - HNSW indexes: DROP before bulk inserts >50 rows, recreate after
    - DuckDB: Single-threaded only via SerialDatabaseProvider

Output Table:
    - Namespace: oideachas.curriculum_pdfs
    - Schema: document_id, chunk_index, text, vector, cycle, subject, language, etc.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# Import from curriculum_embedding for shared components
from .curriculum_embedding import (
    TextChunker,
    EmbeddingEngine,
    LanceDBEmbeddingSink,
    MIN_EMBEDDING_BATCH_SIZE,
    HNSW_DROP_THRESHOLD,
)

# LanceDB imports
try:
    import lancedb
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

# DuckDB imports
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class PDFEmbeddingConfig:
    """Configuration for PDF embedding flow."""

    # Source (DuckDB table with extracted PDF text)
    source_table: str = "pdf_extracted_text"
    duckdb_path: str = "./.dlt/curriculum_unified/curriculum.duckdb"

    # Embedding
    model_name: str = "BAAI/bge-m3"  # Best for multilingual/Irish
    embedding_dim: int = 1024
    batch_size: int = 100  # MANDATORY: minimum 100

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 100
    min_chunk_length: int = 50

    # Output (LanceDB)
    lancedb_path: str = "./storage/data/lancedb"
    output_table: str = "oideachas.curriculum_pdfs"  # Namespaced

    # Index
    metric_type: str = "cosine"

    # Filter (optional)
    cycles: list[str] = field(default_factory=lambda: [
        "junior_cycle", "senior_cycle", "primary", "early_childhood"
    ])


# =============================================================================
# PDF Text Source
# =============================================================================

def read_pdf_extracted_text(
    duckdb_path: str,
    table_name: str = "pdf_extracted_text",
    limit: int | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Read extracted PDF text from DuckDB.

    Uses single-threaded read_only connection for safety.

    Yields:
        Dict with document_id, text, cycle, subject, language, etc.
    """
    if not DUCKDB_AVAILABLE:
        logger.error("duckdb_not_available")
        return

    try:
        # Single-threaded read-only connection
        conn = duckdb.connect(duckdb_path, read_only=True)

        query = f"""
            SELECT
                document_id,
                local_path,
                cycle,
                subject,
                text,
                confidence,
                model_id,
                backend,
                page_count,
                extracted_at
            FROM {table_name}
            WHERE text IS NOT NULL AND length(text) > 0
        """

        if limit:
            query += f" LIMIT {limit}"

        result = conn.execute(query).fetchall()
        columns = [
            "document_id", "local_path", "cycle", "subject",
            "text", "confidence", "model_id", "backend",
            "page_count", "extracted_at"
        ]

        for row in result:
            yield dict(zip(columns, row))

        conn.close()

    except Exception as e:
        logger.error("pdf_source_error", error=str(e))
        return


# =============================================================================
# PDF Embedding Pipeline
# =============================================================================

class PDFEmbeddingPipeline:
    """
    Pipeline for embedding PDF documents.

    Follows CRITICAL CONSTRAINTS:
    - Batch minimum 100 embeddings
    - Drop HNSW before bulk insert >50 rows
    """

    def __init__(self, config: PDFEmbeddingConfig | None = None):
        self.config = config or PDFEmbeddingConfig()
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            min_chunk_length=self.config.min_chunk_length,
        )
        self.engine = EmbeddingEngine(model_name=self.config.model_name)
        self.sink = None

    def _init_sink(self):
        """Initialize LanceDB sink."""
        if self.sink is None and LANCEDB_AVAILABLE:
            self.sink = LanceDBEmbeddingSink(
                db_path=self.config.lancedb_path,
                table_name=self.config.output_table,
                metric_type=self.config.metric_type,
            )

    def process_documents(
        self,
        documents: Iterator[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Process PDF documents end-to-end.

        Steps:
        1. Read from DuckDB (or use provided documents)
        2. Chunk each document
        3. Batch embed chunks (minimum 100)
        4. Insert into LanceDB with HNSW management

        Returns:
            Stats dict with counts
        """
        if documents is None:
            documents = read_pdf_extracted_text(
                duckdb_path=self.config.duckdb_path,
                table_name=self.config.source_table,
            )

        self._init_sink()

        stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
            "errors": 0,
            "elapsed_seconds": 0,
        }

        start_time = time.time()

        # Collect all chunks for batching
        all_chunks: list[dict[str, Any]] = []

        for doc in documents:
            try:
                # Chunk the document text
                doc_chunks = self.chunker.split(doc.get("text", ""))

                for chunk in doc_chunks:
                    all_chunks.append({
                        "id": f"{doc['document_id']}_{chunk['chunk_index']}",
                        "document_id": doc["document_id"],
                        "local_path": doc.get("local_path", ""),
                        "cycle": doc.get("cycle", "unknown"),
                        "subject": doc.get("subject", "unknown"),
                        "chunk_index": chunk["chunk_index"],
                        "text": chunk["text"],
                        "start_char": chunk["start_char"],
                        "end_char": chunk["end_char"],
                        "ocr_confidence": doc.get("confidence", 0.0),
                        "ocr_backend": doc.get("backend", "unknown"),
                        "page_count": doc.get("page_count", 1),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    })

                stats["documents_processed"] += 1
                stats["chunks_created"] += len(doc_chunks)

            except Exception as e:
                logger.warning("document_processing_error", doc_id=doc.get("document_id"), error=str(e))
                stats["errors"] += 1

        logger.info(
            "chunking_complete",
            documents=stats["documents_processed"],
            chunks=stats["chunks_created"],
        )

        # Batch embed all chunks
        if all_chunks:
            texts = [c["text"] for c in all_chunks]

            # Ensure batch size meets minimum
            batch_size = max(MIN_EMBEDDING_BATCH_SIZE, len(texts))

            embeddings = self.engine.embed_batch(texts, batch_size=batch_size)

            # Add embeddings to chunks
            for i, chunk in enumerate(all_chunks):
                chunk["vector"] = embeddings[i].tolist()

            stats["embeddings_created"] = len(embeddings)

            # Insert into LanceDB with HNSW management
            if self.sink and len(all_chunks) > 0:
                rows_inserted = self.sink.insert_with_index_management(all_chunks)
                logger.info("lancedb_insert_complete", rows=rows_inserted)

        stats["elapsed_seconds"] = round(time.time() - start_time, 2)

        logger.info(
            "pdf_embedding_pipeline_complete",
            **stats,
        )

        return stats


# =============================================================================
# Standalone Runner
# =============================================================================

def run_pdf_embedding(
    config: PDFEmbeddingConfig | None = None,
) -> dict[str, Any]:
    """
    Run the PDF embedding pipeline.

    Usage:
        from cocoindex_flows.pdf_embedding import run_pdf_embedding

        stats = run_pdf_embedding()
        print(f"Processed {stats['documents_processed']} documents")
    """
    pipeline = PDFEmbeddingPipeline(config)
    return pipeline.process_documents()


# =============================================================================
# LanceDB Schema for PDF Embeddings
# =============================================================================

PDF_EMBEDDING_SCHEMA = pa.schema([
    ("id", pa.string()),
    ("document_id", pa.string()),
    ("local_path", pa.string()),
    ("cycle", pa.string()),
    ("subject", pa.string()),
    ("chunk_index", pa.int32()),
    ("text", pa.string()),
    ("start_char", pa.int32()),
    ("end_char", pa.int32()),
    ("vector", pa.list_(pa.float32(), 1024)),  # BGE-M3 dimension
    ("ocr_confidence", pa.float64()),
    ("ocr_backend", pa.string()),
    ("page_count", pa.int32()),
    ("created_at", pa.string()),
]) if LANCEDB_AVAILABLE else None


__all__ = [
    "PDFEmbeddingConfig",
    "PDFEmbeddingPipeline",
    "run_pdf_embedding",
    "read_pdf_extracted_text",
    "PDF_EMBEDDING_SCHEMA",
]
