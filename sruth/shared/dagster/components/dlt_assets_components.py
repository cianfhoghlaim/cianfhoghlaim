"""Dagster-DLT Integration with @dlt_assets decorator.

This module provides components using the official dagster-dlt integration
with the @dlt_assets decorator pattern for automatic asset tracking.

References:
- https://docs.dagster.io/integrations/libraries/dlt
- https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-dlt

The @dlt_assets Pattern:
    from dagster_dlt import dlt_assets, DagsterDltResource

    @dlt_assets(
        name="curriculum_pages",
        dlt_resource= DagsterDltResource(),
        partitions_def=MultiPartitionsDefinition({...}),
    )
    def curriculum_dlt_asset(context, dlt: DagsterDltResource):
        yield from dlt.resources(curriculum_source()).with_resources(
            subject=context.partition_key.keys_by_dimension["subject"]
        )

This enables:
- Automatic asset key inference from DLT resource names
- Built-in partition handling
- Automatic materialization tracking
- Dagster UI integration with DLT load info
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable, Iterator

import dagster as dg
from dagster_dlt import DagsterDltResource, dlt_assets


# ============================================================================
# DLT ASSET COMPONENTS WITH OFFICIAL DAGSTER-DLT PATTERN
# ============================================================================

@dataclass
class DLTAssetsComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for DLT-based assets using @dlt_assets decorator.

    This component creates assets with the official dagster-dlt integration
    pattern, providing automatic asset tracking and partition handling.

    Example YAML:
        type: sruth.shared.dagster.components.dlt_assets_components.DLTAssetsComponent
        attributes:
          asset_key_prefix: ["ireland", "curriculum"]
          name: "junior_cycle"
          source_module: "sruth.oideachais.dlt_sources.ireland.curriculum_source"
          source_function: "curriculum_dlt_source"
    """

    # Asset identification
    asset_key_prefix: list[str] = dg.Field(
        default=["dlt"],
        description="Prefix for asset keys",
    )
    name: str = dg.Field(
        description="Asset name (suffix of asset key)",
    )
    group_name: str = dg.Field(
        default="dlt",
        description="Asset group name in Dagster UI",
    )

    # DLT source configuration
    source_module: str = dg.Field(
        description="Python module containing DLT source function",
    )
    source_function: str = dg.Field(
        default="dlt_source",
        description="Function name in module that returns DLT source",
    )

    # DLT pipeline configuration
    pipeline_name: str = dg.Field(
        description="DLT pipeline name",
    )
    dataset_name: str = dg.Field(
        default="data",
        description="DLT dataset name (table name)",
    )

    # Partitioning (optional)
    partitions_def: dg.PartitionsDefinition | None = None

    # Concurrency
    max_retries: int = dg.Field(
        default=3,
        description="Maximum retry attempts",
    )

    def _get_source_function(self) -> Callable:
        """Import and return the DLT source function."""
        import importlib
        module = importlib.import_module(self.source_module)
        return getattr(module, self.source_function)

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build Dagster definitions with @dlt_assets pattern."""
        from sruth.oideachais.dlt_utils import get_dlt_destination

        source_func = self._get_source_function()

        # Create retry policy
        retry_policy = dg.RetryPolicy(
            max_retries=self.max_retries,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        )

        # Create @dlt_assets decorated function
        @dlt_assets(
            name=self.name,
            dlt_resource=DagsterDltResource(
                pipeline_name=self.pipeline_name,
                destination=get_dlt_destination(),
                dataset_name=self.dataset_name,
            ),
            asset_key_prefix=self.asset_key_prefix,
            group_name=self.group_name,
            partitions_def=self.partitions_def,
            retry_policy=retry_policy,
            compute_kind="dlt",
        )
        def _dlt_asset(context, dlt: DagsterDltResource):
            """
            DLT asset function.

            This function is decorated with @dlt_assets which automatically:
            - Tracks DLT load info as asset materialization metadata
            - Handles partition context
            - Creates appropriate asset keys from resource names
            """
            # Get source function
            source = source_func()

            # Handle partition context
            if hasattr(context, "partition_key") and context.partition_key:
                if hasattr(context.partition_key, "keys_by_dimension"):
                    # MultiPartition context
                    partition_keys = context.partition_key.keys_by_dimension
                    # Configure source with partition values
                    yield from dlt.resources(source).with_resources(
                        **{k: v for k, v in partition_keys.items()}
                    )
                else:
                    # Single partition context
                    yield from dlt.resources(source).with_resources(
                        partition_value=str(context.partition_key)
                    )
            else:
                # No partition context
                yield from dlt.resources(source)

        return dg.Definitions(
            assets=[_dlt_asset],
        )


@dataclass
class CurriculumDLTAssetsComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for Irish curriculum DLT assets using @dlt_assets.

    Creates curriculum ingestion assets with proper DLT integration.

    Example YAML:
        type: sruth.shared.dagster.components.dlt_assets_components.CurriculumDLTAssetsComponent
        attributes:
          cycles:
            - "junior_cycle"
            - "senior_cycle"
          enable_multi_partition: true
    """

    cycles: list[str] = dg.Field(
        default=["junior_cycle", "senior_cycle", "primary", "early_childhood"],
        description="Curriculum cycles to create assets for",
    )
    asset_key_prefix: list[str] = dg.Field(
        default=["ireland", "curriculum"],
        description="Asset key prefix",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build curriculum DLT assets for each cycle."""
        from sruth.oideachais.dagster_defs.assets.ireland import (
            CYCLE_PARTITIONS,
            create_cycle_asset,
        )

        assets = []

        for cycle in self.cycles:
            if cycle in CYCLE_PARTITIONS:
                asset = create_cycle_asset(cycle)
                assets.append(asset)

        return dg.Definitions(assets=assets)


@dataclass
class GitHubDLTAssetsComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for GitHub ingestion using @dlt_assets.

    Creates GitHub assets with DLT integration.

    Example YAML:
        type: sruth.shared.dagster.components.dlt_assets_components.GitHubDLTAssetsComponent
        attributes:
          include_issues: true
          include_prs: true
          repos:
            - "dagster-io/dagster"
    """

    repos: list[str] = dg.Field(
        default_factory=list,
        description="GitHub repositories to ingest (owner/repo format)",
    )
    include_issues: bool = dg.Field(
        default=True,
        description="Include issues",
    )
    include_prs: bool = dg.Field(
        default=True,
        description="Include pull requests",
    )
    include_commits: bool = dg.Field(
        default=True,
        description="Include commits",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build GitHub DLT assets."""
        from sruth.crypteolas.dagster_assets.github_assets import (
            github_repo_data,
            github_issues,
            github_pull_requests,
            github_commits,
        )

        assets = [github_repo_data]

        if self.include_issues:
            assets.append(github_issues)
        if self.include_prs:
            assets.append(github_pull_requests)
        if self.include_commits:
            assets.append(github_commits)

        return dg.Definitions(assets=assets)


# ============================================================================
# MULTI-SOURCE DLT ASSET COMPONENT
# ============================================================================

@dataclass
class MultiSourceDLTComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for multiple DLT sources in a single asset.

    Aggregates data from multiple DLT sources into a single table.

    Example YAML:
        type: sruth.shared.dagster.components.dlt_assets_components.MultiSourceDLTComponent
        attributes:
          asset_key: ["aggregated", "curriculum"]
          sources:
            - module: "sruth.oideachais.dlt_sources.ireland.curriculum_source"
              function: "curriculum_dlt_source"
            - module: "sruth.oideachais.dlt_sources.england.curriculum_source"
              function: "curriculum_dlt_source"
    """

    asset_key: list[str] = dg.Field(
        default=["aggregated"],
        description="Asset key for aggregated data",
    )
    sources: list[dict] = dg.Field(
        default_factory=list,
        description="List of DLT sources to aggregate",
    )
    table_name: str = dg.Field(
        default="aggregated_data",
        description="Destination table name",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build multi-source DLT asset."""
        import importlib
        import dlt
        from sruth.oideachais.dlt_utils import get_dlt_destination

        @dg.asset(
            key=self.asset_key,
            group_name="multi_source",
            compute_kind="dlt",
        )
        def multi_source_asset(context) -> dg.MaterializeResult:
            """Aggregate data from multiple DLT sources."""
            destination = get_dlt_destination()

            total_rows = 0

            for source_config in self.sources:
                module = importlib.import_module(source_config["module"])
                source_func = getattr(module, source_config["function"])

                pipeline = dlt.pipeline(
                    pipeline_name=f"multi_source_{len(self.sources)}",
                    destination=destination,
                    dataset_name=self.table_name,
                )

                source = source_func()
                info = pipeline.run(source)

                for pkg in info.load_packages:
                    if hasattr(pkg, "jobs"):
                        for job in pkg.jobs.values():
                            if hasattr(job, "metrics"):
                                total_rows += getattr(job.metrics, "rows_count", 0)

            return dg.MaterializeResult(
                metadata={
                    "sources_count": len(self.sources),
                    "total_rows": total_rows,
                }
            )

        return dg.Definitions(assets=[multi_source_asset])


# ============================================================================
# DLT PIPELINE FACTORY COMPONENT
# ============================================================================

@dataclass
class DLTPipelineFactoryComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Factory component for complete DLT pipelines.

    Creates assets, resources, and schedules for a complete DLT pipeline.

    Example YAML:
        type: sruth.shared.dagster.components.dlt_assets_components.DLTPipelineFactoryComponent
        attributes:
          pipeline_name: "curriculum_ingestion"
          assets:
            - name: "junior_cycle"
              source_module: "..."
          schedules:
            - cron: "0 2 * * *"
    """

    pipeline_name: str = dg.Field(
        description="Pipeline name",
    )
    assets: list[dict] = dg.Field(
        default_factory=list,
        description="Asset configurations",
    )
    schedules: list[dict] = dg.Field(
        default_factory=list,
        description="Schedule configurations",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build complete DLT pipeline with assets and schedules."""
        from sruth.oideachais.dagster_defs.assets.ireland import (
            create_cycle_asset,
        )

        assets = []
        schedules = []

        # Create assets from configuration
        for asset_config in self.assets:
            if asset_config.get("type") == "cycle":
                asset = create_cycle_asset(asset_config["name"])
                assets.append(asset)

        # Create schedules from configuration
        for schedule_config in self.schedules:
            cron = schedule_config.get("cron", "0 2 * * *")
            job_name = schedule_config.get("job", f"{self.pipeline_name}_job")

            schedule = dg.ScheduleDefinition(
                name=f"{self.pipeline_name}_schedule",
                cron_schedule=cron,
                job_name=job_name,
            )
            schedules.append(schedule)

        return dg.Definitions(
            assets=assets,
            schedules=schedules,
        )


__all__ = [
    "DLTAssetsComponent",
    "CurriculumDLTAssetsComponent",
    "GitHubDLTAssetsComponent",
    "MultiSourceDLTComponent",
    "DLTPipelineFactoryComponent",
]
