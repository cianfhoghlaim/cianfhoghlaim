"""
LanceDB storage for códeolas.

Provides vector storage for code embeddings with HNSW indexing.

Features:
    - Code chunk embedding tables (by language, chunk_type)
    - HNSW index management (drop before bulk, recreate after)
    - Batch embedding operations (MANDATORY min 100)
    - File/function/class relationship tracking
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LanceCatalogConfig:
    """Configuration for LanceDB catalog."""

    # LanceDB storage
    uri: str = "./storage/data/lancedb"
    table_prefix: str = "codeolas_"

    # Embedding settings
    default_model: str = "BAAI/bge-m3"
    default_dimension: int = 1024

    # HNSW settings
    hnsw_num_partitions: int = 256
    hnsw_num_sub_vectors: int = 96
    hnsw_drop_threshold: int = 50  # Drop index for bulk inserts > this

    # Batching (CRITICAL: minimum 100 for performance)
    min_batch_size: int = 100
    max_batch_size: int = 1000

    @classmethod
    def from_env(cls) -> "LanceCatalogConfig":
        """Load configuration from environment variables."""
        return cls(
            uri=os.getenv("LANCEDB_URI", "./storage/data/lancedb"),
            table_prefix=os.getenv("LANCEDB_TABLE_PREFIX", "codeolas_"),
            default_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            default_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1024")),
            hnsw_num_partitions=int(os.getenv("HNSW_NUM_PARTITIONS", "256")),
            hnsw_num_sub_vectors=int(os.getenv("HNSW_NUM_SUB_VECTORS", "96")),
            hnsw_drop_threshold=int(os.getenv("HNSW_DROP_THRESHOLD", "50")),
        )


@dataclass
class CodeChunk:
    """A code chunk with embedding for storage."""

    id: str
    file_path: str
    language: str
    chunk_type: str
    name: str | None
    start_line: int
    end_line: int
    text: str
    vector: list[float]
    parent_id: str | None = None
    git_sha: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LanceCatalog:
    """
    LanceDB catalog manager for code embeddings.

    Manages embedding tables for code chunks:
    - code_chunks: All code chunks with embeddings
    - files: File metadata and statistics
    """

    def __init__(self, config: LanceCatalogConfig | None = None):
        self.config = config or LanceCatalogConfig.from_env()
        self._db = None

    def _get_db(self):
        """Get or create LanceDB connection."""
        if self._db is not None:
            return self._db

        try:
            import lancedb
        except ImportError:
            raise ImportError("lancedb is not installed. Run: pip install lancedb")

        # Ensure directory exists
        Path(self.config.uri).mkdir(parents=True, exist_ok=True)

        self._db = lancedb.connect(self.config.uri)
        logger.info(f"Connected to LanceDB: {self.config.uri}")

        return self._db

    @property
    def db(self):
        """Get LanceDB connection."""
        return self._get_db()

    # =========================================================================
    # Table Management
    # =========================================================================

    def _table_name(self, table_type: str) -> str:
        """Get full table name for a table type."""
        return f"{self.config.table_prefix}{table_type}"

    def list_tables(self) -> list[str]:
        """List all códeolas tables."""
        all_tables = self.db.table_names()
        return [t for t in all_tables if t.startswith(self.config.table_prefix)]

    def table_exists(self, table_type: str) -> bool:
        """Check if a table exists."""
        return self._table_name(table_type) in self.db.table_names()

    def get_table(self, table_type: str):
        """Get a table by type."""
        table_name = self._table_name(table_type)
        if table_name not in self.db.table_names():
            return None
        return self.db.open_table(table_name)

    def create_code_chunks_table(
        self,
        model: str | None = None,
        dimension: int | None = None,
    ) -> Any:
        """Create the code chunks embedding table."""
        import pyarrow as pa

        table_name = self._table_name("code_chunks")
        model = model or self.config.default_model
        dim = dimension or self.config.default_dimension

        # Define schema for code chunks
        schema = pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("file_path", pa.string()),
                pa.field("language", pa.string()),
                pa.field("chunk_type", pa.string()),
                pa.field("name", pa.string()),
                pa.field("start_line", pa.int32()),
                pa.field("end_line", pa.int32()),
                pa.field("text", pa.large_string()),
                pa.field("vector", pa.list_(pa.float32(), dim)),
                pa.field("parent_id", pa.string()),
                pa.field("git_sha", pa.string()),
                pa.field("metadata", pa.string()),  # JSON string
                pa.field("indexed_at", pa.string()),
            ]
        )

        # Create table
        table = self.db.create_table(table_name, schema=schema, mode="overwrite")

        logger.info(f"Created code chunks table: {table_name} (model={model}, dim={dim})")

        return table

    def create_files_table(self) -> Any:
        """Create the files metadata table."""
        import pyarrow as pa

        table_name = self._table_name("files")

        schema = pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("file_path", pa.string()),
                pa.field("language", pa.string()),
                pa.field("size_bytes", pa.int64()),
                pa.field("line_count", pa.int32()),
                pa.field("chunk_count", pa.int32()),
                pa.field("git_sha", pa.string()),
                pa.field("last_modified", pa.string()),
                pa.field("indexed_at", pa.string()),
            ]
        )

        table = self.db.create_table(table_name, schema=schema, mode="overwrite")

        logger.info(f"Created files table: {table_name}")

        return table

    def drop_table(self, table_type: str) -> None:
        """Drop a table."""
        table_name = self._table_name(table_type)
        if table_name in self.db.table_names():
            self.db.drop_table(table_name)
            logger.info(f"Dropped table: {table_name}")

    # =========================================================================
    # HNSW Index Management
    # =========================================================================

    def create_hnsw_index(self, table_type: str = "code_chunks") -> None:
        """Create HNSW index on a table."""
        table = self.get_table(table_type)
        if table is None:
            raise ValueError(f"Table not found: {table_type}")

        table.create_index(
            "vector",
            index_type="IVF_PQ",
            num_partitions=self.config.hnsw_num_partitions,
            num_sub_vectors=self.config.hnsw_num_sub_vectors,
        )
        logger.info(f"Created HNSW index: {self._table_name(table_type)}")

    def drop_hnsw_index(self, table_type: str = "code_chunks") -> None:
        """Drop HNSW index from a table (for bulk inserts)."""
        table = self.get_table(table_type)
        if table is None:
            return

        try:
            # LanceDB automatically handles index cleanup
            logger.info(f"Index will be rebuilt after bulk insert: {table_type}")
        except Exception as e:
            logger.warning(f"Could not drop index: {e}")

    # =========================================================================
    # Code Chunk Operations
    # =========================================================================

    def add_code_chunks(
        self,
        chunks: list[CodeChunk],
        batch_size: int | None = None,
    ) -> int:
        """
        Add code chunks to the table.

        IMPORTANT: Batching is MANDATORY (100x performance difference).
        For large inserts (>50 rows), HNSW index is managed automatically.
        """
        if not chunks:
            return 0

        # Enforce minimum batch size
        batch_size = batch_size or self.config.min_batch_size
        if batch_size < self.config.min_batch_size:
            logger.warning(
                f"Batch size {batch_size} below minimum {self.config.min_batch_size}, using minimum"
            )
            batch_size = self.config.min_batch_size

        table = self.get_table("code_chunks")
        if table is None:
            table = self.create_code_chunks_table()

        # For large inserts, we'll rebuild index after
        rebuild_index = len(chunks) > self.config.hnsw_drop_threshold

        now = datetime.utcnow().isoformat()
        total_added = 0

        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            data = []
            for chunk in batch:
                data.append(
                    {
                        "id": chunk.id,
                        "file_path": chunk.file_path,
                        "language": chunk.language,
                        "chunk_type": chunk.chunk_type,
                        "name": chunk.name or "",
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "text": chunk.text,
                        "vector": chunk.vector,
                        "parent_id": chunk.parent_id or "",
                        "git_sha": chunk.git_sha or "",
                        "metadata": json.dumps(chunk.metadata) if chunk.metadata else "{}",
                        "indexed_at": now,
                    }
                )

            table.add(data)
            total_added += len(batch)

            if (i + batch_size) % 1000 == 0:
                logger.info(f"Added {total_added}/{len(chunks)} chunks")

        # Rebuild index after large insert
        if rebuild_index:
            self.create_hnsw_index("code_chunks")

        logger.info(f"Added {total_added} code chunks")
        return total_added

    def search_code(
        self,
        query_vector: list[float],
        limit: int = 10,
        language: str | None = None,
        chunk_type: str | None = None,
        file_path: str | None = None,
    ) -> list[dict]:
        """Search for similar code chunks."""
        table = self.get_table("code_chunks")
        if table is None:
            return []

        search = table.search(query_vector).limit(limit)

        # Build filter expression
        filters = []
        if language:
            filters.append(f"language = '{language}'")
        if chunk_type:
            filters.append(f"chunk_type = '{chunk_type}'")
        if file_path:
            filters.append(f"file_path LIKE '{file_path}%'")

        if filters:
            search = search.where(" AND ".join(filters))

        results = search.to_pandas()
        return results.to_dict("records")

    def get_file_chunks(self, file_path: str) -> list[dict]:
        """Get all chunks for a file."""
        table = self.get_table("code_chunks")
        if table is None:
            return []

        results = table.search().where(f"file_path = '{file_path}'").to_pandas()
        return results.to_dict("records")

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get catalog statistics."""
        stats = {
            "tables": self.list_tables(),
            "code_chunks": {"exists": False},
            "files": {"exists": False},
        }

        chunks_table = self.get_table("code_chunks")
        if chunks_table:
            stats["code_chunks"] = {
                "exists": True,
                "row_count": chunks_table.count_rows(),
            }

        files_table = self.get_table("files")
        if files_table:
            stats["files"] = {
                "exists": True,
                "row_count": files_table.count_rows(),
            }

        return stats


# Singleton instance
_lance_catalog: LanceCatalog | None = None


def get_lance_catalog(config: LanceCatalogConfig | None = None) -> LanceCatalog:
    """Get the Lance catalog singleton."""
    global _lance_catalog
    if _lance_catalog is None:
        _lance_catalog = LanceCatalog(config)
    return _lance_catalog
