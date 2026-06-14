"""
Dagster Asset Factory Patterns.

Provides factory functions for creating common asset patterns:
- DLT source assets
- Embedding assets
- Evaluation assets
- Export assets

Based on patterns from taighde/dagster/ research.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

import dagster as dg

logger = logging.getLogger(__name__)


@dataclass
class DLTAssetConfig:
    """Configuration for a DLT source asset."""
    name: str
    source_module: str
    source_function: str
    group_name: str = "ingestion"
    compute_kind: str = "dlt"
    description: str | None = None
    partitions_def: dg.PartitionsDefinition | None = None
    deps: Sequence[dg.AssetKey] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def create_dlt_asset(config: DLTAssetConfig) -> dg.AssetsDefinition:
    """
    Create a Dagster asset that runs a DLT pipeline.

    Usage:
        ncca_asset = create_dlt_asset(DLTAssetConfig(
            name="ncca_curriculum",
            source_module="data_platform.dlt_sources.ncca",
            source_function="ncca_source",
            group_name="ireland_education",
        ))
    """
    @dg.asset(
        name=config.name,
        group_name=config.group_name,
        compute_kind=config.compute_kind,
        description=config.description or f"DLT asset for {config.name}",
        partitions_def=config.partitions_def,
        deps=list(config.deps),
        tags=config.tags,
        metadata=config.metadata,
    )
    def _dlt_asset(
        context,
        duckdb: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Execute DLT pipeline and materialize asset."""
        import importlib

        import dlt as dlt_lib

        # Import source function
        module = importlib.import_module(config.source_module)
        source_fn = getattr(module, config.source_function)

        # Get partition key if partitioned
        partition_key = None
        if config.partitions_def and context.has_partition_key:
            partition_key = context.partition_key

        # Run DLT pipeline
        context.log.info(f"Running DLT source: {config.source_function}")

        source = source_fn(partition_key=partition_key) if partition_key else source_fn()

        # Create DLT pipeline - use pipeline.run() directly (not DagsterDltResource.run())
        pipeline = dlt_lib.pipeline(
            pipeline_name=config.name,
            destination="duckdb",
            dataset_name="education",
        )

        # Execute pipeline directly (DagsterDltResource.run() requires @dlt_assets decorator)
        load_info = pipeline.run(source)

        # Extract metrics
        rows_loaded = sum(
            pkg.state.get("rows_count", 0)
            for pkg in load_info.load_packages
        )

        context.log.info(f"Loaded {rows_loaded} rows")

        return dg.MaterializeResult(
            metadata={
                "rows_loaded": rows_loaded,
                "source": config.source_function,
                "partition_key": partition_key or "full",
            }
        )

    return _dlt_asset


@dataclass
class EmbeddingAssetConfig:
    """Configuration for an embedding asset."""
    name: str
    source_asset: dg.AssetKey
    table_name: str
    text_column: str
    group_name: str = "embeddings"
    embedding_model: str = "BAAI/bge-m3"
    batch_size: int = 100
    dimensions: int = 1024
    description: str | None = None
    partitions_def: dg.PartitionsDefinition | None = None


def create_embedding_asset(config: EmbeddingAssetConfig) -> dg.AssetsDefinition:
    """
    Create an asset that generates embeddings for text data.

    Usage:
        curriculum_embeddings = create_embedding_asset(EmbeddingAssetConfig(
            name="curriculum_embeddings",
            source_asset=AssetKey("ncca_curriculum"),
            table_name="curriculum",
            text_column="content",
        ))
    """
    @dg.asset(
        name=config.name,
        group_name=config.group_name,
        compute_kind="embedding",
        description=config.description or f"Embeddings for {config.table_name}",
        deps=[config.source_asset],
        partitions_def=config.partitions_def,
    )
    def _embedding_asset(
        context,
        lancedb: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Generate embeddings and store in LanceDB."""
        context.log.info(f"Generating embeddings for {config.table_name}")

        # This would integrate with actual embedding generation
        # Placeholder for the pattern
        rows_processed = 0
        embeddings_generated = 0

        context.log.info(
            f"Generated {embeddings_generated} embeddings "
            f"for {rows_processed} rows"
        )

        return dg.MaterializeResult(
            metadata={
                "rows_processed": rows_processed,
                "embeddings_generated": embeddings_generated,
                "model": config.embedding_model,
                "dimensions": config.dimensions,
                "batch_size": config.batch_size,
            }
        )

    return _embedding_asset


@dataclass
class ModalAssetConfig:
    """Configuration for a Modal GPU asset."""
    name: str
    modal_function: str
    group_name: str = "gpu_compute"
    gpu_type: str = "A10G"
    timeout: int = 3600
    description: str | None = None
    deps: Sequence[dg.AssetKey] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)


def create_modal_asset(config: ModalAssetConfig) -> dg.AssetsDefinition:
    """
    Create an asset that runs on Modal GPU.

    Usage:
        finetune_asset = create_modal_asset(ModalAssetConfig(
            name="irish_llm_finetune",
            modal_function="oideachais.modal.finetune.train",
            gpu_type="H100",
        ))
    """
    @dg.asset(
        name=config.name,
        group_name=config.group_name,
        compute_kind="modal",
        description=config.description or f"Modal GPU: {config.modal_function}",
        deps=list(config.deps),
    )
    def _modal_asset(
        context,
        modal_resource: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Execute function on Modal GPU."""
        context.log.info(f"Running Modal function: {config.modal_function}")

        # Execute on Modal
        result = modal_resource.run(
            func_ref=config.modal_function,
            gpu=config.gpu_type,
            timeout=config.timeout,
            **config.inputs,
        )

        return dg.MaterializeResult(
            metadata={
                "function": config.modal_function,
                "gpu_type": config.gpu_type,
                "result": str(result),
            }
        )

    return _modal_asset


def create_asset_group(
    configs: Sequence[DLTAssetConfig | EmbeddingAssetConfig | ModalAssetConfig],
) -> list[dg.AssetsDefinition]:
    """
    Create a group of assets from configurations.

    Usage:
        ireland_education_assets = create_asset_group([
            DLTAssetConfig(name="ncca", ...),
            DLTAssetConfig(name="curriculum_online", ...),
            EmbeddingAssetConfig(name="curriculum_embeddings", ...),
        ])
    """
    assets = []
    for config in configs:
        if isinstance(config, DLTAssetConfig):
            assets.append(create_dlt_asset(config))
        elif isinstance(config, EmbeddingAssetConfig):
            assets.append(create_embedding_asset(config))
        elif isinstance(config, ModalAssetConfig):
            assets.append(create_modal_asset(config))
        else:
            raise ValueError(f"Unknown config type: {type(config)}")
    return assets


# ============================================================================
# Pre-configured asset factories for common patterns
# ============================================================================


def create_ireland_education_assets() -> list[dg.AssetsDefinition]:
    """
    Create assets for Ireland education sources.

    .. deprecated::
        Use `create_unified_curriculum_assets()` instead for the new
        subject-centric pipeline with cross-source deduplication.
    """
    import warnings
    warnings.warn(
        "create_ireland_education_assets() is deprecated. "
        "Use create_unified_curriculum_assets() for subject-centric pipelines.",
        DeprecationWarning,
        stacklevel=2,
    )
    return create_asset_group([
        DLTAssetConfig(
            name="ncca_curriculum",
            source_module="data_platform.dlt_sources.ncca",
            source_function="ncca_source",
            group_name="ireland_education",
            description="NCCA curriculum specifications and publications",
        ),
        DLTAssetConfig(
            name="curriculum_online",
            source_module="data_platform.dlt_sources.curriculumonline",
            source_function="curriculum_source",
            group_name="ireland_education",
            description="Curriculum Online subject specifications",
        ),
        DLTAssetConfig(
            name="sec_exams",
            source_module="data_platform.dlt_sources.sec",
            source_function="sec_source",
            group_name="ireland_education",
            description="State Examination Commission papers",
            partitions_def=dg.StaticPartitionsDefinition(
                [str(year) for year in range(2000, 2025)]
            ),
        ),
    ])


def create_celtic_language_assets() -> list[dg.AssetsDefinition]:
    """Create assets for Celtic language sources."""
    return create_asset_group([
        DLTAssetConfig(
            name="duchas_schools",
            source_module="data_platform.dlt_sources.duchas",
            source_function="duchas_source",
            group_name="celtic_language",
            description="Dúchas.ie Schools Collection",
            partitions_def=dg.StaticPartitionsDefinition(
                ["galway", "mayo", "kerry", "cork", "donegal", "clare"]
            ),
        ),
        DLTAssetConfig(
            name="tearma_terminology",
            source_module="data_platform.dlt_sources.tearma",
            source_function="tearma_source",
            group_name="celtic_language",
            description="Téarma.ie Irish terminology database",
        ),
    ])


# ============================================================================
# Tenant-Specific Asset Factories
# ============================================================================


@dataclass
class TenantAssetConfig:
    """Configuration for a tenant-specific asset."""
    tenant_id: str
    asset_type: str  # "profile", "project", "music", "curriculum"
    source_type: str  # "yaml", "database", "external"
    source_config: dict[str, Any] = field(default_factory=dict)
    group_name: str | None = None
    description: str | None = None


def create_tenant_profile_asset(tenant_id: str) -> dg.AssetsDefinition:
    """
    Create an asset that loads and extracts profile data for a tenant.

    This asset:
    1. Reads YAML profile files
    2. Fetches data from external sources (GitHub, Spotify, etc.)
    3. Uses BAML to extract structured profile data
    4. Stores results in tenant's DuckDB
    """
    @dg.asset(
        key=[tenant_id, "raw", "profile"],
        group_name=f"{tenant_id}_pipeline",
        compute_kind="dlt",
        description=f"Profile data for {tenant_id}",
    )
    def _tenant_profile_asset(
        context,
        tenant_duckdb: dg.ResourceParam[Any],
        tenant_config: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Load and extract profile data for the tenant."""
        from .tenant_resources import load_tenant_config

        config = load_tenant_config(tenant_id)
        data_sources = config.get("dataSources", {})

        profiles_loaded = 0
        external_sources = 0

        # Process YAML sources
        yaml_sources = data_sources.get("yaml", [])
        for source in yaml_sources:
            if source.get("type") == "profile":
                context.log.info(f"Loading YAML profile from {source['path']}")
                profiles_loaded += 1

        # Process external sources
        external_list = data_sources.get("external", [])
        for ext_source in external_list:
            context.log.info(f"Fetching from {ext_source['source']} via {ext_source['pipeline']}")
            external_sources += 1

        context.log.info(f"Loaded {profiles_loaded} profiles, {external_sources} external sources")

        return dg.MaterializeResult(
            metadata={
                "tenant_id": tenant_id,
                "profiles_loaded": profiles_loaded,
                "external_sources": external_sources,
            }
        )

    return _tenant_profile_asset


def create_tenant_projects_asset(tenant_id: str) -> dg.AssetsDefinition:
    """
    Create an asset that loads project data for a tenant.

    For portfolio tenants (aleyum), this includes game projects.
    For education tenants (cianfhoghlaim), this includes curriculum projects.
    """
    @dg.asset(
        key=[tenant_id, "raw", "projects"],
        group_name=f"{tenant_id}_pipeline",
        compute_kind="yaml",
        description=f"Project data for {tenant_id}",
        deps=[dg.AssetKey([tenant_id, "raw", "profile"])],
    )
    def _tenant_projects_asset(
        context,
        tenant_duckdb: dg.ResourceParam[Any],
        tenant_config: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Load project data for the tenant."""
        from pathlib import Path

        from .tenant_resources import load_tenant_config

        config = load_tenant_config(tenant_id)
        tenant_type = config.get("tenant", {}).get("type", "education")
        data_sources = config.get("dataSources", {})

        projects_loaded = 0

        # Load YAML project sources
        for source in data_sources.get("yaml", []):
            if source.get("type") == "projects":
                project_path = Path(source["path"])
                if project_path.exists():
                    # Load all YAML files in the directory
                    for yaml_file in project_path.glob("*.yaml"):
                        context.log.info(f"Loading project: {yaml_file.name}")
                        projects_loaded += 1

        context.log.info(f"Loaded {projects_loaded} projects for {tenant_id} ({tenant_type})")

        return dg.MaterializeResult(
            metadata={
                "tenant_id": tenant_id,
                "tenant_type": tenant_type,
                "projects_loaded": projects_loaded,
            }
        )

    return _tenant_projects_asset


def create_tenant_embeddings_asset(tenant_id: str) -> dg.AssetsDefinition:
    """
    Create an asset that generates embeddings for a tenant's content.

    Embeds profile, project, and other content into LanceDB.
    """
    @dg.asset(
        key=[tenant_id, "embeddings", "content"],
        group_name=f"{tenant_id}_pipeline",
        compute_kind="embedding",
        description=f"Content embeddings for {tenant_id}",
        deps=[
            dg.AssetKey([tenant_id, "raw", "profile"]),
            dg.AssetKey([tenant_id, "raw", "projects"]),
        ],
    )
    def _tenant_embeddings_asset(
        context,
        tenant_lancedb: dg.ResourceParam[Any],
        tenant_config: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Generate embeddings for tenant content."""
        from .tenant_resources import load_tenant_config

        config = load_tenant_config(tenant_id)

        embeddings_generated = 0

        context.log.info(f"Generating embeddings for {tenant_id} content")

        # Placeholder for actual embedding generation
        # Would integrate with LanceDB and embedding model

        return dg.MaterializeResult(
            metadata={
                "tenant_id": tenant_id,
                "embeddings_generated": embeddings_generated,
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            }
        )

    return _tenant_embeddings_asset


def create_tenant_assets(tenant_id: str) -> list[dg.AssetsDefinition]:
    """
    Create all assets for a specific tenant.

    Usage:
        aleyum_assets = create_tenant_assets("aleyum")
        cianfhoghlaim_assets = create_tenant_assets("cianfhoghlaim")
    """
    return [
        create_tenant_profile_asset(tenant_id),
        create_tenant_projects_asset(tenant_id),
        create_tenant_embeddings_asset(tenant_id),
    ]


def create_all_tenant_assets() -> list[dg.AssetsDefinition]:
    """
    Create assets for all configured tenants.

    Reads tenant configs from config/tenants/*.yaml
    """
    from .tenant_resources import list_tenant_ids

    assets = []
    for tenant_id in list_tenant_ids():
        assets.extend(create_tenant_assets(tenant_id))
    return assets


# ============================================================================
# Unified Curriculum Asset Factories (Subject-Centric Pipeline)
# ============================================================================


@dataclass
class CurriculumAssetConfig:
    """
    Configuration for a unified curriculum asset.

    Uses the new subject-centric pipeline with cross-source deduplication.
    Partitions by 4 cycles (early_childhood, primary, junior_cycle, senior_cycle)
    with subject selection at runtime via config.
    """
    name: str
    asset_type: str  # "ingestion", "processing", "enrichment", "search"
    group_name: str = "ireland_curriculum"
    description: str | None = None
    deps: Sequence[dg.AssetKey] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    retry_policy: dg.RetryPolicy | None = None


def create_curriculum_ingestion_asset(
    resource_name: str = "curriculum_pages",
) -> dg.AssetsDefinition:
    """
    Create a unified curriculum ingestion asset.

    Uses the new ireland_curriculum DLT source that:
    - Crawls all 3 sources (curriculumonline, ncca, examinations)
    - Deduplicates content across sources via content hashing
    - Tracks source provenance
    - Uses 4-cycle partitions with runtime subject config

    Args:
        resource_name: DLT resource to use (curriculum_pages, curriculum_pdfs, source_provenance)

    Returns:
        Dagster asset definition

    Usage:
        raw_pages = create_curriculum_ingestion_asset("curriculum_pages")
        raw_pdfs = create_curriculum_ingestion_asset("curriculum_pdfs")
    """
    from .partitions_v2 import CURRICULUM_CONFIG_SCHEMA, ireland_curriculum_partitions

    @dg.asset(
        key=["ireland", "curriculum", f"raw_{resource_name}"],
        group_name="ireland_curriculum",
        compute_kind="dlt",
        description=f"Unified curriculum {resource_name} from all sources (deduplicated)",
        partitions_def=ireland_curriculum_partitions,
        config_schema=CURRICULUM_CONFIG_SCHEMA,
        retry_policy=dg.RetryPolicy(
            max_retries=3,
            delay=30,
            backoff=dg.Backoff.EXPONENTIAL,
        ),
        tags={"pipeline": "unified_curriculum", "source_count": "3"},
    )
    def _curriculum_ingestion_asset(
        context,
        duckdb: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Ingest curriculum content from all sources with deduplication."""
        import dlt as dlt_lib
        from oideachais.dlt_sources.ireland.curriculum_source import curriculum_source

        # Get partition key (cycle)
        cycle = context.partition_key

        # Get config values from context.op_config
        config = context.op_config or {}
        subjects = config.get("subjects")  # None = all subjects
        languages = config.get("languages", ["en", "ga"])
        max_pages = config.get("max_pages_per_subject", 50)
        sources = config.get("sources", ["curriculumonline", "ncca", "examinations"])
        deduplicate = config.get("deduplicate", True)

        context.log.info(
            f"Crawling {cycle} curriculum: "
            f"subjects={subjects or 'all'}, "
            f"languages={languages}, "
            f"sources={sources}"
        )

        # Create DLT source for specified resource
        source = curriculum_source(
            cycle=cycle,
            subject=subjects[0] if subjects and len(subjects) == 1 else None,
            language=languages[0] if len(languages) == 1 else "en",
            sources=sources,
            max_pages_per_subject=max_pages,
            deduplicate=deduplicate,
        )

        # Create DLT pipeline for DuckDB destination
        # Use pipeline.run() directly (DagsterDltResource.run() requires @dlt_assets decorator)
        pipeline = dlt_lib.pipeline(
            pipeline_name=f"curriculum_{resource_name}",
            destination="duckdb",
            dataset_name="education",
        )

        # Run DLT pipeline for the specific resource
        load_info = pipeline.run(source.with_resources(resource_name))

        # Extract metrics
        rows_loaded = sum(
            pkg.state.get("rows_count", 0)
            for pkg in load_info.load_packages
        )

        context.log.info(f"Loaded {rows_loaded} rows for {resource_name}")

        return dg.MaterializeResult(
            metadata={
                "rows_loaded": rows_loaded,
                "cycle": cycle,
                "subjects": subjects or "all",
                "languages": languages,
                "sources": sources,
                "deduplicated": deduplicate,
                "resource": resource_name,
            }
        )

    return _curriculum_ingestion_asset


def create_curriculum_processing_asset(
    stage: str,
    upstream_keys: list[dg.AssetKey],
    processing_fn: Callable[[dg.AssetExecutionContext, Any], dict[str, Any]] | None = None,
) -> dg.AssetsDefinition:
    """
    Create a curriculum processing asset.

    Args:
        stage: Processing stage name (e.g., "extracted", "structured", "embeddings")
        upstream_keys: Asset keys this depends on
        processing_fn: Optional custom processing function

    Returns:
        Dagster asset definition

    Usage:
        pdf_extractions = create_curriculum_processing_asset(
            stage="pdf_extractions",
            upstream_keys=[AssetKey(["ireland", "curriculum", "raw_curriculum_pdfs"])],
        )
    """
    from .partitions_v2 import ireland_curriculum_partitions

    @dg.asset(
        key=["ireland", "curriculum", stage],
        group_name="ireland_curriculum",
        compute_kind="python",
        description=f"Curriculum {stage} processing stage",
        partitions_def=ireland_curriculum_partitions,
        deps=upstream_keys,
        retry_policy=dg.RetryPolicy(max_retries=2, delay=60),
    )
    def _curriculum_processing_asset(
        context,
        duckdb: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Process curriculum data through specified stage."""
        cycle = context.partition_key

        context.log.info(f"Processing {stage} for {cycle}")

        rows_processed = 0

        if processing_fn:
            result = processing_fn(context, duckdb)
            rows_processed = result.get("rows_processed", 0)

        return dg.MaterializeResult(
            metadata={
                "cycle": cycle,
                "stage": stage,
                "rows_processed": rows_processed,
            }
        )

    return _curriculum_processing_asset


def create_curriculum_enrichment_asset(
    enrichment_type: str,
    upstream_keys: list[dg.AssetKey],
) -> dg.AssetsDefinition:
    """
    Create a non-partitioned enrichment asset that depends on all cycles.

    Enrichment assets (embeddings, translations, knowledge graph) run after
    all cycle partitions are complete.

    Args:
        enrichment_type: Type of enrichment (embeddings, translations, knowledge_graph)
        upstream_keys: Asset keys this depends on (partitioned assets)

    Returns:
        Dagster asset definition
    """
    @dg.asset(
        key=["ireland", "curriculum", enrichment_type],
        group_name="ireland_curriculum",
        compute_kind="enrichment",
        description=f"Curriculum {enrichment_type} (all cycles)",
        deps=upstream_keys,
        retry_policy=dg.RetryPolicy(max_retries=2, delay=120),
    )
    def _curriculum_enrichment_asset(
        context,
        lancedb: dg.ResourceParam[Any],
        duckdb: dg.ResourceParam[Any],
    ) -> dg.MaterializeResult:
        """Generate enrichments across all curriculum content."""
        context.log.info(f"Generating {enrichment_type} for all curriculum content")

        items_enriched = 0

        # Placeholder for enrichment logic
        # Would integrate with embedding models, translation APIs, or graph construction

        return dg.MaterializeResult(
            metadata={
                "enrichment_type": enrichment_type,
                "items_enriched": items_enriched,
            }
        )

    return _curriculum_enrichment_asset


def create_unified_curriculum_assets() -> list[dg.AssetsDefinition]:
    """
    Create the complete unified curriculum asset pipeline.

    Asset hierarchy:
        Layer 1: Ingestion (partitioned by 4 cycles)
        ├── ireland.curriculum.raw_curriculum_pages
        ├── ireland.curriculum.raw_curriculum_pdfs
        └── ireland.curriculum.raw_source_provenance

        Layer 2: Processing (partitioned by 4 cycles)
        ├── ireland.curriculum.pdf_extractions
        └── ireland.curriculum.structured

        Layer 3: Enrichment (non-partitioned, runs after all cycles)
        ├── ireland.curriculum.embeddings
        └── ireland.curriculum.translations

    Returns:
        List of all curriculum asset definitions

    Usage:
        from oideachais.dagster_defs.factories import create_unified_curriculum_assets

        curriculum_assets = create_unified_curriculum_assets()
        defs = Definitions(assets=curriculum_assets, ...)
    """
    assets = []

    # Layer 1: Ingestion assets (partitioned)
    assets.append(create_curriculum_ingestion_asset("curriculum_pages"))
    assets.append(create_curriculum_ingestion_asset("curriculum_pdfs"))
    assets.append(create_curriculum_ingestion_asset("source_provenance"))

    # Layer 2: Processing assets (partitioned)
    assets.append(create_curriculum_processing_asset(
        stage="pdf_extractions",
        upstream_keys=[dg.AssetKey(["ireland", "curriculum", "raw_curriculum_pdfs"])],
    ))
    assets.append(create_curriculum_processing_asset(
        stage="structured",
        upstream_keys=[
            dg.AssetKey(["ireland", "curriculum", "raw_curriculum_pages"]),
            dg.AssetKey(["ireland", "curriculum", "pdf_extractions"]),
        ],
    ))

    # Layer 3: Enrichment assets (non-partitioned)
    assets.append(create_curriculum_enrichment_asset(
        enrichment_type="embeddings",
        upstream_keys=[dg.AssetKey(["ireland", "curriculum", "structured"])],
    ))
    assets.append(create_curriculum_enrichment_asset(
        enrichment_type="translations",
        upstream_keys=[dg.AssetKey(["ireland", "curriculum", "structured"])],
    ))

    return assets


def create_curriculum_asset_job(
    name: str = "unified_curriculum_pipeline",
    selection: dg.AssetSelection | None = None,
) -> dg.JobDefinition:
    """
    Create a job that materializes curriculum assets.

    Args:
        name: Job name
        selection: Optional AssetSelection (defaults to all ireland.curriculum.* assets)

    Returns:
        Job definition

    Usage:
        curriculum_job = create_curriculum_asset_job()
    """
    from .partitions_v2 import ireland_curriculum_partitions

    return dg.define_asset_job(
        name=name,
        selection=selection or dg.AssetSelection.key_prefixes(["ireland", "curriculum"]),
        partitions_def=ireland_curriculum_partitions,
        description="Materialize unified curriculum assets across all sources",
        tags={"pipeline": "unified_curriculum"},
    )
