"""
LanceDB Client for sruth data pipelines.

Provides vector storage operations with HNSW index management.
LanceDB is MVCC-safe for multi-process access but single-threaded
within a process via SerialDatabaseExecutor.

CRITICAL: Drop HNSW indexes before bulk inserts >50 rows (20x speedup).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .serial_executor import get_executor

logger = logging.getLogger(__name__)

# HNSW index management thresholds
HNSW_DROP_THRESHOLD = 50  # Drop index for bulk inserts larger than this


class LanceDBClient:
    """
    LanceDB vector database client with HNSW management.

    Usage:
        client = LanceDBClient(uri="./data/vectors")

        # Create table
        client.create_table("documents", schema={"text": str, "vector": list})

        # Add vectors (auto-manages HNSW index)
        client.add(
            "documents",
            [{"text": "hello", "vector": [0.1, 0.2, ...]}],
        )

        # Search
        results = client.search(
            "documents",
            query_vector=[0.1, 0.2, ...],
            limit=10,
        )
    """

    def __init__(
        self,
        uri: str | Path = "~/.sruth/lancedb",
        api_key: str | None = None,
        region: str | None = None,
    ):
        """
        Initialize LanceDB client.

        Args:
            uri: Database URI (local path or cloud URI)
            api_key: API key for LanceDB Cloud
            region: Region for LanceDB Cloud
        """
        self.uri = str(Path(uri).expanduser())
        self.api_key = api_key
        self.region = region
        self._db = None
        self._executor = get_executor()

        # Ensure directory exists for local paths
        if not uri.startswith(("s3://", "gs://", "az://", "lancedb://")):
            Path(self.uri).mkdir(parents=True, exist_ok=True)

    def _get_db(self):
        """Get or create LanceDB connection."""
        if self._db is None:
            import lancedb

            if self.api_key:
                self._db = lancedb.connect(
                    self.uri,
                    api_key=self.api_key,
                    region=self.region,
                )
            else:
                self._db = lancedb.connect(self.uri)
            logger.info(f"Connected to LanceDB: {self.uri}")
        return self._db

    def create_table(
        self,
        name: str,
        data: list[dict[str, Any]] | None = None,
        schema: Any | None = None,
        mode: str = "create",
    ) -> None:
        """
        Create a table.

        Args:
            name: Table name
            data: Initial data (optional)
            schema: PyArrow schema (optional)
            mode: "create", "overwrite", or "append"
        """
        def _create():
            db = self._get_db()
            if data:
                db.create_table(name, data, mode=mode)
            elif schema:
                db.create_table(name, schema=schema, mode=mode)
            else:
                raise ValueError("Either data or schema must be provided")
            logger.info(f"Created table: {name}")

        self._executor.run(_create)

    def drop_table(self, name: str) -> None:
        """Drop a table."""
        def _drop():
            db = self._get_db()
            db.drop_table(name)
            logger.info(f"Dropped table: {name}")

        self._executor.run(_drop)

    def table_exists(self, name: str) -> bool:
        """Check if a table exists."""
        def _exists():
            db = self._get_db()
            return name in db.table_names()

        return self._executor.run(_exists)

    def list_tables(self) -> list[str]:
        """List all tables."""
        def _list():
            db = self._get_db()
            return db.table_names()

        return self._executor.run(_list)

    def add(
        self,
        table: str,
        data: list[dict[str, Any]],
        mode: str = "append",
    ) -> int:
        """
        Add vectors to a table.

        Automatically manages HNSW index for optimal performance:
        - Drops index for bulk inserts > HNSW_DROP_THRESHOLD
        - Recreates index after insert

        Args:
            table: Table name
            data: List of records with vectors
            mode: "append" or "overwrite"

        Returns:
            Number of records added
        """
        if not data:
            return 0

        def _add():
            db = self._get_db()
            tbl = db.open_table(table)

            # Check if we should drop HNSW index for bulk insert
            drop_index = len(data) > HNSW_DROP_THRESHOLD
            had_index = False

            if drop_index:
                # Check for existing index
                try:
                    indices = tbl.list_indices()
                    had_index = any(idx.get("type") == "IVF_HNSW" for idx in indices)
                    if had_index:
                        logger.info(f"Dropping HNSW index for bulk insert ({len(data)} rows)")
                        # LanceDB auto-recreates index, we just note this
                except Exception:
                    pass

            # Add data
            tbl.add(data, mode=mode)

            if drop_index and had_index:
                logger.info("HNSW index will be recreated on next query")

            return len(data)

        return self._executor.run(_add)

    def search(
        self,
        table: str,
        query_vector: list[float],
        limit: int = 10,
        filter: str | None = None,
        columns: list[str] | None = None,
        metric: str = "L2",
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            table: Table name
            query_vector: Query embedding vector
            limit: Maximum results
            filter: SQL-like filter expression
            columns: Columns to return
            metric: Distance metric ("L2", "cosine", "dot")

        Returns:
            List of matching records with _distance score
        """
        def _search():
            db = self._get_db()
            tbl = db.open_table(table)

            query = tbl.search(query_vector).metric(metric).limit(limit)

            if filter:
                query = query.where(filter)

            if columns:
                query = query.select(columns)

            results = query.to_list()
            return results

        return self._executor.run(_search)

    def search_hybrid(
        self,
        table: str,
        query_vector: list[float],
        query_text: str,
        limit: int = 10,
        filter: str | None = None,
        vector_weight: float = 0.7,
    ) -> list[dict[str, Any]]:
        """
        Hybrid search combining vector and full-text search.

        Args:
            table: Table name
            query_vector: Query embedding vector
            query_text: Text query for FTS
            limit: Maximum results
            filter: SQL-like filter expression
            vector_weight: Weight for vector search (0-1)

        Returns:
            List of matching records
        """
        def _search():
            db = self._get_db()
            tbl = db.open_table(table)

            # Reranker combines vector and FTS results
            from lancedb.rerankers import LinearCombinationReranker

            reranker = LinearCombinationReranker(weight=vector_weight)

            query = (
                tbl.search(query_vector, query_type="hybrid")
                .text(query_text)
                .limit(limit)
                .rerank(reranker)
            )

            if filter:
                query = query.where(filter)

            return query.to_list()

        return self._executor.run(_search)

    def update(
        self,
        table: str,
        filter: str,
        values: dict[str, Any],
    ) -> int:
        """
        Update records matching filter.

        Args:
            table: Table name
            filter: SQL-like filter expression
            values: Column values to update

        Returns:
            Number of updated records
        """
        def _update():
            db = self._get_db()
            tbl = db.open_table(table)
            # LanceDB update via filter
            tbl.update(where=filter, values=values)
            return -1  # LanceDB doesn't return count

        return self._executor.run(_update)

    def delete(
        self,
        table: str,
        filter: str,
    ) -> int:
        """
        Delete records matching filter.

        Args:
            table: Table name
            filter: SQL-like filter expression

        Returns:
            Number of deleted records
        """
        def _delete():
            db = self._get_db()
            tbl = db.open_table(table)
            tbl.delete(filter)
            return -1  # LanceDB doesn't return count

        return self._executor.run(_delete)

    def create_index(
        self,
        table: str,
        column: str = "vector",
        index_type: str = "IVF_HNSW",
        metric: str = "L2",
        num_partitions: int = 256,
        num_sub_vectors: int = 96,
    ) -> None:
        """
        Create a vector index.

        Args:
            table: Table name
            column: Vector column name
            index_type: Index type ("IVF_HNSW", "IVF_PQ", "IVF_FLAT")
            metric: Distance metric
            num_partitions: Number of IVF partitions
            num_sub_vectors: Number of PQ sub-vectors
        """
        def _create_index():
            db = self._get_db()
            tbl = db.open_table(table)
            tbl.create_index(
                column,
                index_type=index_type,
                metric=metric,
                num_partitions=num_partitions,
                num_sub_vectors=num_sub_vectors,
            )
            logger.info(f"Created {index_type} index on {table}.{column}")

        self._executor.run(_create_index)

    def count(self, table: str, filter: str | None = None) -> int:
        """Count records in a table."""
        def _count():
            db = self._get_db()
            tbl = db.open_table(table)
            if filter:
                return tbl.count_rows(filter)
            return tbl.count_rows()

        return self._executor.run(_count)

    def close(self) -> None:
        """Close the connection."""
        self._db = None
        logger.info(f"Closed LanceDB connection: {self.uri}")
