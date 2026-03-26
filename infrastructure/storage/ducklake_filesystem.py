"""
DuckLake OCR Storage with Time-Travel.

Provides OCR result storage with:
- Time-travel queries for historical comparisons
- Model performance tracking over time
- Snapshot management for reproducibility
- OCR result versioning by model and timestamp

Based on existing ducklake.py patterns for Celtic manuscript OCR.

Usage:
    from sruth.oideachais.storage.ducklake_filesystem import DuckLakeOCRStorage

    storage = DuckLakeOCRStorage()
    await storage.store_ocr_result(document_id, model_id, result)
    history = await storage.get_ocr_history(document_id, as_of="2024-01-01")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class OCRStorageConfig:
    """Configuration for OCR result storage."""

    # DuckLake connection
    duckdb_path: str = "./storage/data/celtic_education.duckdb"
    catalog_name: str = "celtic_ocr"
    schema_name: str = "ocr_results"

    # Table names
    ocr_results_table: str = "model_outputs"
    comparisons_table: str = "model_comparisons"
    documents_table: str = "processed_documents"
    snapshots_table: str = "comparison_snapshots"

    # Retention
    max_snapshots: int = 100
    retention_days: int = 365


# OCR result schema for DuckLake tables
OCR_STORAGE_SCHEMAS = {
    "model_outputs": {
        "id": "VARCHAR PRIMARY KEY",
        "document_id": "VARCHAR NOT NULL",
        "model_id": "VARCHAR NOT NULL",
        "model_name": "VARCHAR",
        "backend": "VARCHAR",  # paddleocr, docling, dots_ocr, etc.
        "text": "TEXT",
        "confidence": "DOUBLE",
        "elapsed_seconds": "DOUBLE",
        "tokens_used": "INTEGER",
        "status": "VARCHAR",
        "error_message": "TEXT",
        "metadata": "JSON",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
    "model_comparisons": {
        "id": "VARCHAR PRIMARY KEY",
        "document_id": "VARCHAR NOT NULL",
        "comparison_timestamp": "TIMESTAMP NOT NULL",
        "models_compared": "JSON",  # List of model IDs
        "best_model_id": "VARCHAR",
        "best_confidence": "DOUBLE",
        "metrics": "JSON",  # CER, WER, fada_accuracy, etc.
        "irish_content_detected": "BOOLEAN",
        "irish_quality_score": "DOUBLE",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
    "processed_documents": {
        "id": "VARCHAR PRIMARY KEY",
        "source_path": "VARCHAR NOT NULL",
        "file_hash": "VARCHAR NOT NULL",
        "file_type": "VARCHAR",
        "file_size_bytes": "BIGINT",
        "page_count": "INTEGER",
        "language_detected": "VARCHAR",
        "has_irish_content": "BOOLEAN",
        "processing_status": "VARCHAR",
        "last_processed_at": "TIMESTAMP",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
    "comparison_snapshots": {
        "id": "VARCHAR PRIMARY KEY",
        "snapshot_name": "VARCHAR NOT NULL",
        "snapshot_timestamp": "TIMESTAMP NOT NULL",
        "document_count": "INTEGER",
        "model_count": "INTEGER",
        "summary_metrics": "JSON",
        "configuration": "JSON",
        "notes": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
}


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class OCRResultRecord:
    """OCR result record for storage."""

    document_id: str
    model_id: str
    text: str
    model_name: str = ""
    backend: str = ""
    confidence: float = 0.0
    elapsed_seconds: float = 0.0
    tokens_used: int = 0
    status: str = "success"
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComparisonRecord:
    """Model comparison record."""

    document_id: str
    models_compared: list[str]
    best_model_id: str
    best_confidence: float
    metrics: dict[str, Any]
    irish_content_detected: bool = False
    irish_quality_score: float = 0.0
    id: str = field(default_factory=lambda: str(uuid4()))
    comparison_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SnapshotRecord:
    """Comparison snapshot record."""

    snapshot_name: str
    document_count: int
    model_count: int
    summary_metrics: dict[str, Any]
    configuration: dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    snapshot_timestamp: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# DuckLake OCR Storage
# =============================================================================


class DuckLakeOCRStorage:
    """
    DuckLake storage for OCR results with time-travel support.

    Provides:
    - Store OCR results with model provenance
    - Compare models across documents
    - Time-travel queries for historical analysis
    - Snapshot management for reproducibility

    CRITICAL: Uses single-threaded database access per CLAUDE.md constraints.
    """

    def __init__(self, config: OCRStorageConfig | None = None):
        self.config = config or OCRStorageConfig()
        self._connection = None

    def _get_connection(self):
        """Get or create DuckDB connection (single-threaded)."""
        if self._connection is None:
            try:
                import duckdb
                self._connection = duckdb.connect(self.config.duckdb_path)
                self._ensure_schema()
            except ImportError:
                logger.warning("duckdb not available, using mock connection")
                self._connection = MockConnection()
        return self._connection

    def _ensure_schema(self):
        """Ensure OCR storage tables exist."""
        conn = self._connection
        if conn is None:
            return

        # Create schema if not exists
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.config.schema_name}")

        # Create tables
        for table_name, schema in OCR_STORAGE_SCHEMAS.items():
            columns = ", ".join(f"{col} {dtype}" for col, dtype in schema.items())
            sql = f"""
                CREATE TABLE IF NOT EXISTS {self.config.schema_name}.{table_name} (
                    {columns}
                )
            """
            try:
                conn.execute(sql)
            except (RuntimeError, OSError) as e:
                logger.warning("ducklake_table_creation_failed", table=table_name, error=str(e))

    def close(self):
        """Close database connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            except (RuntimeError, OSError) as e:
                logger.debug("ducklake_close_warning", error=str(e))
            self._connection = None

    # -------------------------------------------------------------------------
    # OCR Result Storage
    # -------------------------------------------------------------------------

    def store_ocr_result(self, result: OCRResultRecord) -> str:
        """
        Store an OCR result.

        Args:
            result: OCR result record

        Returns:
            Record ID
        """
        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.ocr_results_table}"

        sql = f"""
            INSERT INTO {table} (
                id, document_id, model_id, model_name, backend,
                text, confidence, elapsed_seconds, tokens_used,
                status, error_message, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        import json
        conn.execute(sql, [
            result.id,
            result.document_id,
            result.model_id,
            result.model_name,
            result.backend,
            result.text,
            result.confidence,
            result.elapsed_seconds,
            result.tokens_used,
            result.status,
            result.error_message,
            json.dumps(result.metadata),
            result.created_at.isoformat(),
        ])

        logger.info(f"Stored OCR result: {result.id} for document {result.document_id}")
        return result.id

    def store_ocr_results_batch(self, results: list[OCRResultRecord]) -> list[str]:
        """
        Store multiple OCR results (batch insert).

        CRITICAL: For batches >50 rows, consider dropping HNSW indexes first.
        """
        if not results:
            return []

        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.ocr_results_table}"

        import json
        values = []
        for result in results:
            values.append((
                result.id,
                result.document_id,
                result.model_id,
                result.model_name,
                result.backend,
                result.text,
                result.confidence,
                result.elapsed_seconds,
                result.tokens_used,
                result.status,
                result.error_message,
                json.dumps(result.metadata),
                result.created_at.isoformat(),
            ))

        placeholders = ", ".join(["(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"] * len(values))
        flat_values = [item for row in values for item in row]

        sql = f"""
            INSERT INTO {table} (
                id, document_id, model_id, model_name, backend,
                text, confidence, elapsed_seconds, tokens_used,
                status, error_message, metadata, created_at
            ) VALUES {placeholders}
        """

        conn.execute(sql, flat_values)
        logger.info(f"Stored {len(results)} OCR results in batch")
        return [r.id for r in results]

    # -------------------------------------------------------------------------
    # Model Comparison Storage
    # -------------------------------------------------------------------------

    def store_comparison(self, comparison: ComparisonRecord) -> str:
        """Store a model comparison result."""
        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.comparisons_table}"

        import json
        sql = f"""
            INSERT INTO {table} (
                id, document_id, comparison_timestamp, models_compared,
                best_model_id, best_confidence, metrics,
                irish_content_detected, irish_quality_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn.execute(sql, [
            comparison.id,
            comparison.document_id,
            comparison.comparison_timestamp.isoformat(),
            json.dumps(comparison.models_compared),
            comparison.best_model_id,
            comparison.best_confidence,
            json.dumps(comparison.metrics),
            comparison.irish_content_detected,
            comparison.irish_quality_score,
            datetime.utcnow().isoformat(),
        ])

        return comparison.id

    # -------------------------------------------------------------------------
    # Time-Travel Queries
    # -------------------------------------------------------------------------

    def get_ocr_history(
        self,
        document_id: str,
        as_of: datetime | str | None = None,
        model_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get OCR result history for a document.

        Args:
            document_id: Document identifier
            as_of: Optional timestamp for time-travel query
            model_id: Optional filter by model

        Returns:
            List of OCR results ordered by created_at DESC
        """
        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.ocr_results_table}"

        conditions = ["document_id = ?"]
        params = [document_id]

        if as_of:
            if isinstance(as_of, str):
                as_of_ts = as_of
            else:
                as_of_ts = as_of.isoformat()
            conditions.append("created_at <= ?")
            params.append(as_of_ts)

        if model_id:
            conditions.append("model_id = ?")
            params.append(model_id)

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT * FROM {table}
            WHERE {where_clause}
            ORDER BY created_at DESC
        """

        try:
            result = conn.execute(sql, params).fetchall()
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
        except (RuntimeError, OSError) as e:
            logger.error("ducklake_ocr_history_failed", error=str(e))
            return []

    def get_model_performance_over_time(
        self,
        model_id: str,
        start_date: datetime | str | None = None,
        end_date: datetime | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get model performance metrics over time."""
        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.ocr_results_table}"

        conditions = ["model_id = ?", "status = 'success'"]
        params = [model_id]

        if start_date:
            start_ts = start_date if isinstance(start_date, str) else start_date.isoformat()
            conditions.append("created_at >= ?")
            params.append(start_ts)

        if end_date:
            end_ts = end_date if isinstance(end_date, str) else end_date.isoformat()
            conditions.append("created_at <= ?")
            params.append(end_ts)

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT
                DATE_TRUNC('day', created_at) as date,
                COUNT(*) as document_count,
                AVG(confidence) as avg_confidence,
                AVG(elapsed_seconds) as avg_latency,
                SUM(tokens_used) as total_tokens
            FROM {table}
            WHERE {where_clause}
            GROUP BY DATE_TRUNC('day', created_at)
            ORDER BY date
        """

        try:
            result = conn.execute(sql, params).fetchall()
            columns = ["date", "document_count", "avg_confidence", "avg_latency", "total_tokens"]
            return [dict(zip(columns, row)) for row in result]
        except (RuntimeError, OSError) as e:
            logger.error("ducklake_model_performance_failed", error=str(e))
            return []

    # -------------------------------------------------------------------------
    # Snapshot Management
    # -------------------------------------------------------------------------

    def create_snapshot(
        self,
        snapshot_name: str,
        notes: str = "",
        configuration: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a comparison snapshot for reproducibility.

        Captures current state of all OCR results and comparisons.
        """
        conn = self._get_connection()
        results_table = f"{self.config.schema_name}.{self.config.ocr_results_table}"
        comparisons_table = f"{self.config.schema_name}.{self.config.comparisons_table}"
        snapshots_table = f"{self.config.schema_name}.{self.config.snapshots_table}"

        # Get summary metrics
        try:
            doc_count = conn.execute(f"SELECT COUNT(DISTINCT document_id) FROM {results_table}").fetchone()[0]
            model_count = conn.execute(f"SELECT COUNT(DISTINCT model_id) FROM {results_table}").fetchone()[0]

            # Aggregate metrics per model
            metrics_query = f"""
                SELECT
                    model_id,
                    COUNT(*) as count,
                    AVG(confidence) as avg_confidence,
                    AVG(elapsed_seconds) as avg_latency
                FROM {results_table}
                WHERE status = 'success'
                GROUP BY model_id
            """
            metrics_result = conn.execute(metrics_query).fetchall()
            summary_metrics = {
                row[0]: {
                    "count": row[1],
                    "avg_confidence": row[2],
                    "avg_latency": row[3],
                }
                for row in metrics_result
            }
        except (RuntimeError, OSError) as e:
            logger.warning("ducklake_snapshot_metrics_failed", error=str(e))
            doc_count = 0
            model_count = 0
            summary_metrics = {}

        snapshot = SnapshotRecord(
            snapshot_name=snapshot_name,
            document_count=doc_count,
            model_count=model_count,
            summary_metrics=summary_metrics,
            configuration=configuration or {},
            notes=notes,
        )

        import json
        sql = f"""
            INSERT INTO {snapshots_table} (
                id, snapshot_name, snapshot_timestamp, document_count,
                model_count, summary_metrics, configuration, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn.execute(sql, [
            snapshot.id,
            snapshot.snapshot_name,
            snapshot.snapshot_timestamp.isoformat(),
            snapshot.document_count,
            snapshot.model_count,
            json.dumps(snapshot.summary_metrics),
            json.dumps(snapshot.configuration),
            snapshot.notes,
            datetime.utcnow().isoformat(),
        ])

        logger.info("ducklake_snapshot_created", snapshot_name=snapshot_name, doc_count=doc_count, model_count=model_count)
        return snapshot.id

    def list_snapshots(self) -> list[dict[str, Any]]:
        """List all comparison snapshots."""
        conn = self._get_connection()
        table = f"{self.config.schema_name}.{self.config.snapshots_table}"

        try:
            sql = f"SELECT * FROM {table} ORDER BY snapshot_timestamp DESC"
            result = conn.execute(sql).fetchall()
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
        except (RuntimeError, OSError) as e:
            logger.error("ducklake_list_snapshots_failed", error=str(e))
            return []

    def get_results_at_snapshot(
        self,
        snapshot_id: str,
    ) -> list[dict[str, Any]]:
        """Get OCR results as they existed at a snapshot timestamp."""
        conn = self._get_connection()
        snapshots_table = f"{self.config.schema_name}.{self.config.snapshots_table}"
        results_table = f"{self.config.schema_name}.{self.config.ocr_results_table}"

        try:
            # Get snapshot timestamp
            snapshot = conn.execute(
                f"SELECT snapshot_timestamp FROM {snapshots_table} WHERE id = ?",
                [snapshot_id]
            ).fetchone()

            if not snapshot:
                return []

            snapshot_ts = snapshot[0]

            # Get results as of that timestamp
            sql = f"""
                SELECT * FROM {results_table}
                WHERE created_at <= ?
                ORDER BY document_id, model_id, created_at DESC
            """
            result = conn.execute(sql, [snapshot_ts]).fetchall()
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
        except (RuntimeError, OSError) as e:
            logger.error("ducklake_results_at_snapshot_failed", snapshot_id=snapshot_id, error=str(e))
            return []


# =============================================================================
# Mock Connection (for testing without DuckDB)
# =============================================================================


class MockConnection:
    """Mock connection for testing without DuckDB."""

    def __init__(self):
        self.data = {}
        self.description = []

    def execute(self, sql: str, params: list | None = None):
        logger.debug(f"Mock execute: {sql[:100]}...")
        return self

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def close(self):
        pass


# =============================================================================
# Convenience Functions
# =============================================================================


def create_storage(config: OCRStorageConfig | None = None) -> DuckLakeOCRStorage:
    """Create a new DuckLake OCR storage instance."""
    return DuckLakeOCRStorage(config)


def get_default_storage() -> DuckLakeOCRStorage:
    """Get default storage instance."""
    return DuckLakeOCRStorage()
