"""CocoIndex Assets for the Croílár Portfolio.

Wraps CocoIndex flows as Dagster assets.
Embeds artwork images and CV/teaching text, exports to LanceDB.

Assets:
    - artwork_embeddings: CLIP embeddings in LanceDB
    - artwork_search_index: Vector search index
"""

import os
from typing import Any

from dagster import (
    AssetExecutionContext,
    AssetKey,
    Config,
    In,
    MaterializeResult,
    OpExecutionContext,
    Out,
    asset,
    graph,
    op,
)


class CocoIndexConfig(Config):
    """Configuration for CocoIndex assets."""

    use_duckdb_source: bool = True
    duckdb_path: str = "./croilar.duckdb"
    lancedb_uri: str = "./lancedb_data"
    enable_captioning: bool = False
    vision_model: str = "qwen3-vl"


@asset(
    name="artwork_embeddings",
    group_name="embeddings",
    description="CLIP embeddings of artwork in LanceDB",
    deps=[AssetKey(["artwork_processing"])],
    compute_kind="cocoindex",
)
def artwork_embedding_asset(
    context: AssetExecutionContext,
    config: CocoIndexConfig,
) -> MaterializeResult:
    """Generate CLIP embeddings for artwork images.

    Reads artwork from DuckDB (DLT output) or local files,
    embeds with CLIP, and exports to LanceDB.
    """
    import cocoindex

    # Set environment variables for flow
    os.environ["DUCKDB_PATH"] = config.duckdb_path
    os.environ["LANCEDB_URI"] = config.lancedb_uri

    if config.enable_captioning:
        os.environ["ENABLE_ARTWORK_CAPTIONING"] = "1"
        os.environ["VISION_MODEL"] = config.vision_model

    # Initialize CocoIndex
    cocoindex.init()

    # Import and setup flow
    if config.use_duckdb_source:
        from cocoindex_flows.artwork_embedding import artwork_embedding_duckdb_flow as flow
    else:
        from cocoindex_flows.artwork_embedding import artwork_embedding_flow as flow

    context.log.info(f"Setting up CocoIndex flow: {flow.name}")
    flow.setup(report_to_stdout=True)

    # Run flow
    context.log.info("Running CocoIndex flow...")
    cocoindex.run_flows([flow])

    # Get stats
    stats = get_embedding_stats(config.lancedb_uri)

    return MaterializeResult(
        metadata={
            "lancedb_uri": config.lancedb_uri,
            "embedding_count": stats.get("count", 0),
            "table_name": "artwork_embeddings",
            "captioning_enabled": config.enable_captioning,
        }
    )


@asset(
    name="artwork_search_ready",
    group_name="embeddings",
    description="LanceDB vector index ready for search",
    deps=[AssetKey(["artwork_embeddings"])],
    compute_kind="lancedb",
)
def artwork_search_index_asset(
    context: AssetExecutionContext,
    config: CocoIndexConfig,
) -> MaterializeResult:
    """Create vector index for fast similarity search.

    Builds IVF-PQ index on artwork embeddings for
    efficient nearest neighbor search.
    """
    import lancedb

    db = lancedb.connect(config.lancedb_uri)
    table = db.open_table("artwork_embeddings")

    # Get current row count
    row_count = len(table)

    # Create index if we have enough data
    if row_count >= 256:
        context.log.info(f"Creating IVF-PQ index on {row_count} embeddings")
        table.create_index(
            metric="cosine",
            vector_column_name="embedding",
            index_type="IVF_PQ",
            num_partitions=16,
            num_sub_vectors=48,
            replace=True,
        )
        index_type = "IVF_PQ"
    else:
        context.log.info(f"Too few embeddings ({row_count}) for IVF-PQ, using flat index")
        index_type = "flat"

    return MaterializeResult(
        metadata={
            "index_type": index_type,
            "row_count": row_count,
            "table_name": "artwork_embeddings",
        }
    )


def get_embedding_stats(lancedb_uri: str) -> dict[str, Any]:
    """Get statistics about embeddings in LanceDB.

    Args:
        lancedb_uri: Path to LanceDB database

    Returns:
        Dictionary with count and other stats
    """
    try:
        import lancedb

        db = lancedb.connect(lancedb_uri)
        table = db.open_table("artwork_embeddings")

        return {
            "count": len(table),
            "columns": list(table.schema.names),
        }
    except Exception:
        return {"count": 0}


def run_cocoindex_flow(
    use_duckdb: bool = True,
    live_mode: bool = False,
) -> None:
    """Run CocoIndex flow directly (outside Dagster).

    Args:
        use_duckdb: Use DuckDB source
        live_mode: Run in live update mode
    """
    import cocoindex

    cocoindex.init()

    if use_duckdb:
        from cocoindex_flows.artwork_embedding import artwork_embedding_duckdb_flow as flow
    else:
        from cocoindex_flows.artwork_embedding import artwork_embedding_flow as flow

    flow.setup(report_to_stdout=True)

    if live_mode:
        with cocoindex.FlowLiveUpdater(flow) as updater:
            print("Running in live mode. Press Ctrl+C to stop.")
            updater.wait()
    else:
        cocoindex.run_flows([flow])


# Ops for more granular control


@op(
    name="setup_cocoindex",
    out=Out(description="CocoIndex initialized"),
)
def setup_cocoindex_op(context: OpExecutionContext) -> bool:
    """Initialize CocoIndex runtime."""
    import cocoindex

    cocoindex.init()
    context.log.info("CocoIndex initialized")
    return True


@op(
    name="run_embedding_flow",
    ins={"initialized": In(bool)},
    out=Out(description="Number of embeddings created"),
)
def run_embedding_flow_op(
    context: OpExecutionContext,
    initialized: bool,
    use_duckdb: bool = True,
) -> int:
    """Run the artwork embedding flow."""
    import cocoindex

    if use_duckdb:
        from cocoindex_flows.artwork_embedding import artwork_embedding_duckdb_flow as flow
    else:
        from cocoindex_flows.artwork_embedding import artwork_embedding_flow as flow

    flow.setup(report_to_stdout=True)
    cocoindex.run_flows([flow])

    # Return embedding count
    stats = get_embedding_stats(os.environ.get("LANCEDB_URI", "./lancedb_data"))
    return stats.get("count", 0)


@op(
    name="create_vector_index",
    ins={"embedding_count": In(int)},
)
def create_vector_index_op(
    context: OpExecutionContext,
    embedding_count: int,
) -> None:
    """Create vector index on embeddings."""
    import lancedb

    lancedb_uri = os.environ.get("LANCEDB_URI", "./lancedb_data")
    db = lancedb.connect(lancedb_uri)
    table = db.open_table("artwork_embeddings")

    if embedding_count >= 256:
        context.log.info(f"Creating IVF-PQ index on {embedding_count} embeddings")
        table.create_index(
            metric="cosine",
            vector_column_name="embedding",
            index_type="IVF_PQ",
            num_partitions=16,
            num_sub_vectors=48,
            replace=True,
        )
    else:
        context.log.info(f"Skipping index creation ({embedding_count} < 256)")


@graph
def embedding_graph():
    """Graph combining embedding operations."""
    initialized = setup_cocoindex_op()
    count = run_embedding_flow_op(initialized)
    create_vector_index_op(count)


# Create job from graph
embedding_job = embedding_graph.to_job(
    name="artwork_embedding_job",
    description="Run artwork embedding pipeline",
)
