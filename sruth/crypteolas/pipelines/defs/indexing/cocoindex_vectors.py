"""
CocoIndex integration for semantic code search.

This module provides assets for indexing code using CocoIndex
for semantic search across repositories.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dagster import (
    asset,
    AssetExecutionContext,
    Config,
    Output,
    MetadataValue,
    AssetIn,
)


class CocoIndexConfig(Config):
    """Configuration for CocoIndex integration."""
    index_name: str = "codeolas"
    embedding_model: str = "bge-m3"
    chunk_size: int = 512
    chunk_overlap: int = 64
    languages: list[str] = ["python", "typescript", "rust", "go"]


@asset(
    group_name="indexing",
    description="Create CocoIndex flow for code embedding",
)
def cocoindex_flow_definition(
    context: AssetExecutionContext,
    config: CocoIndexConfig,
) -> Output[dict]:
    """Create CocoIndex flow definition for code indexing."""
    # CocoIndex flow definition
    # In production, this would create a CocoIndex Flow

    flow_config = {
        "name": config.index_name,
        "description": "Semantic code search index for codeolas",
        "embedding_model": config.embedding_model,
        "chunk_config": {
            "size": config.chunk_size,
            "overlap": config.chunk_overlap,
        },
        "supported_languages": config.languages,
        "pipeline_stages": [
            {
                "name": "file_discovery",
                "type": "source",
                "config": {
                    "patterns": ["**/*.py", "**/*.ts", "**/*.rs", "**/*.go"],
                    "exclude": ["**/node_modules/**", "**/.git/**", "**/target/**"],
                },
            },
            {
                "name": "code_chunking",
                "type": "transform",
                "config": {
                    "strategy": "ast_aware",  # Use AST for smart chunking
                    "preserve_context": True,
                    "include_docstrings": True,
                },
            },
            {
                "name": "embedding",
                "type": "transform",
                "config": {
                    "model": config.embedding_model,
                    "batch_size": 32,
                },
            },
            {
                "name": "vector_store",
                "type": "sink",
                "config": {
                    "backend": "lancedb",
                    "table_name": f"{config.index_name}_vectors",
                },
            },
        ],
    }

    context.log.info(f"Created CocoIndex flow: {config.index_name}")

    return Output(
        flow_config,
        metadata={
            "index_name": MetadataValue.text(config.index_name),
            "embedding_model": MetadataValue.text(config.embedding_model),
            "stage_count": MetadataValue.int(len(flow_config["pipeline_stages"])),
        },
    )


@asset(
    group_name="indexing",
    description="Index repository code files",
    ins={"flow_definition": AssetIn("cocoindex_flow_definition")},
)
def indexed_code_files(
    context: AssetExecutionContext,
    config: CocoIndexConfig,
    flow_definition: dict,
    github_repos: list[dict],  # From github_api_assets
) -> Output[dict]:
    """Index code files from cloned repositories."""
    indexed_files = []
    total_chunks = 0

    for repo in github_repos:
        repo_path = repo.get("local_path")
        if not repo_path or not Path(repo_path).exists():
            context.log.warning(f"Repo path not found: {repo_path}")
            continue

        # Count files that would be indexed
        for lang in config.languages:
            patterns = {
                "python": "**/*.py",
                "typescript": "**/*.ts",
                "rust": "**/*.rs",
                "go": "**/*.go",
            }
            pattern = patterns.get(lang)
            if pattern:
                files = list(Path(repo_path).glob(pattern))
                for f in files:
                    indexed_files.append({
                        "repo": repo.get("full_name"),
                        "path": str(f.relative_to(repo_path)),
                        "language": lang,
                        "size_bytes": f.stat().st_size,
                    })
                    # Estimate chunks (rough approximation)
                    total_chunks += max(1, f.stat().st_size // (config.chunk_size * 4))

    context.log.info(f"Indexed {len(indexed_files)} files, ~{total_chunks} chunks")

    return Output(
        {
            "files": indexed_files,
            "total_files": len(indexed_files),
            "estimated_chunks": total_chunks,
            "flow_name": flow_definition["name"],
        },
        metadata={
            "total_files": MetadataValue.int(len(indexed_files)),
            "estimated_chunks": MetadataValue.int(total_chunks),
            "languages": MetadataValue.json(config.languages),
        },
    )


@asset(
    group_name="indexing",
    description="Build vector index from code chunks",
    deps=[indexed_code_files],
)
def code_vector_index(
    context: AssetExecutionContext,
    config: CocoIndexConfig,
    indexed_code_files: dict,
) -> Output[dict]:
    """Build vector index from indexed code files."""
    # In production, this would:
    # 1. Chunk files using AST-aware chunking
    # 2. Generate embeddings using bge-m3
    # 3. Store in LanceDB

    index_stats = {
        "index_name": config.index_name,
        "total_files": indexed_code_files["total_files"],
        "total_chunks": indexed_code_files["estimated_chunks"],
        "embedding_model": config.embedding_model,
        "vector_dimensions": 1024,  # bge-m3 default
        "status": "ready",
    }

    context.log.info(f"Built vector index: {config.index_name}")

    return Output(
        index_stats,
        metadata={
            "index_name": MetadataValue.text(config.index_name),
            "total_chunks": MetadataValue.int(indexed_code_files["estimated_chunks"]),
            "status": MetadataValue.text("ready"),
        },
    )


@asset(
    group_name="indexing",
    description="Create semantic search API endpoint",
    deps=[code_vector_index],
)
def semantic_search_endpoint(
    context: AssetExecutionContext,
    code_vector_index: dict,
) -> Output[dict]:
    """Create semantic search endpoint for code queries."""
    endpoint_config = {
        "index_name": code_vector_index["index_name"],
        "endpoint_path": f"/api/v1/search/{code_vector_index['index_name']}",
        "supported_queries": [
            "semantic_search",    # Natural language code search
            "similar_code",       # Find similar code snippets
            "function_lookup",    # Find functions by description
            "dependency_graph",   # Explore code dependencies
        ],
        "max_results": 20,
        "reranking": True,
        "status": "active",
    }

    context.log.info(f"Created search endpoint: {endpoint_config['endpoint_path']}")

    return Output(
        endpoint_config,
        metadata={
            "endpoint": MetadataValue.text(endpoint_config["endpoint_path"]),
            "query_types": MetadataValue.json(endpoint_config["supported_queries"]),
        },
    )


# Export assets
cocoindex_assets = [
    cocoindex_flow_definition,
    indexed_code_files,
    code_vector_index,
    semantic_search_endpoint,
]
