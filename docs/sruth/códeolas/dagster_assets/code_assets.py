"""
Dagster assets for Códeolas code analysis flow.

Assets:
- code_chunks: TreeSitter-chunked code indexed in LanceDB
- code_graph: File/function/class relationships in Memgraph
- architecture_docs: Daily .arch.md generation

Based on patterns from bonneagar/examples and dlt_github.
"""

import logging
import os
from pathlib import Path
from typing import Any

from dagster import (
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    asset,
)

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_REPO_PATH = os.getenv(
    "CODEOLAS_REPO_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent)
)
DEFAULT_LANCEDB_URI = os.getenv("LANCEDB_URI", "./storage/data/lancedb")
DEFAULT_MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")


# =============================================================================
# Code Indexing Assets
# =============================================================================

@asset(
    group_name="codeolas",
    compute_kind="cocoindex",
    description="Index repository code chunks into LanceDB using TreeSitter + BGE-M3",
)
def code_chunks(context: AssetExecutionContext) -> MaterializeResult:
    """
    Run the CocoIndex repo embedding flow.

    This asset:
    1. Discovers source files in the repository
    2. Chunks them using TreeSitter (syntax-aware)
    3. Embeds chunks using BGE-M3
    4. Stores in LanceDB with FTS + vector indexes

    Critical constraints:
    - Embeddings batched (min 100)
    - HNSW index dropped for bulk inserts >50
    """
    try:
        from ..cocoindex_flows.repo_embedding import run_indexing
    except ImportError:
        context.log.warning("cocoindex not installed, skipping indexing")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": "cocoindex not installed",
            }
        )

    context.log.info(f"Starting code indexing for {DEFAULT_REPO_PATH}")

    try:
        run_indexing()
        context.log.info("Code indexing complete")

        # Get stats
        stats = _get_index_stats()

        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(DEFAULT_REPO_PATH),
                "lancedb_uri": MetadataValue.path(DEFAULT_LANCEDB_URI),
                "indexed_files": MetadataValue.int(stats.get("indexed_files", 0)),
                "indexed_chunks": MetadataValue.int(stats.get("indexed_chunks", 0)),
                "languages": MetadataValue.json(stats.get("languages", {})),
            }
        )

    except Exception as e:
        context.log.error(f"Code indexing failed: {e}")
        raise


@asset(
    group_name="codeolas",
    compute_kind="memgraph",
    description="Build code relationship graph in Memgraph",
    deps=[code_chunks],
)
def code_graph(context: AssetExecutionContext) -> MaterializeResult:
    """
    Build file/function/class relationship graph.

    This asset:
    1. Reads source files
    2. Extracts AST relationships using TreeSitter
    3. Creates nodes (File, Function, Class, Method)
    4. Creates edges (CONTAINS, IMPORTS, CALLS, EXTENDS)
    5. Stores in Memgraph for Cypher queries

    Depends on code_chunks to ensure files are already processed.
    """
    try:
        from ..cocoindex_flows.file_graph import (
            get_memgraph_client,
            extract_relationships_from_ast,
            GraphNode,
            GraphEdge,
        )
        from ..cocoindex_flows.transforms.treesitter_chunking import (
            detect_language,
            EXTENSION_TO_LANGUAGE,
        )
    except ImportError as e:
        context.log.warning(f"Dependencies not available: {e}")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": str(e),
            }
        )

    context.log.info(f"Building code graph for {DEFAULT_REPO_PATH}")

    # Get Memgraph client
    client = get_memgraph_client(DEFAULT_MEMGRAPH_URI)

    try:
        # Setup schema
        client.setup_schema()

        # Clear existing graph for fresh build
        client.clear_graph()

        # Process files
        repo_path = Path(DEFAULT_REPO_PATH)
        all_nodes: list[GraphNode] = []
        all_edges: list[GraphEdge] = []

        file_count = 0
        for ext, lang in EXTENSION_TO_LANGUAGE.items():
            for file_path in repo_path.rglob(f"*{ext}"):
                if _should_ignore(file_path, repo_path):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    rel_path = str(file_path.relative_to(repo_path))

                    nodes, edges = extract_relationships_from_ast(
                        content=content,
                        file_path=rel_path,
                        language=lang,
                    )

                    all_nodes.extend(nodes)
                    all_edges.extend(edges)
                    file_count += 1

                except Exception as e:
                    context.log.debug(f"Failed to process {file_path}: {e}")

        # Batch insert
        context.log.info(f"Inserting {len(all_nodes)} nodes and {len(all_edges)} edges")
        node_count = client.create_nodes_batch(all_nodes)
        edge_count = client.create_edges_batch(all_edges)

        # Get stats
        stats = client.get_stats()

        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(DEFAULT_REPO_PATH),
                "memgraph_uri": DEFAULT_MEMGRAPH_URI,
                "files_processed": MetadataValue.int(file_count),
                "nodes_created": MetadataValue.int(node_count),
                "edges_created": MetadataValue.int(edge_count),
                "graph_stats": MetadataValue.json(stats),
            }
        )

    except Exception as e:
        context.log.error(f"Code graph build failed: {e}")
        raise
    finally:
        client.close()


@asset(
    group_name="codeolas",
    compute_kind="generator",
    description="Generate .arch.md architecture documentation",
    deps=[code_chunks, code_graph],
)
def architecture_docs(context: AssetExecutionContext) -> MaterializeResult:
    """
    Generate architecture documentation.

    This asset:
    1. Analyzes repository structure
    2. Detects languages and key files
    3. Generates Mermaid diagrams
    4. Outputs .arch.md file

    Runs daily after code indexing and graph building.
    """
    import asyncio

    try:
        from ..generators.arch_generator import generate_arch_docs
    except ImportError as e:
        context.log.warning(f"Generator not available: {e}")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": str(e),
            }
        )

    context.log.info(f"Generating architecture docs for {DEFAULT_REPO_PATH}")

    try:
        # Run async generator
        output_path = asyncio.run(generate_arch_docs(
            repo_path=DEFAULT_REPO_PATH,
        ))

        context.log.info(f"Architecture docs saved to {output_path}")

        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(DEFAULT_REPO_PATH),
                "output_path": MetadataValue.path(output_path),
                "status": "success",
            }
        )

    except Exception as e:
        context.log.error(f"Architecture doc generation failed: {e}")
        raise


# =============================================================================
# Helper Functions
# =============================================================================

def _get_index_stats() -> dict[str, Any]:
    """Get LanceDB index statistics."""
    try:
        import lancedb
    except ImportError:
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}

    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("codeolas_code_chunks")
        df = table.to_pandas()

        return {
            "indexed_files": df["file_path"].nunique(),
            "indexed_chunks": len(df),
            "languages": df["language"].value_counts().to_dict(),
        }
    except Exception:
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}


def _should_ignore(path: Path, repo_path: Path) -> bool:
    """Check if a path should be ignored."""
    ignore_patterns = [
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        "target",
    ]

    try:
        parts = path.relative_to(repo_path).parts
        return any(p in ignore_patterns for p in parts)
    except ValueError:
        return True


# Export all assets
codeolas_assets = [code_chunks, code_graph, architecture_docs]
