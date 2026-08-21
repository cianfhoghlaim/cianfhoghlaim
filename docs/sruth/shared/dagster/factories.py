"""Dagster asset factories for common patterns.

This module provides factory functions for creating:
- DLT-based assets (with automatic source/destination management)
- Multi-partition assets (for complex partitioning)
- Observable assets (with Langfuse/Logfire/MLflow integration)
"""

from __future__ import annotations

import os
from typing import Any, Callable, TypeVar

import dagster as dg

T = TypeVar("T")


def dlt_asset_factory(
    dlt_source_fn: Callable,
    pipeline_name: str,
    dataset_name: str,
    write_disposition: str = "merge",
    primary_key: str | list[str] = "id",
    partitions_def: dg.PartitionsDefinition | None = None,
    retry_policy: dg.RetryPolicy | None = None,
    group_name: str = "dlt",
    description: str = "",
):
    """Factory for creating DLT-based Dagster assets.

    Handles:
    - DLT pipeline creation
    - Destination selection
    - Load info extraction
    - Metadata generation

    Args:
        dlt_source_fn: Function that returns DLT source
        pipeline_name: Name for the DLT pipeline
        dataset_name: Dataset/table name
        write_disposition: DLT write disposition (merge, replace, append)
        primary_key: Primary key for merge/upsert
        partitions_def: Optional partition definition
        retry_policy: Retry policy for failures
        group_name: Asset group name
        description: Asset description

    Example:
        def my_source():
            @dlt.resource
            def items():
                yield {"id": 1, "name": "Item"}
            return items

        my_asset = dlt_asset_factory(
            dlt_source_fn=my_source,
            pipeline_name="my_pipeline",
            dataset_name="my_data",
        )
    """

    @dg.asset(
        name=dataset_name,
        group_name=group_name,
        partitions_def=partitions_def,
        retry_policy=retry_policy or dg.RetryPolicy(max_retries=3, delay=30),
        description=description,
        compute_kind="dlt",
    )
    def _dlt_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
        """Execute DLT pipeline and return materialization result."""
        import dlt
        from sruth.shared.dlt.destinations import get_dlt_destination

        # Get partition keys if applicable
        partition_keys = None
        if partitions_def and context.partition_key:
            partition_keys = context.partition_key.keys_by_dimension

        # Create DLT pipeline
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name,
            destination=get_dlt_destination(),
            dataset_name=dataset_name,
            write_disposition=write_disposition,
        )

        # Run the source function
        source = dlt_source_fn(context, partition_keys)

        # Handle partition context in source
        if partition_keys:
            result = pipeline.run(
                source.with_resources(**partition_keys),
                write_disposition=write_disposition,
                primary_key=primary_key,
                table_name=dataset_name,
            )
        else:
            result = pipeline.run(
                source,
                write_disposition=write_disposition,
                primary_key=primary_key,
                table_name=dataset_name,
            )

        # Extract metrics for materialization
        rows_loaded = 0
        for load_package in result.load_packages:
            for job in load_package.jobs.values():
                if hasattr(job, "metrics"):
                    rows_loaded += getattr(job.metrics, "rows_count", 0)

        # Build metadata
        metadata = {
            "pipeline_name": pipeline_name,
            "load_id": str(result.loads_ids[0]) if result.loads_ids else "",
            "rows_loaded": rows_loaded,
        }

        if partition_keys:
            for key, value in partition_keys.items():
                metadata[key] = str(value)

        return dg.MaterializeResult(metadata=metadata)

    return _dlt_asset


def multi_partition_factory(
    assets_fn: Callable,
    partition_dims: dict[str, list[str]],
    asset_name: str,
    group_name: str = "multi_partition",
):
    """Factory for multi-partition assets (e.g., subject × year × language).

    Creates a MultiPartitionsDefinition with the specified dimensions.

    Args:
        assets_fn: Function that takes partition keys and returns data
        partition_dims: Dictionary of dimension name to values
        asset_name: Name for the asset
        group_name: Asset group name

    Example:
        def fetch_curriculum(subject: str, year: str, language: str):
            return scrape_curriculum(subject, year, language)

        curriculum_asset = multi_partition_factory(
            assets_fn=fetch_curriculum,
            partition_dims={
                "subject": ["mathematics", "english", "irish"],
                "year": [str(y) for y in range(2020, 2025)],
                "language": ["en", "ga"],
            },
            asset_name="curriculum",
        )
    """
    from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

    partitions_def = MultiPartitionsDefinition(
        {dim: StaticPartitionsDefinition(values) for dim, values in partition_dims.items()}
    )

    @dg.asset(
        name=asset_name,
        group_name=group_name,
        partitions_def=partitions_def,
        compute_kind="multi_partition",
    )
    def _multi_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
        """Execute asset function with partition context."""
        partition_keys = context.partition_key.keys_by_dimension
        data = assets_fn(**partition_keys)

        # Count records for metadata
        if isinstance(data, list):
            row_count = len(data)
        elif isinstance(data, dict):
            row_count = len(data.get("items", []))
        else:
            row_count = 1

        return dg.MaterializeResult(
            metadata={
                **partition_keys,
                "row_count": row_count,
            }
        )

    return _multi_asset


def observable_asset(
    asset_fn: Callable,
    langfuse: bool = True,
    logfire: bool = True,
    mlflow: bool = False,
    **asset_kwargs,
):
    """Factory for observable assets with automatic instrumentation.

    Wraps an asset function with observability integrations:
    - Langfuse: LLM call tracking, cost attribution
    - Logfire: Structured logging, performance metrics
    - MLflow: Experiment tracking, artifact storage

    Args:
        asset_fn: The asset function to wrap
        langfuse: Enable Langfuse tracing
        logfire: Enable Logfire logging
        mlflow: Enable MLflow tracking
        **asset_kwargs: Additional arguments for @asset decorator

    Example:
        @observable_asset(
            langfuse=True,
            logfire=True,
        )
        def my_asset(context: AssetExecutionContext):
            return process_data()
    """

    # Apply base decorator
    @dg.asset(**asset_kwargs)
    def _observable_asset(context: dg.AssetExecutionContext):
        """Asset function with automatic observability."""
        # Langfuse integration
        if langfuse:
            from sruth.shared.observability import langfuse_observe

            langfuse_observe.start_span(
                name=context.asset_key.to_string(),
                metadata={"partition_key": str(context.partition_key)},
            )

        try:
            result = asset_fn(context)

            # Track success
            if langfuse:
                langfuse_observe.end_span(success=True)

            if mlflow:
                import mlflow

                with mlflow.start_run() as run:
                    mlflow.log_metric(
                        f"{context.asset_key.to_string()}_success",
                        1,
                    )

            return result

        except Exception as e:
            # Track failure
            if langfuse:
                langfuse_observe.end_span(success=False, error=str(e))

            if logfire:
                import logfire

                logfire.error(
                    f"{context.asset_key.to_string()}_failed",
                    error=str(e),
                )

            raise

    return _observable_asset
