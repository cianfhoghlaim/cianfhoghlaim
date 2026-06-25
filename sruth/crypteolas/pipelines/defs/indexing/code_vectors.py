"""
Code indexing asset - indexes code files into LanceDB vectors.

This asset reads code from cloned repositories and creates
vector embeddings for semantic code search.

Depends on: Repository cloning (code mode ingestion)
Outputs to: LanceDB code_embeddings table
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
        "description": "Code files indexed into LanceDB vectors",
        "storage": "LanceDB",
        "search_types": ["vector", "fts", "hybrid"],
    },
)
def code_vector_index(context: AssetExecutionContext) -> Output[dict[str, Any]]:
    """Index code files from repositories into LanceDB vectors.

    Reads code from cloned repositories, chunks it, generates embeddings,
    and stores in LanceDB for semantic search.

    Returns:
        Dictionary with indexing statistics
    """
    from cocoindex.flows.code_indexing import CodeIndexingFlow
    from cocoindex.config import CodeIndexingConfig

    lancedb = context.resources.lancedb
    config = load_repos_config()
    defaults = config.get("defaults", {})

    total_chunks = 0
    indexed_repos = []

    repos_dir = Path("./data/repos")

    for repo_key, repo_config in config.get("repositories", {}).items():
        modes = repo_config.get("modes", {})

        # Only index if code mode is enabled
        if not modes.get("code", False):
            continue

        owner = repo_config["owner"]
        repo = repo_config["repo"]
        code_config = repo_config.get("code_config", {})

        # Check if repo is cloned
        repo_path = repos_dir / owner / repo
        if not repo_path.exists():
            context.log.warning(f"Repository not cloned: {owner}/{repo}")
            continue

        context.log.info(f"Indexing code from {owner}/{repo}")

        # Build indexing configuration
        indexing_config = CodeIndexingConfig(
            repo_owner=owner,
            repo_name=repo,
            included_patterns=code_config.get(
                "included_patterns",
                defaults.get("included_patterns", ["*.py", "*.md"])
            ),
            excluded_patterns=code_config.get(
                "excluded_patterns",
                defaults.get("excluded_patterns", ["**/.*"])
            ),
            chunk_size=code_config.get("chunk_size", defaults.get("chunk_size", 1000)),
            min_chunk_size=defaults.get("min_chunk_size", 300),
            chunk_overlap=code_config.get("chunk_overlap", defaults.get("chunk_overlap", 300)),
            embedding_model=defaults.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
            lancedb_uri=lancedb.uri,
        )

        flow = CodeIndexingFlow(indexing_config)

        try:
            num_chunks = flow.index_directory(repo_path)
            total_chunks += num_chunks
            indexed_repos.append(f"{owner}/{repo}")
            context.log.info(f"Indexed {num_chunks} chunks from {owner}/{repo}")
        except Exception as e:
            context.log.error(f"Failed to index {owner}/{repo}: {e}")

    return Output(
        value={
            "total_chunks": total_chunks,
            "indexed_repos": indexed_repos,
            "lancedb_uri": lancedb.uri,
        },
        metadata={
            "chunks_indexed": MetadataValue.int(total_chunks),
            "repos_indexed": MetadataValue.int(len(indexed_repos)),
            "storage_path": MetadataValue.path(lancedb.uri),
        },
    )
