"""
Processing assets for document indexing and knowledge graph construction.

- CocoIndex: Semantic chunking and vector indexing to LanceDB
- Cognee: Knowledge graph extraction to Memgraph
"""

from typing import Any

from dagster import (
    asset,
    AssetExecutionContext,
    AssetIn,
    Definitions,
    MetadataValue,
    Output,
)


@asset(
    group_name="processing",
    ins={
        "protocol_documentation": AssetIn(
            key="protocol_documentation",
            partition_mapping=None,  # All partitions
        ),
    },
)
def indexed_documents(
    context: AssetExecutionContext,
    protocol_documentation: dict[str, Any],
) -> Output[dict[str, Any]]:
    """Index scraped documents with CocoIndex."""
    from pipelines.indexers.cocoindex_flow import index_crypto_docs

    context.log.info("Running CocoIndex document indexing...")

    result = index_crypto_docs(
        source_type="duckdb",
        source_config={
            "db_path": "data/crypto_analytics.duckdb",
            "table_name": "firecrawl_crawl",
        },
        lancedb_uri="data/crypto_vectors",
    )

    return Output(
        value=result,
        metadata={
            "index_location": MetadataValue.path("data/crypto_vectors"),
        },
    )


@asset(
    group_name="processing",
    ins={
        "indexed_documents": AssetIn(),
    },
)
def knowledge_graph(
    context: AssetExecutionContext,
    indexed_documents: dict[str, Any],
) -> Output[dict[str, Any]]:
    """Build knowledge graph with Cognee."""
    from pipelines.knowledge.cognee_pipeline import sync_cognify_docs, load_from_duckdb

    context.log.info("Loading documents for Cognee processing...")
    documents = load_from_duckdb()

    context.log.info(f"Processing {len(documents)} documents through Cognee...")
    result = sync_cognify_docs(documents)

    return Output(
        value=result,
        metadata={
            "documents_processed": MetadataValue.int(len(documents)),
            "graph_backend": "memgraph",
        },
    )


# Export definitions for load_from_defs_folder
defs = Definitions(
    assets=[indexed_documents, knowledge_graph],
)
