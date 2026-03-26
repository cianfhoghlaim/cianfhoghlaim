"""
LanceDB Cloud Client for Celtic Education Pipeline.

Direct connection to LanceDB Cloud ($100 credits) for production vector search.
Provides managed HNSW indexing, automatic compaction, and cloud-native scaling.

Key differences from local/Iceberg integration:
- No self-managed infrastructure
- Automatic HNSW index management
- Built-in replication and backups
- Pay-per-query pricing after credits

Usage:
    from sruth.oideachais.storage.lancedb_cloud import LanceDBCloudClient

    client = LanceDBCloudClient()
    await client.create_table("duchas_embeddings", schema)
    await client.add_embeddings("duchas_embeddings", embeddings, batch_size=100)

Critical Constraints (from CLAUDE.md):
- BATCH MINIMUM: 100 embeddings per API call (100x performance)
- HNSW INDEX: Managed automatically by cloud (no manual DROP/RECREATE)
- SINGLE-THREADED: Use SerialDatabaseExecutor within process
"""

import asyncio
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

import lancedb
import pyarrow as pa
import structlog

# Import resilience utilities from shared infrastructure
from sruth.shared.utils import CircuitBreaker, CircuitBreakerOpen, retry_with_backoff

from .serial_executor import SerialDatabaseExecutor

logger = structlog.get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# LanceDB Configuration and Client
# =============================================================================


class LanceDBEnvironment(str, Enum):
    """LanceDB deployment environment."""

    LOCAL = "local"  # Local file-based (development)
    CLOUD = "cloud"  # LanceDB Cloud ($100 credits)
    ICEBERG = "iceberg"  # Via Iceberg REST catalog (self-hosted)


@dataclass
class LanceDBCloudConfig:
    """LanceDB Cloud configuration."""

    # Cloud connection
    uri: str = field(
        default_factory=lambda: os.getenv(
            "LANCEDB_URI",
            "db://cianfhoghlaim",
        )
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("LANCEDB_API_KEY", "")
    )
    region: str = field(
        default_factory=lambda: os.getenv("LANCEDB_REGION", "eu-west-1")
    )

    # Local fallback
    local_path: str = field(
        default_factory=lambda: os.getenv(
            "LANCEDB_LOCAL_PATH",
            "/tmp/lancedb",
        )
    )

    # Performance settings
    batch_size: int = 100  # MINIMUM for acceptable performance
    max_batch_size: int = 10000  # Provider limit

    def is_cloud_configured(self) -> bool:
        """Check if cloud credentials are configured."""
        return bool(self.api_key and self.uri.startswith("db://"))


@dataclass
class EmbeddingBatch:
    """Batch of embeddings for bulk insert."""

    vectors: list[list[float]]
    metadata: list[dict[str, Any]]
    ids: list[str]

    def __len__(self) -> int:
        return len(self.vectors)

    def to_arrow(self, vector_column: str = "vector") -> pa.Table:
        """Convert to PyArrow table for LanceDB ingestion."""
        return pa.table(
            {
                "id": self.ids,
                vector_column: self.vectors,
                "metadata": [str(m) for m in self.metadata],
            }
        )


class LanceDBCloudClient:
    """
    LanceDB Cloud client for production vector search.

    Provides:
    - Direct cloud connection with managed infrastructure
    - Automatic HNSW index management
    - Batch-optimized embedding operations
    - Single-threaded execution via SerialDatabaseExecutor

    Tables (organized by pipeline):
    - duchas_pages: Dúchas.ie handwriting page embeddings
    - duchas_transcriptions: OCR/HTR transcription embeddings
    - sec_papers: SEC exam paper embeddings
    - sec_marking_schemes: Marking scheme embeddings
    - canuint_audio: Canúint.ie audio segment embeddings
    - curriculum_ireland: Irish curriculum embeddings
    """

    # Standard tables for ML pipeline
    PIPELINE_TABLES = {
        "duchas_pages": "Dúchas.ie handwriting page embeddings",
        "duchas_transcriptions": "OCR/HTR transcription embeddings",
        "sec_papers": "SEC exam paper embeddings",
        "sec_marking_schemes": "Marking scheme embeddings",
        "canuint_audio": "Canúint.ie audio segment embeddings",
        "curriculum_ireland": "Irish curriculum content embeddings",
        "curriculum_bilingual": "Bilingual alignment embeddings",
    }

    def __init__(
        self,
        config: LanceDBCloudConfig | None = None,
        environment: LanceDBEnvironment | None = None,
        circuit_breaker: CircuitBreaker | None = None,
    ):
        self.config = config or LanceDBCloudConfig()
        self.environment = environment or self._detect_environment()
        self._db: lancedb.DBConnection | None = None
        self._executor = SerialDatabaseExecutor()
        self._lock = asyncio.Lock()

        # Circuit breaker for resilience
        self._circuit_breaker = circuit_breaker or CircuitBreaker(
            failure_threshold=3,
            recovery_time=60,
        )
        self._service_name = "lancedb"

    def _detect_environment(self) -> LanceDBEnvironment:
        """Detect environment based on configuration."""
        if self.config.is_cloud_configured():
            return LanceDBEnvironment.CLOUD
        return LanceDBEnvironment.LOCAL

    async def _run_with_resilience(
        self,
        func: Callable[[], T],
        operation: str,
        max_retries: int = 3,
        retryable: tuple[type[Exception], ...] = (OSError, ConnectionError, TimeoutError),
    ) -> T:
        """
        Execute operation with circuit breaker and retry logic.

        Args:
            func: Synchronous function to execute
            operation: Operation name for logging
            max_retries: Maximum retry attempts
            retryable: Exception types that trigger retry

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: If all retries exhausted
        """
        # Check circuit breaker first
        if self._circuit_breaker.is_open(self._service_name):
            retry_after = self._circuit_breaker.time_until_recovery(self._service_name)
            logger.warning(
                "lancedb_circuit_open",
                operation=operation,
                retry_after=retry_after,
            )
            raise CircuitBreakerOpen(self._service_name, retry_after)

        try:
            # Execute with retry logic
            result = await retry_with_backoff(
                func,
                max_attempts=max_retries,
                retryable_exceptions=retryable,
            )
            # Record success
            self._circuit_breaker.record_success(self._service_name)
            return result
        except retryable as e:
            # Record failure after all retries exhausted
            self._circuit_breaker.record_failure(self._service_name)
            logger.error(
                "lancedb_operation_failed",
                operation=operation,
                error=str(e),
                circuit_state=self._circuit_breaker.get_state(self._service_name),
            )
            raise

    async def _get_db(self) -> lancedb.DBConnection:
        """Get or create database connection (single-threaded)."""
        async with self._lock:
            if self._db is None:
                self._db = await self._run_with_resilience(
                    self._connect,
                    operation="connect",
                )
            return self._db

    def _connect(self) -> lancedb.DBConnection:
        """Establish database connection."""
        if self.environment == LanceDBEnvironment.CLOUD:
            logger.info("lancedb_connecting", environment="cloud", uri=self.config.uri)
            return lancedb.connect(
                self.config.uri,
                api_key=self.config.api_key,
                region=self.config.region,
            )
        else:
            logger.info("lancedb_connecting", environment="local", path=self.config.local_path)
            return lancedb.connect(self.config.local_path)

    # =========================================================================
    # Table Operations
    # =========================================================================

    async def create_table(
        self,
        name: str,
        schema: pa.Schema | None = None,
        mode: str = "create",
    ) -> lancedb.table.Table:
        """
        Create a new table.

        Args:
            name: Table name
            schema: PyArrow schema (optional, can be inferred from first insert)
            mode: 'create' (error if exists), 'overwrite', or 'append'

        Returns:
            LanceDB table handle
        """
        db = await self._get_db()

        def _create():
            if schema:
                return db.create_table(name, schema=schema, mode=mode)
            # Create empty table that accepts any data
            return db.create_table(name, mode=mode)

        table = await self._executor.run(_create)
        logger.info("lancedb_table_created", table_name=name)
        return table

    async def get_table(self, name: str) -> lancedb.table.Table:
        """Get an existing table."""
        db = await self._get_db()

        def _open() -> lancedb.table.Table:
            return db.open_table(name)

        return await self._run_with_resilience(
            _open,
            operation=f"get_table:{name}",
        )

    async def list_tables(self) -> list[str]:
        """List all tables in the database."""
        db = await self._get_db()

        def _list():
            return db.table_names()

        return await self._executor.run(_list)

    async def drop_table(self, name: str) -> None:
        """Drop a table."""
        db = await self._get_db()

        def _drop():
            db.drop_table(name)

        await self._executor.run(_drop)
        logger.info("lancedb_table_dropped", table_name=name)

    # =========================================================================
    # Embedding Operations (Batch-Optimized)
    # =========================================================================

    async def add_embeddings(
        self,
        table_name: str,
        batch: EmbeddingBatch,
        create_if_missing: bool = True,
    ) -> int:
        """
        Add embeddings to a table in batch.

        CRITICAL: Minimum batch size is 100 for acceptable performance.

        Args:
            table_name: Target table name
            batch: EmbeddingBatch with vectors, metadata, and IDs
            create_if_missing: Create table if it doesn't exist

        Returns:
            Number of embeddings added

        Raises:
            ValueError: If batch size < 100 (performance warning)
        """
        if len(batch) < self.config.batch_size:
            logger.warning(
                "lancedb_batch_size_warning",
                batch_size=len(batch),
                minimum=self.config.batch_size,
                message="Performance will be significantly degraded",
            )

        db = await self._get_db()
        arrow_table = batch.to_arrow()

        def _add() -> int:
            try:
                table = db.open_table(table_name)
                table.add(arrow_table)
            except (FileNotFoundError, ValueError) as e:
                # Table doesn't exist - FileNotFoundError for local, ValueError for cloud
                if create_if_missing:
                    logger.info("lancedb_creating_table", table_name=table_name, reason=str(e))
                    db.create_table(table_name, arrow_table)
                else:
                    raise
            return len(batch)

        count = await self._run_with_resilience(
            _add,
            operation=f"add_embeddings:{table_name}",
            retryable=(OSError, ConnectionError, TimeoutError),
        )
        logger.info("lancedb_embeddings_added", count=count, table_name=table_name)
        return count

    async def add_embeddings_bulk(
        self,
        table_name: str,
        vectors: list[list[float]],
        metadata: list[dict[str, Any]],
        ids: list[str],
    ) -> int:
        """
        Bulk add embeddings with automatic batching.

        Splits large inserts into optimal batch sizes.

        Args:
            table_name: Target table name
            vectors: List of embedding vectors
            metadata: List of metadata dicts
            ids: List of unique IDs

        Returns:
            Total embeddings added
        """
        total = len(vectors)
        if total == 0:
            return 0

        added = 0
        batch_size = min(self.config.max_batch_size, max(self.config.batch_size, 100))

        for i in range(0, total, batch_size):
            end = min(i + batch_size, total)
            batch = EmbeddingBatch(
                vectors=vectors[i:end],
                metadata=metadata[i:end],
                ids=ids[i:end],
            )
            added += await self.add_embeddings(table_name, batch)

        logger.info("lancedb_bulk_embeddings_added", count=added, table_name=table_name)
        return added

    # =========================================================================
    # Search Operations
    # =========================================================================

    async def search(
        self,
        table_name: str,
        query_vector: list[float],
        limit: int = 10,
        filter_sql: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Vector similarity search.

        Args:
            table_name: Table to search
            query_vector: Query embedding vector
            limit: Maximum results to return
            filter_sql: Optional SQL filter expression

        Returns:
            List of matching records with distances
        """
        table = await self.get_table(table_name)

        def _search() -> list[dict[str, Any]]:
            search = table.search(query_vector).limit(limit)
            if filter_sql:
                search = search.where(filter_sql)
            return search.to_list()

        results = await self._run_with_resilience(
            _search,
            operation=f"search:{table_name}",
        )
        return results

    async def hybrid_search(
        self,
        table_name: str,
        query_vector: list[float],
        query_text: str,
        limit: int = 10,
        reranker: str = "rrf",
    ) -> list[dict[str, Any]]:
        """
        Hybrid vector + full-text search.

        Args:
            table_name: Table to search
            query_vector: Query embedding vector
            query_text: Query text for FTS
            limit: Maximum results
            reranker: Reranking strategy ('rrf', 'linear', 'cohere')

        Returns:
            Reranked search results
        """
        table = await self.get_table(table_name)

        def _hybrid() -> list[dict[str, Any]]:
            return (
                table.search(query_vector, query_type="hybrid")
                .text(query_text)
                .limit(limit)
                .rerank(reranker=reranker)
                .to_list()
            )

        return await self._run_with_resilience(
            _hybrid,
            operation=f"hybrid_search:{table_name}",
        )

    # =========================================================================
    # Index Management (Cloud handles automatically, but expose controls)
    # =========================================================================

    async def create_index(
        self,
        table_name: str,
        column: str = "vector",
        index_type: str = "IVF_PQ",
        num_partitions: int = 256,
        num_sub_vectors: int = 96,
    ) -> None:
        """
        Create vector index on a table.

        Note: LanceDB Cloud manages indexes automatically.
        This is mainly for local development.

        Args:
            table_name: Table to index
            column: Vector column name
            index_type: Index type (IVF_PQ, IVF_HNSW_SQ, etc.)
            num_partitions: Number of IVF partitions
            num_sub_vectors: Number of PQ sub-vectors
        """
        table = await self.get_table(table_name)

        def _create_index():
            table.create_index(
                column,
                index_type=index_type,
                num_partitions=num_partitions,
                num_sub_vectors=num_sub_vectors,
            )

        await self._executor.run(_create_index)
        logger.info("lancedb_index_created", index_type=index_type, table_name=table_name, column=column)

    # =========================================================================
    # Pipeline Helpers
    # =========================================================================

    async def init_pipeline_tables(self) -> dict[str, bool]:
        """
        Initialize all ML pipeline tables.

        Returns:
            Dict of table names and whether they were created
        """
        existing = set(await self.list_tables())
        results = {}

        for name, description in self.PIPELINE_TABLES.items():
            if name in existing:
                results[name] = False
                logger.info("lancedb_table_exists", table_name=name)
            else:
                await self.create_table(name)
                results[name] = True
                logger.info("lancedb_pipeline_table_created", table_name=name, description=description)

        return results

    async def get_table_stats(self, table_name: str) -> dict[str, Any]:
        """Get statistics for a table."""
        table = await self.get_table(table_name)

        def _stats():
            return {
                "name": table_name,
                "row_count": table.count_rows(),
                "schema": str(table.schema),
            }

        return await self._executor.run(_stats)

    async def close(self) -> None:
        """Close database connection."""
        if self._db is not None:
            self._db = None
            logger.info("lancedb_connection_closed")

    def get_circuit_breaker_status(self) -> dict[str, Any]:
        """
        Get circuit breaker status for observability.

        Returns:
            Dict with state, failures, and recovery time
        """
        return {
            "service": self._service_name,
            "state": self._circuit_breaker.get_state(self._service_name),
            "failures": self._circuit_breaker._failures.get(self._service_name, 0),
            "is_open": self._circuit_breaker.is_open(self._service_name),
            "time_until_recovery": self._circuit_breaker.time_until_recovery(self._service_name),
        }

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker to closed state (for testing/recovery)."""
        self._circuit_breaker._failures[self._service_name] = 0
        if self._service_name in self._circuit_breaker._open_until:
            del self._circuit_breaker._open_until[self._service_name]
        if self._service_name in self._circuit_breaker._half_open_calls:
            del self._circuit_breaker._half_open_calls[self._service_name]
        logger.info("circuit_breaker_reset", service=self._service_name)


# =============================================================================
# Convenience Functions
# =============================================================================

_client: LanceDBCloudClient | None = None


def get_lancedb_client() -> LanceDBCloudClient:
    """Get the LanceDB Cloud client singleton."""
    global _client
    if _client is None:
        _client = LanceDBCloudClient()
    return _client


async def add_duchas_embeddings(
    vectors: list[list[float]],
    metadata: list[dict[str, Any]],
    page_ids: list[str],
) -> int:
    """
    Add Dúchas.ie page embeddings.

    Convenience wrapper for the ML pipeline.
    """
    client = get_lancedb_client()
    return await client.add_embeddings_bulk(
        "duchas_pages",
        vectors,
        metadata,
        page_ids,
    )


async def add_sec_embeddings(
    vectors: list[list[float]],
    metadata: list[dict[str, Any]],
    doc_ids: list[str],
    table: str = "sec_papers",
) -> int:
    """
    Add SEC exam paper embeddings.

    Convenience wrapper for the ML pipeline.
    """
    client = get_lancedb_client()
    return await client.add_embeddings_bulk(
        table,
        vectors,
        metadata,
        doc_ids,
    )


async def search_curriculum(
    query_vector: list[float],
    nation: str = "ireland",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search curriculum embeddings.

    Args:
        query_vector: Query embedding
        nation: 'ireland' or 'bilingual'
        limit: Max results

    Returns:
        Matching curriculum content
    """
    client = get_lancedb_client()
    table = f"curriculum_{nation}"
    return await client.search(table, query_vector, limit=limit)
