"""Dagster Component for CocoIndex flows.

Creates Dagster assets from CocoIndex flow definitions.

Example YAML:
    type: sruth.shared.dagster.components.CocoIndexFlowComponent
    attributes:
      flow_module: "sruth.oideachais.cocoindex.flows.curriculum_flow"
      flow_name: "curriculum_extraction"

      sources:
        - type: "s3"
          bucket: "curriculum-pdfs"
          prefix: "ncca/"

      transformations:
        - type: "dspy"
          module: "sruth.shared.extraction.dspy_modules"
          class: "CurriculumExtractor"

      exports:
        - type: "postgres"
          table: "curriculum_structured"
        - type: "lancedb"
          namespace: "curriculum_embeddings"
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import dagster as dg


@dataclass
class SourceConfig:
    """Configuration for a data source."""

    type: str  # "s3", "local", "rest"
    path: str = ""
    bucket: str = ""
    prefix: str = ""
    included_patterns: list[str] = field(default_factory=list)
    excluded_patterns: list[str] = field(default_factory=list)
    binary: bool = False

    # REST-specific
    base_url: str = ""
    endpoints: list[str] = field(default_factory=list)
    auth_header: str = ""


@dataclass
class TransformConfig:
    """Configuration for a transformation step."""

    type: str  # "dspy", "baml", "split", "embed"
    module: str = ""
    class_name: str = ""
    function_name: str = ""

    # DSPy/BAML specific
    model: str = ""

    # Embedding specific
    embedding_model: str = ""
    batch_size: int = 100
    dimension: int = 1024

    # Split specific
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class ExportConfig:
    """Configuration for an export target."""

    type: str  # "postgres", "lancedb", "motherduck", "s3"
    table: str = ""
    namespace: str = "public"
    primary_key: str | None = None

    # LanceDB specific
    metric: str = "cosine"  # cosine, euclidean, dot

    # S3 specific
    s3_path: str = ""
    format: str = "parquet"


@dataclass
class CocoIndexFlowComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for CocoIndex flow definitions.

    Creates Dagster assets from CocoIndex flow definitions.
    Supports DSPy and BAML transformations.
    """

    # Flow location
    flow_module: str
    flow_name: str = "default_flow"

    # Sources
    sources: list[SourceConfig | dict] = field(default_factory=list)

    # Transformations
    transformations: list[TransformConfig | dict] = field(default_factory=list)

    # Exports
    exports: list[ExportConfig | dict] = field(default_factory=list)

    # Dagster asset configuration
    asset_key: list[str] = field(default_factory=list)
    group_name: str = "cocoindex"
    description: str = ""

    # Scheduling
    schedule_cron: str | None = None
    schedule_timezone: str = "UTC"

    def _normalize_configs(self) -> tuple[list[dict], list[dict], list[dict]]:
        """Normalize config objects to dicts."""
        sources = [
            s
            if isinstance(s, dict)
            else {
                "type": s.type,
                "path": s.path,
                "bucket": s.bucket,
                "prefix": s.prefix,
                "included_patterns": s.included_patterns,
                "excluded_patterns": s.excluded_patterns,
                "binary": s.binary,
                "base_url": s.base_url,
                "endpoints": s.endpoints,
                "auth_header": s.auth_header,
            }
            for s in self.sources
        ]

        transforms = [
            t
            if isinstance(t, dict)
            else {
                "type": t.type,
                "module": t.module,
                "class_name": t.class_name,
                "function_name": t.function_name,
                "model": t.model,
                "embedding_model": t.embedding_model,
                "batch_size": t.batch_size,
                "dimension": t.dimension,
                "chunk_size": t.chunk_size,
                "chunk_overlap": t.chunk_overlap,
            }
            for t in self.transformations
        ]

        exports = [
            e
            if isinstance(e, dict)
            else {
                "type": e.type,
                "table": e.table,
                "namespace": e.namespace,
                "primary_key": e.primary_key,
                "metric": e.metric,
                "s3_path": e.s3_path,
                "format": e.format,
            }
            for e in self.exports
        ]

        return sources, transforms, exports

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build Dagster assets from CocoIndex flow."""
        try:
            import cocoindex
        except ImportError:
            # Return empty defs if cocoindex not available
            return dg.Definitions()

        sources, transforms, exports = self._normalize_configs()

        # Create the flow definition
        flow_def = self._create_flow_definition(sources, transforms, exports)

        # Wrap in Dagster asset
        asset = self._create_asset(flow_def)

        # Add schedule if configured
        assets = [asset]
        schedules = []
        if self.schedule_cron:
            schedule = dg.ScheduleDefinition(
                name=f"{self.flow_name}_schedule",
                cron_schedule=self.schedule_cron,
                job=dg.define_asset_job(
                    name=f"{self.flow_name}_job",
                    selection=asset.key,
                ),
            )
            schedules.append(schedule)

        return dg.Definitions(
            assets=assets,
            schedules=schedules,
        )

    def _create_flow_definition(
        self,
        sources: list[dict],
        transforms: list[dict],
        exports: list[dict],
    ) -> Any:
        """Create CocoIndex flow definition from configs."""
        import cocoindex

        @cocoindex.flow_def(name=self.flow_name)
        def flow_definition(
            flow_builder: cocoindex.FlowBuilder,
            data_scope: cocoindex.DataScope,
        ) -> None:
            # Add sources
            for source_config in sources:
                source = self._create_source(source_config, cocoindex)
                data_scope[f"source_{source_config['type']}"] = flow_builder.add_source(source)

            # Add collectors for each source
            collectors = {}
            for source_config in sources:
                source_type = source_config["type"]
                collectors[source_type] = data_scope.add_collector()

            # Process each source
            for source_config in sources:
                source_type = source_config["type"]
                source_name = f"source_{source_type}"
                collector = collectors[source_type]

                with data_scope[source_name].row() as row:
                    # Apply transformations
                    for transform in transforms:
                        row = self._apply_transform(row, transform, cocoindex)

                    # Collect results
                    collector.collect(**row.as_dict())

            # Export to targets
            for export_config in exports:
                target = self._create_target(export_config)
                # Export from first available collector
                if collectors:
                    first_collector = next(iter(collectors.values()))
                    first_collector.export(
                        export_config.get("table", "exported_data"),
                        target,
                        primary_key_fields=[export_config["primary_key"]]
                        if export_config.get("primary_key")
                        else None,
                    )

        return flow_definition

    def _create_source(self, config: dict, cocoindex: Any) -> Any:
        """Create CocoIndex source from config."""
        source_type = config["type"]

        if source_type == "local":
            return cocoindex.sources.LocalFile(
                path=config.get("path", "."),
                binary=config.get("binary", False),
                included_patterns=config.get("included_patterns", []),
                excluded_patterns=config.get("excluded_patterns", []),
            )
        elif source_type == "s3":
            return cocoindex.sources.AmazonS3(
                bucket=config.get("bucket", ""),
                prefix=config.get("prefix", ""),
                included_patterns=config.get("included_patterns", []),
                excluded_patterns=config.get("excluded_patterns", []),
            )
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _apply_transform(self, row: Any, config: dict, cocoindex: Any) -> Any:
        """Apply transformation to a row."""
        transform_type = config["type"]

        if transform_type == "dspy":
            # DSPy transformation
            module_path = config.get("module")
            class_name = config.get("class_name")
            if module_path and class_name:
                # Dynamic import of DSPy module
                parts = module_path.rsplit(".", 1)
                module = __import__(parts[0], fromlist=[parts[1] if len(parts) > 1 else None])
                extractor_class = getattr(module, class_name)
                extractor = extractor_class(model=config.get("model"))
                # Apply extraction
                row["extracted"] = row["content"].transform(extractor)

        elif transform_type == "split":
            # Text chunking
            row["chunks"] = cocoindex.functions.SplitRecursively(
                chunk_size=config.get("chunk_size", 1000),
                chunk_overlap=config.get("chunk_overlap", 200),
            )

        elif transform_type == "embed":
            # Embedding generation
            row["embedding"] = cocoindex.functions.SentenceTransformerEmbed(
                model=config.get("embedding_model", "BAAI/bge-small-en-v1.5"),
                batch_size=config.get("batch_size", 100),
            )

        return row

    def _create_target(self, config: dict) -> Any:
        """Create export target from config."""
        target_type = config["type"]

        if target_type == "postgres":
            from sruth.shared.storage.postgres_target import CocoIndexPostgresTarget

            return CocoIndexPostgresTarget(
                table=config.get("table", ""),
                primary_key=config.get("primary_key"),
            )
        elif target_type == "lancedb":
            import cocoindex

            return cocoindex.targets.LanceDB(
                namespace=config.get("namespace", "default"),
                metric_type=getattr(
                    cocoindex.VectorSimilarityMetric,
                    config.get("metric", "COSINE_SIMILARITY").upper(),
                ),
            )
        else:
            raise ValueError(f"Unknown target type: {target_type}")

    def _create_asset(self, flow_def: Any) -> dg.Asset:
        """Create Dagster asset from flow definition."""

        @dg.asset(
            name=self.flow_name,
            key=self.asset_key or ["cocoindex", self.flow_name],
            group_name=self.group_name,
            description=self.description or f"CocoIndex flow: {self.flow_name}",
        )
        def cocoasset(context: dg.AssetExecutionContext) -> None:
            """Run CocoIndex flow."""
            import cocoindex

            # Get the flow runner
            runner = cocoindex.get_flow_runner(flow_def)

            # Execute the flow
            runner.run()

        return cocoasset


class DSPyTransformComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for DSPy-based transformations.

    Provides DSPy extraction as a Dagster resource or op.
    """

    # DSPy configuration
    module: str = ""
    class_name: str = ""
    model: str = "openai/gpt-4o"

    # Resource name
    resource_name: str = "dspy_extractor"

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build DSPy extractor resource."""

        @dg.resource(
            config_schema={
                "module": str,
                "class_name": str,
                "model": str,
            }
        )
        def dspy_extractor_resource(init_context):
            """DSPy extractor resource."""
            module_path = init_context.resource_config.get("module", self.module)
            class_name = init_context.resource_config.get("class_name", self.class_name)
            model = init_context.resource_config.get("model", self.model)

            parts = module_path.rsplit(".", 1)
            module = __import__(parts[0], fromlist=[parts[1] if len(parts) > 1 else None])
            extractor_class = getattr(module, class_name)

            return extractor_class(model=model)

        return dg.Definitions(
            resources={
                self.resource_name: dspy_extractor_resource.configured(
                    {
                        "module": self.module,
                        "class_name": self.class_name,
                        "model": self.model,
                    }
                )
            }
        )
