"""
Benchmark Metrics Database.

SQLite database for tracking PDF extraction quality metrics over time,
based on pdfstract DatabaseService pattern with WAL mode for concurrency.
"""
from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Default database path
DEFAULT_DB_PATH = Path(__file__).parents[4] / "storage" / "data" / "extraction_metrics.db"


@dataclass
class ExtractionTask:
    """A document extraction task record."""

    task_id: str
    filename: str
    file_size_bytes: int
    document_type: str  # ncca, sec, circular, etc.

    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    total_duration_seconds: float | None = None

    selected_extractor: str | None = None
    output_format: str = "markdown"
    status: str = "pending"  # pending, running, completed, failed

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "file_size_bytes": self.file_size_bytes,
            "document_type": self.document_type,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": self.total_duration_seconds,
            "selected_extractor": self.selected_extractor,
            "output_format": self.output_format,
            "status": self.status,
        }


@dataclass
class ExtractorComparison:
    """Per-extractor comparison record."""

    task_id: str
    extractor_name: str

    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: float | None = None

    output_file: str | None = None
    output_size_bytes: int | None = None

    completeness_score: float | None = None
    irish_text_quality: float | None = None  # Special metric for Irish content

    status: str = "pending"
    error_message: str | None = None

    comparison_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "comparison_id": self.comparison_id,
            "task_id": self.task_id,
            "extractor_name": self.extractor_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "output_file": self.output_file,
            "output_size_bytes": self.output_size_bytes,
            "completeness_score": self.completeness_score,
            "irish_text_quality": self.irish_text_quality,
            "status": self.status,
            "error_message": self.error_message,
        }


class MetricsDatabase:
    """
    SQLite database for extraction metrics.

    Uses WAL mode for better concurrency, based on pdfstract pattern.
    """

    SCHEMA = """
    -- Extraction tasks
    CREATE TABLE IF NOT EXISTS extraction_tasks (
        task_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_size_bytes INTEGER,
        document_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        total_duration_seconds FLOAT,
        selected_extractor TEXT,
        output_format TEXT DEFAULT 'markdown',
        status TEXT DEFAULT 'pending'
    );

    -- Per-extractor comparisons
    CREATE TABLE IF NOT EXISTS extractor_comparisons (
        comparison_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        extractor_name TEXT NOT NULL,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds FLOAT,
        output_file TEXT,
        output_size_bytes INTEGER,
        completeness_score FLOAT,
        irish_text_quality FLOAT,
        status TEXT DEFAULT 'pending',
        error_message TEXT,
        FOREIGN KEY(task_id) REFERENCES extraction_tasks(task_id)
    );

    -- Aggregated extractor performance
    CREATE TABLE IF NOT EXISTS extractor_performance (
        extractor_name TEXT NOT NULL,
        document_type TEXT NOT NULL,
        total_extractions INTEGER DEFAULT 0,
        successful_extractions INTEGER DEFAULT 0,
        avg_duration_seconds FLOAT,
        avg_completeness_score FLOAT,
        avg_irish_quality FLOAT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (extractor_name, document_type)
    );

    -- Indexes for fast queries
    CREATE INDEX IF NOT EXISTS idx_tasks_created ON extraction_tasks(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_tasks_document_type ON extraction_tasks(document_type);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON extraction_tasks(status);
    CREATE INDEX IF NOT EXISTS idx_comparisons_task ON extractor_comparisons(task_id);
    CREATE INDEX IF NOT EXISTS idx_comparisons_extractor ON extractor_comparisons(extractor_name);
    """

    def __init__(self, db_path: Path | None = None):
        """
        Initialize metrics database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=30000")

            # Create tables
            conn.executescript(self.SCHEMA)
            conn.commit()

        logger.info(f"Initialized metrics database at {self.db_path}")

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # =========================================================================
    # Task Operations
    # =========================================================================

    def create_task(self, task: ExtractionTask) -> None:
        """Create a new extraction task."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO extraction_tasks
                (task_id, filename, file_size_bytes, document_type, created_at,
                 output_format, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.task_id,
                    task.filename,
                    task.file_size_bytes,
                    task.document_type,
                    task.created_at,
                    task.output_format,
                    task.status,
                ),
            )
            conn.commit()

    def update_task(
        self,
        task_id: str,
        status: str | None = None,
        completed_at: datetime | None = None,
        total_duration_seconds: float | None = None,
        selected_extractor: str | None = None,
    ) -> None:
        """Update task fields."""
        updates = []
        params = []

        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if completed_at is not None:
            updates.append("completed_at = ?")
            params.append(completed_at)
        if total_duration_seconds is not None:
            updates.append("total_duration_seconds = ?")
            params.append(total_duration_seconds)
        if selected_extractor is not None:
            updates.append("selected_extractor = ?")
            params.append(selected_extractor)

        if not updates:
            return

        params.append(task_id)

        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE extraction_tasks SET {', '.join(updates)} WHERE task_id = ?",
                params,
            )
            conn.commit()

    def get_task(self, task_id: str) -> ExtractionTask | None:
        """Get a task by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM extraction_tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()

            if row is None:
                return None

            return ExtractionTask(
                task_id=row["task_id"],
                filename=row["filename"],
                file_size_bytes=row["file_size_bytes"],
                document_type=row["document_type"],
                created_at=row["created_at"],
                completed_at=row["completed_at"],
                total_duration_seconds=row["total_duration_seconds"],
                selected_extractor=row["selected_extractor"],
                output_format=row["output_format"],
                status=row["status"],
            )

    def list_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        document_type: str | None = None,
    ) -> list[ExtractionTask]:
        """List extraction tasks with optional filtering."""
        query = "SELECT * FROM extraction_tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if document_type:
            query += " AND document_type = ?"
            params.append(document_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                ExtractionTask(
                    task_id=row["task_id"],
                    filename=row["filename"],
                    file_size_bytes=row["file_size_bytes"],
                    document_type=row["document_type"],
                    created_at=row["created_at"],
                    completed_at=row["completed_at"],
                    total_duration_seconds=row["total_duration_seconds"],
                    selected_extractor=row["selected_extractor"],
                    output_format=row["output_format"],
                    status=row["status"],
                )
                for row in rows
            ]

    # =========================================================================
    # Comparison Operations
    # =========================================================================

    def add_comparison(
        self,
        task_id: str,
        extractor_name: str,
    ) -> int:
        """Add a new comparison record."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO extractor_comparisons (task_id, extractor_name, start_time)
                VALUES (?, ?, ?)
                """,
                (task_id, extractor_name, datetime.now()),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def complete_comparison(
        self,
        task_id: str,
        extractor_name: str,
        duration_seconds: float,
        output_file: str | None = None,
        output_size_bytes: int | None = None,
        completeness_score: float | None = None,
        irish_text_quality: float | None = None,
        error_message: str | None = None,
    ) -> None:
        """Complete a comparison with results."""
        status = "completed" if error_message is None else "failed"

        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE extractor_comparisons
                SET end_time = ?,
                    duration_seconds = ?,
                    output_file = ?,
                    output_size_bytes = ?,
                    completeness_score = ?,
                    irish_text_quality = ?,
                    status = ?,
                    error_message = ?
                WHERE task_id = ? AND extractor_name = ?
                """,
                (
                    datetime.now(),
                    duration_seconds,
                    output_file,
                    output_size_bytes,
                    completeness_score,
                    irish_text_quality,
                    status,
                    error_message,
                    task_id,
                    extractor_name,
                ),
            )
            conn.commit()

    def get_comparisons(self, task_id: str) -> list[ExtractorComparison]:
        """Get all comparisons for a task."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM extractor_comparisons WHERE task_id = ?",
                (task_id,),
            ).fetchall()

            return [
                ExtractorComparison(
                    comparison_id=row["comparison_id"],
                    task_id=row["task_id"],
                    extractor_name=row["extractor_name"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    duration_seconds=row["duration_seconds"],
                    output_file=row["output_file"],
                    output_size_bytes=row["output_size_bytes"],
                    completeness_score=row["completeness_score"],
                    irish_text_quality=row["irish_text_quality"],
                    status=row["status"],
                    error_message=row["error_message"],
                )
                for row in rows
            ]

    # =========================================================================
    # Analytics
    # =========================================================================

    def get_extractor_stats(
        self,
        extractor_name: str | None = None,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get aggregated extractor performance statistics."""
        query = """
        SELECT
            extractor_name,
            document_type,
            COUNT(*) as total_extractions,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
            AVG(duration_seconds) as avg_duration,
            AVG(completeness_score) as avg_completeness,
            AVG(irish_text_quality) as avg_irish_quality
        FROM extractor_comparisons ec
        JOIN extraction_tasks et ON ec.task_id = et.task_id
        WHERE 1=1
        """
        params = []

        if extractor_name:
            query += " AND extractor_name = ?"
            params.append(extractor_name)
        if document_type:
            query += " AND document_type = ?"
            params.append(document_type)

        query += " GROUP BY extractor_name, document_type"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                {
                    "extractor_name": row["extractor_name"],
                    "document_type": row["document_type"],
                    "total_extractions": row["total_extractions"],
                    "successful": row["successful"],
                    "success_rate": row["successful"] / max(row["total_extractions"], 1),
                    "avg_duration": row["avg_duration"],
                    "avg_completeness": row["avg_completeness"],
                    "avg_irish_quality": row["avg_irish_quality"],
                }
                for row in rows
            ]

    def get_best_extractor(self, document_type: str) -> str | None:
        """
        Get the best extractor for a document type based on historical metrics.

        Ranking factors:
        1. Completeness score (40%)
        2. Success rate (30%)
        3. Irish text quality (20%)
        4. Speed (10%)
        """
        stats = self.get_extractor_stats(document_type=document_type)

        if not stats:
            return None

        def score(s: dict) -> float:
            completeness = s.get("avg_completeness") or 0
            success = s.get("success_rate") or 0
            irish = s.get("avg_irish_quality") or 0
            # Invert duration (faster = better)
            duration = s.get("avg_duration") or 999
            speed_score = max(0, 1 - duration / 60)  # Normalize to 60 seconds

            return (
                0.4 * completeness
                + 0.3 * success
                + 0.2 * irish
                + 0.1 * speed_score
            )

        best = max(stats, key=score)
        return best["extractor_name"]

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """Delete tasks older than specified days."""
        with self._get_connection() as conn:
            # Delete comparisons first
            conn.execute(
                """
                DELETE FROM extractor_comparisons
                WHERE task_id IN (
                    SELECT task_id FROM extraction_tasks
                    WHERE created_at < datetime('now', ?)
                )
                """,
                (f"-{days} days",),
            )

            # Delete tasks
            cursor = conn.execute(
                "DELETE FROM extraction_tasks WHERE created_at < datetime('now', ?)",
                (f"-{days} days",),
            )
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old extraction tasks")
            return deleted


# =============================================================================
# Convenience Functions
# =============================================================================

_metrics_db: MetricsDatabase | None = None


def get_metrics_db(db_path: Path | None = None) -> MetricsDatabase:
    """Get the singleton metrics database instance."""
    global _metrics_db
    if _metrics_db is None or (db_path and db_path != _metrics_db.db_path):
        _metrics_db = MetricsDatabase(db_path)
    return _metrics_db
