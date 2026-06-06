"""
Documentation graph indexing asset - extracts relationships into Memgraph.

This asset reads crawled documentation and extracts entities and
relationships for knowledge graph storage.

Depends on: docs_vector_index
Outputs to: Memgraph static knowledge graph
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
    group_name="indexing",
    ins={
        "docs_vector_index": AssetIn(),
    },
    required_resource_keys={"memgraph"},
    metadata={
        "description": "Documentation relationships in Memgraph",
        "storage": "Memgraph",
        "graph_type": "static_knowledge",
    },
)
def docs_graph_index(
    context: AssetExecutionContext,
    docs_vector_index: dict[str, Any],
) -> Output[dict[str, Any]]:
    """Extract relationships from docs and store in Memgraph.

    Uses entity extraction to identify concepts and relationships
    from documentation content.

    Args:
        docs_vector_index: Output from docs_vector_index asset

    Returns:
        Dictionary with graph statistics
    """
    import duckdb

    from cognee.entity_extraction import extract_entities_and_relationships

    memgraph = context.resources.memgraph
    driver = memgraph.get_driver()
    config = load_repos_config()

    # Get DuckDB path
    db_path = config.get("databases", {}).get("duckdb", {}).get(
        "path", "./data/github_intelligence.duckdb"
    )

    total_relationships = 0
    total_entities = 0
    documents_processed = 0

    # Connect to DuckDB
    try:
        con = duckdb.connect(db_path, read_only=True)
    except Exception as e:
        context.log.warning(f"Could not connect to DuckDB: {e}")
        driver.close()
        return Output(
            value={"total_relationships": 0, "total_entities": 0},
            metadata={"status": "no_data"},
        )

    # Find all crawl datasets
    try:
        schemas = con.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'docs_%'"
        ).fetchall()
    except Exception:
        schemas = []

    with driver.session() as session:
        for (schema_name,) in schemas:
            context.log.info(f"Extracting entities from {schema_name}")

            try:
                docs = con.execute(f"""
                    SELECT url, title, content
                    FROM {schema_name}.pages
                    WHERE content IS NOT NULL
                    LIMIT 50
                """).fetchall()
            except Exception as e:
                context.log.warning(f"Could not read {schema_name}.pages: {e}")
                continue

            for url, title, content in docs:
                documents_processed += 1

                # Create document node
                session.run(
                    """
                    MERGE (d:Document {url: $url})
                    SET d.title = $title, d.source_schema = $schema
                    """,
                    url=url,
                    title=title or "",
                    schema=schema_name,
                )

                # Extract entities and relationships
                try:
                    # Truncate content for extraction
                    result = extract_entities_and_relationships(content[:4000])

                    for entity in result.entities:
                        session.run(
                            """
                            MERGE (e:Entity {value: $value})
                            SET e.type = $type
                            """,
                            value=entity.value,
                            type=entity.type if hasattr(entity, 'type') else "UNKNOWN",
                        )

                        # Link entity to document
                        session.run(
                            """
                            MATCH (d:Document {url: $url})
                            MATCH (e:Entity {value: $entity})
                            MERGE (d)-[:MENTIONS]->(e)
                            """,
                            url=url,
                            entity=entity.value,
                        )
                        total_entities += 1

                    for rel in result.relationships:
                        session.run(
                            """
                            MERGE (s:Entity {value: $subject})
                            MERGE (o:Entity {value: $object})
                            MERGE (s)-[r:RELATIONSHIP {predicate: $predicate}]->(o)
                            """,
                            subject=rel.subject,
                            object=rel.object,
                            predicate=rel.predicate,
                        )
                        total_relationships += 1

                except Exception as e:
                    context.log.warning(f"Entity extraction failed for {url}: {e}")

    con.close()
    driver.close()

    return Output(
        value={
            "total_relationships": total_relationships,
            "total_entities": total_entities,
            "documents_processed": documents_processed,
        },
        metadata={
            "relationships_created": MetadataValue.int(total_relationships),
            "entities_created": MetadataValue.int(total_entities),
            "documents_processed": MetadataValue.int(documents_processed),
            "graph_backend": "memgraph",
        },
    )
