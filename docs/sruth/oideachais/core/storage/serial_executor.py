"""
Serial Database Executor for DuckDB/LanceDB Safety.

CRITICAL: All database operations MUST go through this executor to prevent
concurrent access crashes and data corruption.

DuckDB: Requires single-threaded access - concurrent operations cause
        segfaults and data corruption.
LanceDB: MVCC supports multi-process, but within-process needs serialization
         via this executor.
"""

from __future__ import annotations

import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any, Callable, Generator, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SerialDatabaseExecutor:
    """
    Single-threaded executor for database operations.

    DuckDB requires single-threaded access - concurrent operations cause
    segfaults and data corruption. This executor ensures all DB operations
    go through a single thread.

    Usage:
        executor = SerialDatabaseExecutor()
        result = executor.run(lambda conn: conn.execute("SELECT * FROM table"))

    Thread Safety:
        - All operations serialized through single worker thread
        - Safe to call from multiple threads
        - Blocks caller until operation completes

    Example:
        >>> executor = get_executor()
        >>> result = executor.run(
        ...     lambda: duckdb.connect(":memory:").execute("SELECT 1").fetchone()
        ... )
        >>> print(result)
        (1,)
    """

    _instance: SerialDatabaseExecutor | None = None
    _lock = threading.Lock()

    def __new__(cls) -> SerialDatabaseExecutor:
        """Singleton pattern - only one executor per process."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._executor = ThreadPoolExecutor(
                    max_workers=1, thread_name_prefix="db_serial"
                )
                cls._instance._initialized = True
                cls._instance._operation_count = 0
                logger.info("SerialDatabaseExecutor initialized (singleton)")
            return cls._instance

    def run(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a database operation in the serial thread.

        Args:
            fn: Function to execute (receives connection as first arg)
            *args: Additional arguments to pass to fn
            **kwargs: Keyword arguments to pass to fn

        Returns:
            Result of fn execution

        Raises:
            Exception: Any exception raised by fn is re-raised
        """
        self._operation_count += 1
        op_id = self._operation_count

        logger.debug(f"Submitting DB operation #{op_id}")
        future: Future[T] = self._executor.submit(fn, *args, **kwargs)

        try:
            result = future.result()
            logger.debug(f"DB operation #{op_id} completed successfully")
            return result
        except Exception as e:
            logger.error(f"DB operation #{op_id} failed: {e}")
            raise

    def run_async(
        self, fn: Callable[..., T], *args: Any, **kwargs: Any
    ) -> Future[T]:
        """
        Submit a database operation without waiting.

        Use sparingly - prefer run() for most operations to ensure
        proper error handling.

        Args:
            fn: Function to execute
            *args: Arguments to pass
            **kwargs: Keyword arguments to pass

        Returns:
            Future that will contain the result
        """
        self._operation_count += 1
        logger.debug(f"Submitting async DB operation #{self._operation_count}")
        return self._executor.submit(fn, *args, **kwargs)

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """
        Context manager for transaction-like operations.

        Note: This doesn't provide actual database transactions,
        but ensures a block of operations run serially.

        Usage:
            with executor.transaction():
                executor.run(lambda: db.insert(...))
                executor.run(lambda: db.update(...))
        """
        logger.debug("Starting serial transaction block")
        try:
            yield
        finally:
            logger.debug("Completed serial transaction block")

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.

        Args:
            wait: If True, wait for pending operations to complete
        """
        logger.info(
            f"Shutting down SerialDatabaseExecutor "
            f"(processed {self._operation_count} operations)"
        )
        self._executor.shutdown(wait=wait)
        logger.info("SerialDatabaseExecutor shutdown complete")

    @property
    def operation_count(self) -> int:
        """Number of operations processed by this executor."""
        return self._operation_count


# Global singleton instance
_executor: SerialDatabaseExecutor | None = None


def get_executor() -> SerialDatabaseExecutor:
    """Get the global SerialDatabaseExecutor instance."""
    global _executor
    if _executor is None:
        _executor = SerialDatabaseExecutor()
    return _executor


def run_serial(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Convenience function to run a database operation serially.

    Usage:
        result = run_serial(lambda conn: conn.execute("SELECT 1"))
    """
    return get_executor().run(fn, *args, **kwargs)
