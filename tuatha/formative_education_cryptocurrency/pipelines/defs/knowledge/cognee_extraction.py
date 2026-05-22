"""
Cognee entity extraction asset - builds knowledge graph in Memgraph.

This asset uses Cognee's ECL (Extract-Cognify-Load) pipeline to
extract entities from documents and build a knowledge graph.

Depends on: docs_graph_index
Uses: Cognee for LLM-powered entity resolution
Outputs to: Memgraph with resolved entities
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dagster import (
    asset,
    AssetExecutionContext,
    AssetIn,
    MetadataValue,
    Output,
)


def load_repos_config() -> dict[str, Any]:
    """Load repository configuration from repos.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


@asset(
    group_name="knowledge",
    ins={
        "docs_graph_index": AssetIn(),
    },
    required_resource_keys={"memgraph"},
    metadata={
        "description": "Cognee-processed knowledge graph",
        "storage": "Memgraph",
        "processing": "Cognee ECL pipeline",
    },
)
def cognee_knowledge_graph(
    context: AssetExecutionContext,
    docs_graph_index: dict[str, Any],
) -> Output[dict[str, Any]]:
    """Run Cognee cognification on documents.

    Uses Cognee's ECL pipeline to:
    1. Extract entities from documents
    2. Cognify - resolve and link entities
    3. Load into Memgraph knowledge graph

    Args:
        docs_graph_index: Output from docs_graph_index asset

    Returns:
        Dictionary with cognification statistics
    """
    import asyncio
    import duckdb

    config = load_repos_config()
    db_path = config.get("databases", {}).get("duckdb", {}).get(
        "path", "./data/github_intelligence.duckdb"
    )

    documents_processed = 0
    cognee_result = {}

    # Connect to DuckDB to get documents
    try:
        con = duckdb.connect(db_path, read_only=True)
    except Exception as e:
        context.log.warning(f"Could not connect to DuckDB: {e}")
        return Output(
            value={"documents_processed": 0, "status": "no_data"},
            metadata={"status": "no_data"},
        )

    # Find all crawl datasets
    try:
        schemas = con.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'docs_%'"
        ).fetchall()
    except Exception:
        schemas = []

    documents = []
    for (schema_name,) in schemas:
        try:
            docs = con.execute(f"""
                SELECT url, title, content
                FROM {schema_name}.pages
                WHERE content IS NOT NULL
                LIMIT 30
            """).fetchall()

            for url, title, content in docs:
                documents.append({
                    "url": url,
                    "title": title or "",
                    "content": content,
                    "source": schema_name,
                })
        except Exception as e:
            context.log.warning(f"Could not read {schema_name}.pages: {e}")

    con.close()

    if not documents:
        context.log.info("No documents to process")
        return Output(
            value={"documents_processed": 0, "status": "no_documents"},
            metadata={"status": "no_documents"},
        )

    # Process with Cognee
    try:
        from cognee.processor import CogneeMemgraphProcessor

        processor = CogneeMemgraphProcessor(dataset_name="codeolas_knowledge")

        async def run_cognee():
            nonlocal documents_processed, cognee_result

            await processor.process_documents(documents)
            documents_processed = len(documents)
            cognee_result = processor.get_graph_stats()

        asyncio.run(run_cognee())
        processor.close()

    except ImportError:
        context.log.warning("Cognee not available, using fallback extraction")
        # Fallback to simple entity linking without Cognee
        memgraph = context.resources.memgraph
        driver = memgraph.get_driver()

        with driver.session() as session:
            for doc in documents:
                # Simple keyword extraction
                words = doc["content"].split()
                keywords = [w for w in words if len(w) > 5 and w.isalpha()][:10]

                for keyword in keywords:
                    session.run(
                        """
                        MERGE (e:Entity {value: $keyword})
                        SET e.type = 'KEYWORD'
                        WITH e
                        MATCH (d:Document {url: $url})
                        MERGE (d)-[:MENTIONS]->(e)
                        """,
                        keyword=keyword.lower(),
                        url=doc["url"],
                    )

                documents_processed += 1

        driver.close()
        cognee_result = {"method": "fallback_keywords"}

    except Exception as e:
        context.log.error(f"Cognee processing failed: {e}")
        return Output(
            value={"documents_processed": 0, "error": str(e)},
            metadata={"status": "error"},
        )

    return Output(
        value={
            "documents_processed": documents_processed,
            "graph_stats": cognee_result,
        },
        metadata={
            "documents_processed": MetadataValue.int(documents_processed),
            "cognee_dataset": "codeolas_knowledge",
            "graph_backend": "memgraph",
        },
    )
