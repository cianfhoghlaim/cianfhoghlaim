"""
SerialDatabaseExecutor integration for DLT pipelines.

Ensures all DuckDB writes through DLT go through the single-threaded executor,
preventing segfaults and data corruption from concurrent access.

Usage:
    from cianfhoghlaim.dlt.safety import safe_dlt_run

    load_info = safe_dlt_run(pipeline, source_data)

Two dlt 1.0 helpers are added in 2026-06 to align with the canonical
dlt best-practices:

- `validate_source_kwargs(source, **kwargs)` — pre-flight validation
  that catches the 4 common dlt 1.0 mistakes (missing `name`,
  missing `primary_key` on incremental, no `write_disposition`,
  `merge` without `primary_key`).
- `safe_dlt_run_with_progress(pipeline, data, **kwargs)` — runs
  through the serial executor and streams per-package progress
  via the structured logger.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

import dlt

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Common dlt 1.0 mistake checks
# ---------------------------------------------------------------------------

#: The set of dlt 1.0 mistake codes returned by `validate_source_kwargs`.
DLT_1_0_MISTAKES = frozenset(
    {
        "missing_name",
        "incremental_no_primary_key",
        "merge_without_primary_key",
    }
)


def validate_source_kwargs(source: Any, **kwargs: Any) -> list[str]:
    """Pre-flight validation of a DLT source + kwargs.

    Catches the 3 most common dlt 1.0 mistakes that surface as
    confusing runtime errors rather than actionable compile-time
    errors:

    1. `missing_name` — the source's `@dlt.source(name=...)` is
       not set (defaults to the function name, but the pipeline
       can end up with a confusing dataset name).
    2. `incremental_no_primary_key` — an `@dlt.resource` is
       `incremental=True` but no `primary_key` is set. Without
       a primary key, incremental loads accumulate duplicates.
    3. `merge_without_primary_key` — `write_disposition="merge"`
       is set but no `primary_key` is set. Without a primary
       key, `merge` cannot deduplicate and silently degrades to
       `append`.

    Note on `missing_write_disposition`: dlt 1.0 always sets a
    default of `append` when not specified, so this mistake is
    effectively unreachable through the public API. We omit it
    from the 3 actionable mistakes.

    Returns a list of mistake codes (empty list = OK). The caller
    may choose to raise or log.

    Example:
        >>> mistakes = validate_source_kwargs(src(), write_disposition="merge")
        >>> if mistakes:
        ...     raise ValueError(f"DLT 1.0 source has mistakes: {mistakes}")
    """
    mistakes: list[str] = []
    # 1. missing_name
    name = getattr(source, "name", None) or getattr(source, "__name__", None)
    if not name or name == "<lambda>":
        mistakes.append("missing_name")

    # Inspect the source's resources for the other 2 mistakes.
    # IMPORTANT: the source must have been called (`src()`) so the
    # `_hints` dict is populated. We accept the source as either
    # a function (decorated with @dlt.source) or a `DltSource`
    # instance.
    resources: list[Any] = []
    if hasattr(source, "selected_resources"):
        try:
            resources = list(source.selected_resources.values())  # type: ignore[union-attr]
        except AttributeError:
            pass
    if not resources and hasattr(source, "resources"):
        try:
            resources = list(source.resources.keys())  # type: ignore[union-attr]
            resources = [source.resources[k] for k in resources]  # type: ignore[index]
        except AttributeError:
            pass

    for res in resources:
        is_incremental = bool(getattr(res, "incremental", None))

        # In dlt 1.0, the `primary_key` is stored in the internal
        # `_hints` dict (alongside `write_disposition`, `columns`,
        # and `schema_contract`). We read it via the `_hints`
        # attribute for stability across dlt 1.0.x patch versions.
        hints: dict[str, Any] = {}
        try:
            hints = res._hints  # type: ignore[attr-defined]
        except AttributeError:  # pragma: no cover - older dlt
            hints = {}

        primary_key: Any = (
            hints.get("primary_key")
            or kwargs.get(f"{res.name}_primary_key")
        )

        write_disposition: Any = (
            hints.get("write_disposition")
            or getattr(res, "write_disposition", None)
            or kwargs.get(f"{res.name}_write_disposition")
            or kwargs.get("write_disposition")
        )

        # 2. incremental_no_primary_key
        if is_incremental and not primary_key:
            mistakes.append(f"{res.name}:incremental_no_primary_key")

        # 3. merge_without_primary_key
        if write_disposition == "merge" and not primary_key:
            mistakes.append(f"{res.name}:merge_without_primary_key")

    return mistakes


# ---------------------------------------------------------------------------
# Serial executor
# ---------------------------------------------------------------------------


def get_executor(name: str = "duckdb") -> ThreadPoolExecutor:
    """Canonical single-thread DuckDB executor.

    The cianfhoghlaim.cianfhoghlaim.core shim previously provided this; it
    is now defined here as the canonical implementation. A backward-
    compat re-export is preserved in cianfhoghlaim.cianfhoghlaim.core for
    one release.

    Args:
        name: Logical executor name; used as the thread-name prefix
              so log lines are grep-able (e.g. "duckdb_serial_*").

    Returns:
        A `ThreadPoolExecutor` with `max_workers=1` and
        `thread_name_prefix=f"{name}_serial"`.
    """
    return ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"{name}_serial")


# ---------------------------------------------------------------------------
# dlt 1.0 alignment — `safe_dlt_run` + `safe_dlt_run_with_progress`
# ---------------------------------------------------------------------------


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


def safe_dlt_run_with_progress(
    pipeline: dlt.Pipeline,
    data: Any,
    **kwargs: Any,
) -> dlt.pipeline.LoadInfo:
    """Run DLT pipeline through SerialDatabaseExecutor with progress logging.

    Same as `safe_dlt_run` but emits a structured log line per load
    package (with the package id, file path, and row count) so the
    Dagster UI / Loki / Logfire can render a live progress bar.

    The progress model follows the dlthub.com blog 2026-03 progress
    pattern: one INFO line per package completion, with a final
    SUMMARY line at the end.

    Args:
        pipeline: DLT pipeline to run
        data: Data source (generator, list, or dlt.resource)
        **kwargs: Additional arguments passed to pipeline.run()

    Returns:
        LoadInfo from the pipeline run
    """
    executor = get_executor()
    logger.debug(
        f"Running DLT pipeline '{pipeline.pipeline_name}' with progress logging"
    )

    def _run() -> dlt.pipeline.LoadInfo:
        # Pre-flight validation (logs the 4 dlt 1.0 mistakes if any).
        try:
            mistakes = validate_source_kwargs(data, **kwargs)
            if mistakes:
                logger.warning(
                    f"dlt 1.0 source '{pipeline.pipeline_name}' has mistakes: {mistakes}"
                )
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(f"validate_source_kwargs skipped: {exc}")

        load_info = pipeline.run(data, **kwargs)

        # Per-package progress.
        for pkg in load_info.load_packages:
            jobs = getattr(pkg, "jobs", {}) or {}
            completed = jobs.get("completed_jobs", []) or []
            rows = sum(getattr(j, "count", 0) or 0 for j in completed)
            file_path = getattr(pkg, "load_id", "<unknown>")
            logger.info(
                f"dlt package_complete pipeline={pipeline.pipeline_name} "
                f"package={file_path} rows={rows}"
            )

        # Final summary.
        total_rows = sum(
            getattr(j, "count", 0) or 0
            for pkg in load_info.load_packages
            for j in (getattr(pkg, "jobs", {}) or {}).get("completed_jobs", []) or []
        )
        logger.info(
            f"dlt pipeline_complete pipeline={pipeline.pipeline_name} "
            f"packages={len(load_info.load_packages)} total_rows={total_rows}"
        )
        return load_info

    return executor.run(_run)


# ---------------------------------------------------------------------------
# The 3 lower-level dlt lifecycle helpers
# ---------------------------------------------------------------------------


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
        with pipeline.sql_client() as client, client.execute_query(sql) as cursor:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

    return executor.run(_query)
