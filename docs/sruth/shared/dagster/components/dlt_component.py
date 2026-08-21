"""Dagster Component for DLT-based assets.

Creates Dagster assets from DLT sources with YAML configuration.

Example YAML:
    type: sruth.shared.dagster.components.DLTAssetComponent
    attributes:
      asset_key: ["curriculum", "pages"]
      source_module: "sruth.oideachais.dlt_sources.curriculum_source"
      pipeline_name: "curriculum_pipeline"
      dataset_name: "curriculum"
      write_disposition: "merge"
      primary_key: "url"
      partitions:
        subject:
          type: "static"
          values: ["mathematics", "english", "irish"]
        language:
          type: "static"
          values: ["en", "ga"]
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Callable

import dagster as dg


@dataclass
class PartitionConfig:
    """Configuration for a single partition dimension."""

    type: str  # "static", "time", "dynamic"
    values: list[str] | None = None
    fmt: str | None = None  # For time partitions: "%Y-%m-%d"


@dataclass
class DLTAssetComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for DLT-based assets.

    Wraps DLT sources into Dagster assets with configurable
    partitioning, retry policies, and metadata.
    """

    # Asset identification
    asset_key: list[str] = field(default_factory=list)
    asset_name: str = ""
    group_name: str = "dlt"
    description: str = ""

    # DLT source configuration
    source_module: str = ""  # Python module path to DLT source
    source_function: str = "source"  # Function name in module
    pipeline_name: str = ""
    dataset_name: str = ""

    # DLT pipeline options
    write_disposition: str = "merge"
    primary_key: str | list[str] = "id"

    # Partitioning
    partitions: dict[str, dict[str, Any]] | None = None

    # Retry policy
    max_retries: int = 3
    retry_delay: int = 30

    # Observability
    enable_langfuse: bool = True
    enable_mlflow: bool = False

    def _get_source_function(self) -> Callable:
        """Import and return the DLT source function."""
        module = importlib.import_module(self.source_module)
        return getattr(module, self.source_function)

    def _create_partitions_def(self) -> dg.PartitionsDefinition | None:
        """Create Dagster partitions definition from config."""
        if not self.partitions:
            return None

        partitions = {}

        for dim_name, dim_config in self.partitions.items():
            partition_type = dim_config.get("type", "static")

            if partition_type == "static":
                values = dim_config.get("values", [])
                partitions[dim_name] = dg.StaticPartitionsDefinition(values)

            elif partition_type == "time":
                fmt = dim_config.get("fmt", "%Y-%m-%d")
                # Time-based partitioning options
                schedule_type = dim_config.get("schedule", "daily")
                if schedule_type == "daily":
                    partitions[dim_name] = dg.DailyPartitionsDefinition(fmt)
                elif schedule_type == "weekly":
                    partitions[dim_name] = dg.WeeklyPartitionsDefinition(fmt)
                elif schedule_type == "monthly":
                    partitions[dim_name] = dg.MonthlyPartitionsDefinition(fmt)

        if len(partitions) == 1:
            return list(partitions.values())[0]

        if len(partitions) > 1:
            return dg.MultiPartitionsDefinition(partitions)

        return None

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build Dagster definitions from this component."""
        import dlt

        from sruth.shared.dlt.destinations import get_dlt_destination
        from sruth.shared.observability import get_tracer

        source_func = self._get_source_function()
        partitions_def = self._create_partitions_def()

        # Get asset name
        asset_name = self.asset_name or self.asset_key[-1] if self.asset_key else "dlt_asset"

        # Create retry policy
        retry_policy = dg.RetryPolicy(
            max_retries=self.max_retries,
            delay=self.retry_delay,
        )

        @dg.asset(
            key=self.asset_key or [asset_name],
            name=asset_name,
            group_name=self.group_name,
            partitions_def=partitions_def,
            retry_policy=retry_policy,
            description=self.description or f"DLT asset: {self.pipeline_name}",
            compute_kind="dlt",
        )
        def dlt_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            """Execute DLT pipeline and return materialization result."""
            with get_tracer().trace_asset(
                asset_name=asset_name,
                partition_key=str(context.partition_key) if context.partition_key else None,
            ):
                # Get partition keys if applicable
                partition_keys = None
                if partitions_def and context.partition_key:
                    partition_keys = context.partition_key.keys_by_dimension

                # Create DLT pipeline
                pipeline = dlt.pipeline(
                    pipeline_name=self.pipeline_name,
                    destination=get_dlt_destination(),
                    dataset_name=self.dataset_name,
                    write_disposition=self.write_disposition,
                )

                # Run the source function
                source = source_func(context, partition_keys)

                # Handle partition context
                if partition_keys:
                    result = pipeline.run(
                        source.with_resources(**partition_keys),
                        write_disposition=self.write_disposition,
                        primary_key=self.primary_key,
                        table_name=self.dataset_name,
                    )
                else:
                    result = pipeline.run(
                        source,
                        write_disposition=self.write_disposition,
                        primary_key=self.primary_key,
                        table_name=self.dataset_name,
                    )

                # Extract metrics
                rows_loaded = 0
                for load_package in result.load_packages:
                    for job in load_package.jobs.values():
                        if hasattr(job, "metrics"):
                            rows_loaded += getattr(job.metrics, "rows_count", 0)

                # Build metadata
                metadata = {
                    "pipeline_name": self.pipeline_name,
                    "load_id": str(result.loads_ids[0]) if result.loads_ids else "",
                    "rows_loaded": rows_loaded,
                    "write_disposition": self.write_disposition,
                }

                if partition_keys:
                    for key, value in partition_keys.items():
                        metadata[key] = str(value)

                return dg.MaterializeResult(metadata=metadata)

        return dg.Definitions(assets=[dlt_asset])


@dataclass
class DLTSourceComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for defining DLT sources.

    Creates reusable DLT sources that can be used by
    DLTAssetComponent instances.
    """

    name: str = ""
    source_type: str = "rest"  # "rest", "browser", "file"

    # REST API configuration
    base_url: str = ""
    auth_type: str = "none"  # "none", "bearer", "api_key", "basic"
    auth_token: str = ""
    headers: dict[str, str] = field(default_factory=dict)

    # Pagination
    paginator_type: str = "page"  # "page", "cursor", "link", "none"
    page_param: str = "page"
    page_size: int = 100
    cursor_param: str = "cursor"

    # Browser scraping configuration
    browser_backend: str = "stagehand"  # "stagehand", "crawl4ai", "browserbase"
    extract_instruction: str = ""
    extract_formats: list[str] = field(default_factory=lambda: ["markdown"])

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build DLT source definition."""
        from sruth.shared.dlt.sources import RESTSource, BrowserSource

        if self.source_type == "rest":
            source = RESTSource(
                base_url=self.base_url,
                auth_header="Authorization" if self.auth_type == "bearer" else None,
                auth_token=self.auth_token if self.auth_type == "bearer" else None,
                auth_type=self.auth_type,
                page_size=self.page_size,
            )

        elif self.source_type == "browser":
            source = BrowserSource(
                preferred_backend=self.browser_backend,
            )

        else:
            raise ValueError(f"Unknown source_type: {self.source_type}")

        # Return empty definitions - source is registered in module
        return dg.Definitions()
