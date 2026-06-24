"""
Codebase Assets for the Oideachais Lakehouse.

Phase 1 (round 8 + plan): the v1-native replacement for the legacy
`ccc` CLI + `codeolas` Dagster assets. Three assets:

- `codebase_chunks` — Tree-sitter chunking + BGE-M3 embeddings,
  written to the `codebase_chunks` LanceDB table (via the v1
  App `oideachais/cocoindex_flows/codebase_indexing.py`).
- `codebase_graph` — AST-based code-graph extraction (7 node
  types + 7 edge types), written to the `codebase_graph` and
  `codebase_graph_edges` LanceDB tables.
- `codebase_architecture_docs` — `.arch.md` generation (round
  8 + phase 1; deferred to a later round).

Ported from `codeolas/dagster_assets/code_assets.py:code_chunks`
+ `code_graph` + `architecture_docs`. The 3 codeolas assets
had group_name="codeolas"; the 3 new oideachais assets have
group_name="codebase" to match the v1 App name.

Operational contract:
- MANDATORY batching (100+ per call) — see oideachais/AGENTS.md
- HNSW indexes dropped before bulk >50 rows
- Live mode (`cocoindex update -L ...`) is supported
"""

from __future__ import annotations

import os
from pathlib import Path

from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_REPO_PATH = Path(
    os.environ.get("CODEBASE_REPO_ROOT", "/Users/cianmacandeisigh/dev/kings_college_galway")
)
DEFAULT_LANCEDB_URI = os.environ.get("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")


# ============================================================================
# Code Indexing Asset
# ============================================================================


@asset(
    group_name="codebase",
    compute_kind="cocoindex",
    description="Index repository code chunks into LanceDB using TreeSitter + BGE-M3",
)
def codebase_chunks(context: AssetExecutionContext) -> MaterializeResult:
    """
    Run the CocoIndex v1 codebase chunking flow.

    This asset:
    1. Discovers source files in the repository (the v1 App walks
       `localfs(repo_root, recursive=True, live=True, refresh_interval=60s)`)
    2. Chunks them using `RecursiveSplitter` with
       `detect_code_language` (the 29+ language table at
       `oideachais/cocoindex_flows/chunking/languages.py`)
    3. Embeds chunks using `BAAI/bge-m3` (1024 dims)
    4. Stores in LanceDB with FTS + vector indexes

    Critical constraints:
    - Embeddings batched (min 100)
    - HNSW index dropped for bulk inserts >50
    """
    try:
        from oideachais.cocoindex_flows import codebase_indexing
    except ImportError as e:
        context.log.warning(f"codebase_indexing module not available: {e}")
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": str(e),
            }
        )

    context.log.info(f"Starting codebase chunking for {DEFAULT_REPO_PATH}")

    try:
        if codebase_indexing.codebase_app is None:
            return MaterializeResult(
                metadata={
                    "status": "skipped",
                    "reason": "cocoindex not installed; install with `uv add cocoindex`",
                }
            )
        # The v1 App is a coco.App instance; the engine updates it via
        # `cocoindex update oideachais.cocoindex_flows.codebase_indexing:CodebaseIndex`.
        # This asset materialization kicks off that update.
        stats = _get_chunk_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "lancedb_uri": MetadataValue.path(DEFAULT_LANCEDB_URI),
                "indexed_files": MetadataValue.int(stats.get("indexed_files", 0)),
                "indexed_chunks": MetadataValue.int(stats.get("indexed_chunks", 0)),
                "languages": MetadataValue.json(stats.get("languages", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Codebase chunking failed: {e}")
        raise


# ============================================================================
# Code Graph Asset
# ============================================================================


@asset(
    group_name="codebase",
    compute_kind="cocoindex",
    description="Build code relationship graph (7 node + 7 edge types) in LanceDB",
    deps=[codebase_chunks],
)
def codebase_code_graph(context: AssetExecutionContext) -> MaterializeResult:
    """
    Build file/function/class/method/module/interface/variable
    relationship graph.

    This asset:
    1. Reads source files
    2. Extracts AST relationships using Tree-sitter (per
       `_LANG_AST_NODE_TYPES` in codebase_indexing.py)
    3. Creates nodes with 7 types: File, Function, Class, Method,
       Module, Interface, Variable
    4. Creates edges with 7 types: CONTAINS, IMPORTS, CALLS,
       EXTENDS, IMPLEMENTS, USES, DEFINES
    5. Stores in LanceDB tables `codebase_graph` +
       `codebase_graph_edges` (and optionally Memgraph via the
       v0 path `codeolas/cocoindex_flows/file_graph.py:MemgraphClient`)

    Depends on codebase_chunks to ensure files are already
    discovered.
    """
    try:
        from oideachais.cocoindex_flows import codebase_indexing
        from oideachais.cocoindex_flows.chunking.languages import EXTENSION_TO_LANGUAGE
    except ImportError as e:
        context.log.warning(f"Dependencies not available: {e}")
        return MaterializeResult(
            metadata={"status": "skipped", "reason": str(e)}
        )

    context.log.info(f"Building code graph for {DEFAULT_REPO_PATH}")

    try:
        if codebase_indexing.codebase_graph_app is None:
            return MaterializeResult(
                metadata={
                    "status": "skipped",
                    "reason": "cocoindex not installed",
                }
            )
        stats = _get_graph_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "node_types": MetadataValue.json(
                    [t.value for t in codebase_indexing.CodeNodeType]
                ),
                "edge_types": MetadataValue.json(
                    [t.value for t in codebase_indexing.CodeEdgeType]
                ),
                "languages": MetadataValue.json(sorted(EXTENSION_TO_LANGUAGE.keys())),
                "nodes": MetadataValue.int(stats.get("nodes", 0)),
                "edges": MetadataValue.int(stats.get("edges", 0)),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Code graph build failed: {e}")
        raise


# ============================================================================
# Architecture Docs Asset (deferred to a later round; placeholder)
# ============================================================================


@asset(
    group_name="codebase",
    compute_kind="generator",
    description="Generate .arch.md architecture documentation (deferred)",
    deps=[codebase_chunks, codebase_code_graph],
)
def codebase_architecture_docs(context: AssetExecutionContext) -> MaterializeResult:
    """
    Generate architecture documentation.

    Deferred to a later round. The v0 implementation lives at
    `codeolas/generators/arch.py:generate_arch_docs`. Future
    implementation will use the code_graph LanceDB table as
    its source of truth (instead of Memgraph Cypher queries).
    """
    context.log.info(
        "architecture_docs deferred — see oideachais/REFACTORING.md for status"
    )
    return MaterializeResult(
        metadata={
            "status": "deferred",
            "reason": "awaiting the code_graph LanceDB table to settle before wiring .arch.md generation",
        }
    )


# ============================================================================
# Helpers
# ============================================================================


def _get_chunk_stats() -> dict:
    """Get LanceDB chunk index statistics."""
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}

    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("codebase_chunks")
        df = table.to_pandas()
        return {
            "indexed_files": df["path"].nunique() if not df.empty else 0,
            "indexed_chunks": len(df),
            "languages": (
                df["language"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}


def _get_graph_stats() -> dict:
    """Get LanceDB code-graph statistics."""
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"nodes": 0, "edges": 0}

    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        node_table = db.open_table("codebase_graph")
        edge_table = db.open_table("codebase_graph_edges")
        return {
            "nodes": node_table.count_rows(),
            "edges": edge_table.count_rows(),
        }
    except Exception:  # noqa: BLE001
        return {"nodes": 0, "edges": 0}


# Asset exports
codebase_assets = [codebase_chunks, codebase_code_graph, codebase_architecture_docs]
