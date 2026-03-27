"""
Graphiti temporal knowledge asset - builds temporal graph in FalkorDB.

This asset uses Graphiti to build a bi-temporal knowledge graph
that tracks how knowledge evolves over time.

Depends on: cognee_knowledge_graph
Uses: Graphiti for temporal episode tracking
Outputs to: FalkorDB with bi-temporal edges
"""

from __future__ import annotations

import os
from datetime import datetime
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
        "cognee_knowledge_graph": AssetIn(),
    },
    required_resource_keys={"falkordb"},
    metadata={
        "description": "Temporal knowledge graph with Graphiti",
        "storage": "FalkorDB",
        "temporal": "bi-temporal (valid_time, transaction_time)",
    },
)
def graphiti_temporal_graph(
    context: AssetExecutionContext,
    cognee_knowledge_graph: dict[str, Any],
) -> Output[dict[str, Any]]:
    """Build temporal knowledge graph with Graphiti.

    Creates episodes from documents with temporal metadata,
    enabling time-travel queries on the knowledge graph.

    Args:
        cognee_knowledge_graph: Output from cognee_knowledge_graph asset

    Returns:
        Dictionary with temporal graph statistics
    """
    import asyncio
    import duckdb

    config = load_repos_config()
    db_path = config.get("databases", {}).get("duckdb", {}).get(
        "path", "./data/github_intelligence.duckdb"
    )

    episodes_added = 0

    # Connect to DuckDB
    try:
        con = duckdb.connect(db_path, read_only=True)
    except Exception as e:
        context.log.warning(f"Could not connect to DuckDB: {e}")
        return Output(
            value={"episodes_added": 0, "status": "no_data"},
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
                SELECT url, title, content, crawled_at
                FROM {schema_name}.pages
                WHERE content IS NOT NULL
                ORDER BY crawled_at DESC
                LIMIT 50
            """).fetchall()

            for url, title, content, crawled_at in docs:
                documents.append({
                    "url": url,
                    "title": title or "",
                    "content": content,
                    "crawled_at": crawled_at,
                    "source": schema_name,
                })
        except Exception as e:
            context.log.warning(f"Could not read {schema_name}.pages: {e}")

    con.close()

    if not documents:
        context.log.info("No documents for temporal processing")
        return Output(
            value={"episodes_added": 0, "status": "no_documents"},
            metadata={"status": "no_documents"},
        )

    # Try to use Graphiti
    try:
        falkordb = context.resources.falkordb
        client = falkordb.get_graphiti_client()

        async def add_episodes():
            nonlocal episodes_added

            for doc in documents:
                # Parse timestamp
                if doc["crawled_at"]:
                    try:
                        ref_time = datetime.fromisoformat(str(doc["crawled_at"]))
                    except Exception:
                        ref_time = datetime.now()
                else:
                    ref_time = datetime.now()

                context.log.info(f"Adding episode: {doc['title']}")

                try:
                    from graphiti_core import EpisodeType

                    await client.add_episode(
                        name=f"doc_{hash(doc['url']) % 100000}",
                        episode_body=doc["content"][:5000],  # Truncate
                        source=EpisodeType.text,
                        source_description=doc["title"] or doc["url"],
                        reference_time=ref_time,
                    )
                    episodes_added += 1

                except Exception as e:
                    context.log.warning(f"Failed to add episode: {e}")

                if episodes_added >= 30:  # Limit for initial run
                    break

        asyncio.run(add_episodes())

    except ImportError:
        context.log.warning("Graphiti not available, using FalkorDB directly")

        # Fallback: Store temporal data directly in FalkorDB
        try:
            falkordb = context.resources.falkordb
            client = falkordb.get_raw_client()
            graph = client.select_graph("temporal_knowledge")

            for doc in documents[:30]:
                timestamp = doc["crawled_at"] or datetime.now().isoformat()

                # Create temporal document node
                query = """
                    CREATE (d:TemporalDocument {
                        url: $url,
                        title: $title,
                        valid_from: $timestamp,
                        transaction_time: $now
                    })
                """
                graph.query(
                    query,
                    params={
                        "url": doc["url"],
                        "title": doc["title"],
                        "timestamp": str(timestamp),
                        "now": datetime.now().isoformat(),
                    }
                )
                episodes_added += 1

        except Exception as e:
            context.log.error(f"FalkorDB fallback failed: {e}")

    except Exception as e:
        context.log.error(f"Graphiti processing failed: {e}")
        return Output(
            value={"episodes_added": 0, "error": str(e)},
            metadata={"status": "error"},
        )

    return Output(
        value={
            "episodes_added": episodes_added,
            "graph_backend": "falkordb",
        },
        metadata={
            "episodes_created": MetadataValue.int(episodes_added),
            "temporal_model": "bi-temporal",
            "backend": "FalkorDB",
        },
    )
