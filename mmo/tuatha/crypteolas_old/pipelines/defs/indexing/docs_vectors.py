"""
Documentation vector indexing asset - indexes docs into LanceDB.

This asset reads crawled documentation from DuckDB and creates
vector embeddings for semantic documentation search.

Depends on: Crawl assets (crawl mode ingestion)
Outputs to: LanceDB docs_embeddings table
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dagster import (
    asset,
    AssetExecutionContext,
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
    required_resource_keys={"lancedb", "embeddings"},
    metadata={
        "description": "Documentation indexed into LanceDB vectors",
        "storage": "LanceDB",
    },
)
def docs_vector_index(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Index documentation into LanceDB vectors.

    Reads crawled documentation from DuckDB, chunks it,
    generates embeddings, and stores in LanceDB.

    Returns:
        Dictionary with indexing statistics
    """
    import duckdb

    from cocoindex.flows.docs_indexing import DocsIndexingFlow
    from cocoindex.config import DocsIndexingConfig

    lancedb_resource = context.resources.lancedb
    embeddings_resource = context.resources.embeddings
    config = load_repos_config()
    defaults = config.get("defaults", {})

    # Get DuckDB path
    db_path = config.get("databases", {}).get("duckdb", {}).get(
        "path", "./data/github_intelligence.duckdb"
    )

    total_chunks = 0
    documents_processed = 0

    # Connect to DuckDB and read crawled docs
    try:
        con = duckdb.connect(db_path, read_only=True)
    except Exception as e:
        context.log.warning(f"Could not connect to DuckDB: {e}")
        return Output(
            value={"total_chunks": 0, "documents_processed": 0},
            metadata={"status": "no_data"},
        )

    # Find all crawl datasets
    try:
        schemas = con.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'docs_%'"
        ).fetchall()
    except Exception:
        schemas = []

    all_chunks = []

    for (schema_name,) in schemas:
        context.log.info(f"Processing docs from {schema_name}")

        try:
            docs = con.execute(f"""
                SELECT url, title, content, crawled_at
                FROM {schema_name}.pages
                WHERE content IS NOT NULL
            """).fetchall()
        except Exception as e:
            context.log.warning(f"Could not read {schema_name}.pages: {e}")
            continue

        for url, title, content, crawled_at in docs:
            documents_processed += 1

            # Chunk the content
            chunk_size = defaults.get("chunk_size", 1000)
            chunk_overlap = defaults.get("chunk_overlap", 300)

            # Simple chunking by paragraphs
            paragraphs = content.split("\n\n")
            current_chunk = ""

            for para in paragraphs:
                if len(current_chunk) + len(para) < chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk.strip():
                        all_chunks.append({
                            "url": url,
                            "title": title or "",
                            "text": current_chunk.strip(),
                            "source_schema": schema_name,
                        })
                    current_chunk = para + "\n\n"

            # Add remaining chunk
            if current_chunk.strip():
                all_chunks.append({
                    "url": url,
                    "title": title or "",
                    "text": current_chunk.strip(),
                    "source_schema": schema_name,
                })

    con.close()

    # Generate embeddings and store in LanceDB
    if all_chunks:
        context.log.info(f"Generating embeddings for {len(all_chunks)} chunks")

        texts = [c["text"] for c in all_chunks]
        embeddings = embeddings_resource.encode(texts)

        for chunk, embedding in zip(all_chunks, embeddings):
            chunk["embedding"] = embedding

        # Store in LanceDB
        db = lancedb_resource.get_connection()
        table_name = "docs_embeddings"

        try:
            if table_name in db.table_names():
                table = db.open_table(table_name)
                table.add(all_chunks)
            else:
                db.create_table(table_name, all_chunks)
            total_chunks = len(all_chunks)
        except Exception as e:
            context.log.error(f"Failed to store in LanceDB: {e}")

    return Output(
        value={
            "total_chunks": total_chunks,
            "documents_processed": documents_processed,
            "lancedb_uri": lancedb_resource.uri,
        },
        metadata={
            "chunks_indexed": MetadataValue.int(total_chunks),
            "documents_processed": MetadataValue.int(documents_processed),
            "storage_path": MetadataValue.path(lancedb_resource.uri),
        },
    )
