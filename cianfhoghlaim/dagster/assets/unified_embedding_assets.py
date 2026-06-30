"""
Unified Embedding Assets for the Oideachais Lakehouse.

Round 7 phase 3: the v1-native replacement for the v0 embedding
Dagster assets in `crypteolas/dagster_assets/unified_embedding_assets.py`
(when those existed). Two Dagster assets (group `embedding`):

- `unified_embeddings` — kicks
  `oideachais.cocoindex_flows.unified_embedding:unified_app` which
  reads from a DuckDB source (default: crypteolas DuckLake
  `crypteolas_catalog.docs.scraped_documents`) and writes to the
  `unified_embeddings` LanceDB table.
- `code_embeddings` — kicks
  `oideachais.cocoindex_flows.unified_embedding:code_app` which
  walks `crypteolas/storage/data/code/` (configurable via
  `UNIFIED_CODE_ROOT`) and writes to the `code_embeddings` LanceDB
  table.

Both Apps use BGE-M3 (1024 dims) for embedding. The v0 file used
the v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`); the
v1 port uses `@coco.fn` + `@coco.lifespan` + `lancedb.mount_table_target`.

Reference: openspec/changes/oideachais-unified-embedding-v1/proposal.md
"""

import os
from pathlib import Path

from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_LANCEDB_URI = os.environ.get("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")


# ============================================================================
# Unified Embeddings Asset
# ============================================================================


@asset(
    group_name="embedding",
    compute_kind="cocoindex",
    description="Embed markdown documents from any DuckDB source into LanceDB",
)
def unified_embeddings(context: AssetExecutionContext) -> MaterializeResult:
    """Embed markdown documents from a DuckDB source.

    Reads from the configurable DuckDB connection + query (default:
    `crypteolas_catalog.docs.scraped_documents`). Chunks each
    document with RecursiveSplitter (markdown) or a paragraph + char
    window fallback. Embeds each chunk with BGE-M3. Stores in the
    `unified_embeddings` LanceDB table.
    """
    try:
        from oideachais.cocoindex_flows import unified_embedding
    except ImportError as e:
        context.log.warning(f"unified_embedding module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info("Embedding unified documents from DuckDB")
    try:
        if unified_embedding.unified_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_unified_stats()
        return MaterializeResult(
            metadata={
                "lancedb_uri": MetadataValue.path(DEFAULT_LANCEDB_URI),
                "duckdb_connection": MetadataValue.path(
                    str(unified_embedding.DEFAULT_DUCKDB_CONNECTION)
                ),
                "indexed_chunks": MetadataValue.int(stats.get("indexed_chunks", 0)),
                "source_types": MetadataValue.json(stats.get("source_types", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Unified embedding failed: {e}")
        raise


# ============================================================================
# Code Embeddings Asset
# ============================================================================


@asset(
    group_name="embedding",
    compute_kind="cocoindex",
    description="Embed local code files into LanceDB with BGE-M3",
)
def code_embeddings(context: AssetExecutionContext) -> MaterializeResult:
    """Embed local code files.

    Walks the configured `UNIFIED_CODE_ROOT` (default:
    `crypteolas/storage/data/code/`) for `*.py`, `*.ts`, `*.tsx`,
    `*.js`, `*.jsx`, `*.rs`, `*.go`, `*.sol` files. Chunks with
    `RecursiveSplitter(detect_code_language)`. Embeds with BGE-M3.
    Stores in the `code_embeddings` LanceDB table.
    """
    try:
        from oideachais.cocoindex_flows import unified_embedding
    except ImportError as e:
        context.log.warning(f"unified_embedding module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info(f"Embedding code files from {unified_embedding.DEFAULT_CODE_ROOT}")
    try:
        if unified_embedding.code_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_code_stats()
        return MaterializeResult(
            metadata={
                "code_root": MetadataValue.path(
                    str(unified_embedding.DEFAULT_CODE_ROOT)
                ),
                "lancedb_uri": MetadataValue.path(DEFAULT_LANCEDB_URI),
                "indexed_chunks": MetadataValue.int(stats.get("indexed_chunks", 0)),
                "languages": MetadataValue.json(stats.get("languages", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Code embedding failed: {e}")
        raise


# ============================================================================
# Helpers
# ============================================================================


def _get_unified_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_chunks": 0, "source_types": {}}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("unified_embeddings")
        df = table.to_pandas()
        return {
            "indexed_chunks": len(df),
            "source_types": (
                df["source_type"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_chunks": 0, "source_types": {}}


def _get_code_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_chunks": 0, "languages": {}}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("code_embeddings")
        df = table.to_pandas()
        return {
            "indexed_chunks": len(df),
            "languages": (
                df["language"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_chunks": 0, "languages": {}}


# Asset exports
unified_embedding_assets = [unified_embeddings, code_embeddings]
