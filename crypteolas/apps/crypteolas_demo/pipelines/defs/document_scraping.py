"""
Document scraping assets for crypto protocol documentation.

Uses Firecrawl to crawl and extract documentation from protocol websites.
"""

from typing import Any

from dagster import (
    asset,
    AssetExecutionContext,
    Definitions,
    MetadataValue,
    Output,
)

from pipelines.defs._partitions import protocol_partitions


@asset(
    group_name="document_scraping",
    partitions_def=protocol_partitions,
    metadata={
        "description": "Crypto protocol documentation scraped with Firecrawl",
    },
)
def protocol_documentation(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Scrape protocol documentation using Firecrawl."""
    from pipelines.scrapers.firecrawl_source import firecrawl_crawl, CRYPTO_DOC_SOURCES
    from pipelines.shared.duckdb_destination import create_pipeline

    protocol = context.partition_key

    if protocol not in CRYPTO_DOC_SOURCES:
        context.log.warning(f"Unknown protocol: {protocol}")
        return Output({"status": "skipped", "protocol": protocol})

    source = CRYPTO_DOC_SOURCES[protocol]
    options = source.get("crawl_options", {})

    context.log.info(f"Crawling {protocol}: {source['url']}")

    # Create pipeline
    pipeline, metadata = create_pipeline(
        pipeline_name=f"docs_{protocol}",
        dataset_name="crypto_docs",
    )

    # Run crawl
    crawl_resource = firecrawl_crawl(
        start_url=source["url"],
        limit=options.get("limit", 100),
        max_depth=options.get("maxDepth", 3),
    )

    load_info = pipeline.run(crawl_resource)

    return Output(
        value={
            "protocol": protocol,
            "url": source["url"],
            "load_info": str(load_info),
        },
        metadata={
            "protocol": protocol,
            "pages_crawled": MetadataValue.int(options.get("limit", 100)),
            "source_url": MetadataValue.url(source["url"]),
        },
    )


# Export definitions for load_from_defs_folder
defs = Definitions(
    assets=[protocol_documentation],
)
