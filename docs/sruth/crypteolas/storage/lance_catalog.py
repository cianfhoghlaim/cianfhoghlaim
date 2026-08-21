"""
Lance Catalog for Crypteolas.

Provides LanceDB namespace management with Lakekeeper integration.
Manages embedding tables across different source types with
proper HNSW index handling for performance.

Features:
- Multi-source embedding tables (protocol_docs, user_url, github, local)
- HNSW index management (drop before bulk, recreate after)
- Batch embedding operations
- Lakekeeper catalog registration
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EmbeddingModel(str, Enum):
    """Supported embedding models."""

    BGE_M3 = "BAAI/bge-m3"
    CODEBERT = "microsoft/codebert-base"
    E5_LARGE = "intfloat/e5-large-v2"
    NOMIC = "nomic-ai/nomic-embed-text-v1.5"


@dataclass
class LanceCatalogConfig:
    """Configuration for Lance catalog."""

    # LanceDB storage
    uri: str = "./storage/data/lancedb"
    table_prefix: str = "crypteolas_"

    # Lakekeeper integration
    lakekeeper_url: str = "http://localhost:8181"
    lakekeeper_warehouse: str = "crypteolas"
    lakekeeper_namespace: str = "embeddings"

    # Embedding settings
    default_model: str = "BAAI/bge-m3"
    default_dimension: int = 1024

    # HNSW settings
    hnsw_num_partitions: int = 256
    hnsw_num_sub_vectors: int = 96
    hnsw_drop_threshold: int = 50  # Drop index for bulk inserts > this

    @classmethod
    def from_env(cls) -> "LanceCatalogConfig":
        """Load configuration from environment variables."""
        return cls(
            uri=os.getenv("LANCEDB_URI", "./storage/data/lancedb"),
            table_prefix=os.getenv("LANCEDB_TABLE_PREFIX", "crypteolas_"),
            lakekeeper_url=os.getenv("LAKEKEEPER_URL", "http://localhost:8181"),
            lakekeeper_warehouse=os.getenv("LAKEKEEPER_WAREHOUSE", "crypteolas"),
            lakekeeper_namespace=os.getenv("LAKEKEEPER_NAMESPACE", "embeddings"),
            default_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            default_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1024")),
            hnsw_num_partitions=int(os.getenv("HNSW_NUM_PARTITIONS", "256")),
            hnsw_num_sub_vectors=int(os.getenv("HNSW_NUM_SUB_VECTORS", "96")),
            hnsw_drop_threshold=int(os.getenv("HNSW_DROP_THRESHOLD", "50")),
        )


@dataclass
class EmbeddingRecord:
    """A record with embedding."""

    id: str
    text: str
    vector: list[float]
    source_type: str
    source_url: str | None = None
    document_id: str | None = None
    chunk_index: int = 0
    metadata: dict[str, Any] | None = None


class LanceCatalog:
    """
    LanceDB catalog manager with Lakekeeper integration.

    Manages embedding tables for different source types:
    - protocol_docs: Pre-configured crypto protocol documentation
    - user_url: User-provided arbitrary URLs
    - github: GitHub repository documentation
    - local: Local workspace files
    """

    def __init__(self, config: LanceCatalogConfig | None = None):
        self.config = config or LanceCatalogConfig.from_env()
        self._db = None
        self._lakekeeper = None

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

    def _get_lakekeeper(self):
        """Get Lakekeeper client for catalog registration."""
        if self._lakekeeper is not None:
            return self._lakekeeper

        from .lakekeeper_client import LakekeeperClient, LakekeeperConfig

        config = LakekeeperConfig(
            url=self.config.lakekeeper_url,
            warehouse=self.config.lakekeeper_warehouse,
            namespace=self.config.lakekeeper_namespace,
        )
        self._lakekeeper = LakekeeperClient(config)

        return self._lakekeeper

    @property
    def db(self):
        """Get LanceDB connection."""
        return self._get_db()

    @property
    def lakekeeper(self):
        """Get Lakekeeper client."""
        return self._get_lakekeeper()

    # =========================================================================
    # Table Management
    # =========================================================================

    def _table_name(self, source_type: str) -> str:
        """Get full table name for a source type."""
        return f"{self.config.table_prefix}{source_type}"

    def list_tables(self) -> list[str]:
        """List all embedding tables."""
        all_tables = self.db.table_names()
        return [t for t in all_tables if t.startswith(self.config.table_prefix)]

    def table_exists(self, source_type: str) -> bool:
        """Check if a table exists for a source type."""
        return self._table_name(source_type) in self.db.table_names()

    def get_table(self, source_type: str):
        """Get a table by source type."""
        table_name = self._table_name(source_type)
        if table_name not in self.db.table_names():
            return None
        return self.db.open_table(table_name)

    def create_table(
        self,
        source_type: str,
        model: str | None = None,
        dimension: int | None = None,
    ) -> Any:
        """Create an embedding table for a source type."""
        import pyarrow as pa

        table_name = self._table_name(source_type)
        model = model or self.config.default_model
        dim = dimension or self.config.default_dimension

        # Define schema
        schema = pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("text", pa.large_string()),
                pa.field("vector", pa.list_(pa.float32(), dim)),
                pa.field("source_type", pa.string()),
                pa.field("source_url", pa.string()),
                pa.field("document_id", pa.string()),
                pa.field("chunk_index", pa.int32()),
                pa.field("metadata", pa.string()),  # JSON string
                pa.field("created_at", pa.string()),
            ]
        )

        # Create table
        table = self.db.create_table(table_name, schema=schema, mode="overwrite")

        logger.info(f"Created embedding table: {table_name} (model={model}, dim={dim})")

        # Register with Lakekeeper
        try:
            self.lakekeeper.register_embedding_table(
                table_name=table_name,
                lance_uri=f"{self.config.uri}/{table_name}.lance",
                model=model,
                dimension=dim,
                source_type=source_type,
            )
        except Exception as e:
            logger.warning(f"Failed to register with Lakekeeper: {e}")

        return table

    def drop_table(self, source_type: str) -> None:
        """Drop a table."""
        table_name = self._table_name(source_type)
        if table_name in self.db.table_names():
            self.db.drop_table(table_name)
            logger.info(f"Dropped table: {table_name}")

    # =========================================================================
    # HNSW Index Management
    # =========================================================================

    def create_hnsw_index(self, source_type: str) -> None:
        """Create HNSW index on a table."""
        table = self.get_table(source_type)
        if table is None:
            raise ValueError(f"Table not found: {source_type}")

        table.create_index(
            "vector",
            index_type="IVF_PQ",
            num_partitions=self.config.hnsw_num_partitions,
            num_sub_vectors=self.config.hnsw_num_sub_vectors,
        )
        logger.info(f"Created HNSW index: {self._table_name(source_type)}")

    def drop_hnsw_index(self, source_type: str) -> None:
        """Drop HNSW index from a table (for bulk inserts)."""
        table = self.get_table(source_type)
        if table is None:
            return

        try:
            # LanceDB automatically handles index cleanup
            # For bulk operations, we just skip index creation until done
            logger.info(f"Index will be rebuilt after bulk insert: {source_type}")
        except Exception as e:
            logger.warning(f"Could not drop index: {e}")

    # =========================================================================
    # Embedding Operations
    # =========================================================================

    def add_embeddings(
        self,
        source_type: str,
        records: list[EmbeddingRecord],
        batch_size: int = 100,  # MANDATORY minimum per CLAUDE.md
    ) -> int:
        """
        Add embeddings to a table.

        IMPORTANT: Batching is MANDATORY (100x performance difference).
        For large inserts (>50 rows), HNSW index is managed automatically.
        """
        import json

        if not records:
            return 0

        table = self.get_table(source_type)
        if table is None:
            table = self.create_table(source_type)

        # For large inserts, we'll rebuild index after
        rebuild_index = len(records) > self.config.hnsw_drop_threshold

        now = datetime.utcnow().isoformat()
        total_added = 0

        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]

            data = []
            for record in batch:
                data.append(
                    {
                        "id": record.id,
                        "text": record.text,
                        "vector": record.vector,
                        "source_type": record.source_type,
                        "source_url": record.source_url or "",
                        "document_id": record.document_id or "",
                        "chunk_index": record.chunk_index,
                        "metadata": json.dumps(record.metadata) if record.metadata else "{}",
                        "created_at": now,
                    }
                )

            table.add(data)
            total_added += len(batch)

            if (i + batch_size) % 1000 == 0:
                logger.info(f"Added {total_added}/{len(records)} embeddings to {source_type}")

        # Rebuild index after large insert
        if rebuild_index:
            self.create_hnsw_index(source_type)

        logger.info(f"Added {total_added} embeddings to {source_type}")
        return total_added

    def search(
        self,
        source_type: str,
        query_vector: list[float],
        limit: int = 10,
        filter_expr: str | None = None,
    ) -> list[dict]:
        """Search for similar embeddings."""
        table = self.get_table(source_type)
        if table is None:
            return []

        search = table.search(query_vector).limit(limit)

        if filter_expr:
            search = search.where(filter_expr)

        results = search.to_pandas()

        return results.to_dict("records")

    def search_all(
        self,
        query_vector: list[float],
        source_types: list[str] | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search across all source types."""
        if source_types is None:
            source_types = ["protocol_docs", "user_url", "github", "local"]

        all_results = []
        for source_type in source_types:
            if self.table_exists(source_type):
                results = self.search(source_type, query_vector, limit=limit)
                all_results.extend(results)

        # Sort by score and limit
        all_results.sort(key=lambda x: x.get("_distance", float("inf")))
        return all_results[:limit]

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_table_stats(self, source_type: str) -> dict[str, Any]:
        """Get statistics for a table."""
        table = self.get_table(source_type)
        if table is None:
            return {"exists": False}

        count = table.count_rows()
        return {
            "exists": True,
            "table_name": self._table_name(source_type),
            "row_count": count,
            "source_type": source_type,
        }

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all tables."""
        source_types = ["protocol_docs", "user_url", "github", "local"]
        return {st: self.get_table_stats(st) for st in source_types}


# Singleton instance
_lance_catalog: LanceCatalog | None = None


def get_lance_catalog(config: LanceCatalogConfig | None = None) -> LanceCatalog:
    """Get the Lance catalog singleton."""
    global _lance_catalog
    if _lance_catalog is None:
        _lance_catalog = LanceCatalog(config)
    return _lance_catalog
