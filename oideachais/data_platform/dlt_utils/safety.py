"""
SerialDatabaseExecutor integration for DLT pipelines.

Ensures all DuckDB writes through DLT go through the single-threaded executor,
preventing segfaults and data corruption from concurrent access.

Usage:
    from data_platform.dlt_utils.safety import safe_dlt_run

    load_info = safe_dlt_run(pipeline, source_data)
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

import dlt

from core import get_executor

logger = logging.getLogger(__name__)

T = TypeVar("T")


def safe_dlt_run(
    pipeline: dlt.Pipeline,
    data: Any,
    **kwargs: Any,
) -> dlt.pipeline.LoadInfo:
    """
    Run DLT pipeline through SerialDatabaseExecutor.

    Wraps pipeline.run() to ensure all database operations go through the
    single-threaded executor, preventing DuckDB concurrent access issues.

    Args:
        pipeline: DLT pipeline to run
        data: Data source (generator, list, or dlt.resource)
        **kwargs: Additional arguments passed to pipeline.run()

    Returns:
        LoadInfo from the pipeline run

    Example:
        >>> pipeline = create_pipeline()
        >>> load_info = safe_dlt_run(pipeline, my_data_source())
        >>> print(load_info)
    """
    executor = get_executor()
    logger.debug(f"Running DLT pipeline '{pipeline.pipeline_name}' through serial executor")

    def _run() -> dlt.pipeline.LoadInfo:
        return pipeline.run(data, **kwargs)

    return executor.run(_run)


def safe_dlt_normalize(
    pipeline: dlt.Pipeline,
    **kwargs: Any,
) -> dlt.pipeline.NormalizeInfo:
    """
    Run DLT normalize through SerialDatabaseExecutor.

    Use when manually controlling extract/normalize/load phases.

    Args:
        pipeline: DLT pipeline to normalize
        **kwargs: Additional arguments passed to pipeline.normalize()

    Returns:
        NormalizeInfo from the normalize operation
    """
    executor = get_executor()
    logger.debug(f"Normalizing DLT pipeline '{pipeline.pipeline_name}' through serial executor")

    return executor.run(lambda: pipeline.normalize(**kwargs))


def safe_dlt_load(
    pipeline: dlt.Pipeline,
    **kwargs: Any,
) -> dlt.pipeline.LoadInfo:
    """
    Run DLT load through SerialDatabaseExecutor.

    Use when manually controlling extract/normalize/load phases.

    Args:
        pipeline: DLT pipeline to load
        **kwargs: Additional arguments passed to pipeline.load()

    Returns:
        LoadInfo from the load operation
    """
    executor = get_executor()
    logger.debug(f"Loading DLT pipeline '{pipeline.pipeline_name}' through serial executor")

    return executor.run(lambda: pipeline.load(**kwargs))


def safe_dataset_query(
    pipeline: dlt.Pipeline,
    sql: str,
) -> list[dict[str, Any]]:
    """
    Execute SQL query against pipeline dataset through serial executor.

    Args:
        pipeline: DLT pipeline with loaded data
        sql: SQL query to execute

    Returns:
        Query results as list of dicts

    Example:
        >>> results = safe_dataset_query(pipeline, "SELECT COUNT(*) FROM curriculum")
        >>> print(results)
    """
    executor = get_executor()

    def _query() -> list[dict[str, Any]]:
        with pipeline.sql_client() as client:
            with client.execute_query(sql) as cursor:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    return executor.run(_query)
