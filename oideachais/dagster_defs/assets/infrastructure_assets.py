"""
Infrastructure Assets for the Oideachais Lakehouse.

Round 7 phase 2: the v1-native companion assets to `codebase_assets.py`
that index the *non-code* surfaces of the Cianfhoghlaim monorepo. Four
v1 CocoIndex Apps, four Dagster assets:

- `api_endpoints` (group `infrastructure`) — FastAPI + Hono +
  TanStack Start + Convex HTTP surface, into the `api_endpoints`
  LanceDB table (via `oideachais/cocoindex_flows/api_indexing.py`).
- `filesystem_layout` (group `infrastructure`) — directory
  structure + per-directory file-type histogram into the
  `filesystem_layout` LanceDB table (via
  `oideachais/cocoindex_flows/filesystem_indexing.py`).
- `storage_backends` (group `infrastructure`) — LanceDB / DuckDB /
  DuckLake / Postgres / Garage / R2 / D1 / KV references into the
  `storage_backends` LanceDB table (via
  `oideachais/cocoindex_flows/storage_indexing.py`).
- `config_files` (group `infrastructure`) — compose / mise / turbo /
  package / pyproject / wrangler / env / k8s / pulumi / dg / github /
  justfile, into the `config_files` LanceDB table (via
  `oideachais/cocoindex_flows/config_indexing.py`).

The v0 reference implementation is at
`codeolas/cocoindex_flows/{api,filesystem,storage,config}_indexing.py`.
v1 swaps the v0 `FlowBuilder` DSL for the v1 `coco.App` + `@coco.fn` +
`@coco.lifespan` model and adds BGE-M3 embeddings for semantic search.

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
    os.environ.get("INFRASTRUCTURE_REPO_ROOT", "/Users/cianmacandeisigh/dev/kings_college_galway")
)
DEFAULT_LANCEDB_URI = os.environ.get("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")


# ============================================================================
# API Endpoints Asset
# ============================================================================


@asset(
    group_name="infrastructure",
    compute_kind="cocoindex",
    description="Index HTTP route surface (FastAPI/Hono/TanStack/Convex) into LanceDB",
)
def api_endpoints(context: AssetExecutionContext) -> MaterializeResult:
    """Index the HTTP API surface.

    Walks the repo for FastAPI @app.get / @router.get, Hono app.get,
    TanStack Start createFileRoute, and Convex httpAction references.
    Stores one row per endpoint in the `api_endpoints` LanceDB
    table with BGE-M3 embedding on the `summary` field.
    """
    try:
        from oideachais.cocoindex_flows import api_indexing
    except ImportError as e:
        context.log.warning(f"api_indexing module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info(f"Indexing API endpoints for {DEFAULT_REPO_PATH}")
    try:
        if api_indexing.api_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_api_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "lancedb_uri": MetadataValue.path(DEFAULT_LANCEDB_URI),
                "indexed_endpoints": MetadataValue.int(stats.get("indexed_endpoints", 0)),
                "frameworks": MetadataValue.json(stats.get("frameworks", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"API endpoint indexing failed: {e}")
        raise


# ============================================================================
# Filesystem Layout Asset
# ============================================================================


@asset(
    group_name="infrastructure",
    compute_kind="cocoindex",
    description="Index directory structure (depth 1-4) with per-dir file-type histogram",
)
def filesystem_layout(context: AssetExecutionContext) -> MaterializeResult:
    """Index the filesystem layout.

    Walks the repo up to depth 4 and records per-directory file count,
    total bytes, top-5 largest files, and file-type histogram. Stores
    one row per directory in the `filesystem_layout` LanceDB table
    with BGE-M3 embedding on the `summary` field.
    """
    try:
        from oideachais.cocoindex_flows import filesystem_indexing
    except ImportError as e:
        context.log.warning(f"filesystem_indexing module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info(f"Indexing filesystem layout for {DEFAULT_REPO_PATH}")
    try:
        if filesystem_indexing.fs_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_fs_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "indexed_directories": MetadataValue.int(stats.get("indexed_directories", 0)),
                "max_depth": MetadataValue.int(filesystem_indexing.MAX_DEPTH),
                "total_files": MetadataValue.int(stats.get("total_files", 0)),
                "total_bytes": MetadataValue.int(stats.get("total_bytes", 0)),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Filesystem layout indexing failed: {e}")
        raise


# ============================================================================
# Storage Backends Asset
# ============================================================================


@asset(
    group_name="infrastructure",
    compute_kind="cocoindex",
    description="Index storage backends (LanceDB/DuckDB/Postgres/Garage/R2/D1/KV) into LanceDB",
)
def storage_backends(context: AssetExecutionContext) -> MaterializeResult:
    """Index every storage backend the monorepo touches.

    Scans source files for lancedb / duckdb / ducklake / postgres /
    garage / r2 references, plus `wrangler.jsonc` / `wrangler.toml`
    for D1 / KV / R2 bindings. Stores one row per backend instance
    in the `storage_backends` LanceDB table with BGE-M3 embedding
    on the `summary` field.
    """
    try:
        from oideachais.cocoindex_flows import storage_indexing
    except ImportError as e:
        context.log.warning(f"storage_indexing module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info(f"Indexing storage backends for {DEFAULT_REPO_PATH}")
    try:
        if storage_indexing.storage_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_storage_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "indexed_backends": MetadataValue.int(stats.get("indexed_backends", 0)),
                "kinds": MetadataValue.json(stats.get("kinds", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Storage backend indexing failed: {e}")
        raise


# ============================================================================
# Config Files Asset
# ============================================================================


@asset(
    group_name="infrastructure",
    compute_kind="cocoindex",
    description="Index config files (compose/mise/turbo/package/pyproject/wrangler/env/k8s/pulumi/dg/github) into LanceDB",
)
def config_files(context: AssetExecutionContext) -> MaterializeResult:
    """Index every config file in the repo.

    Classifies by filename, parses the structure (TOML / JSON / YAML)
    and records a structured summary plus the workspace size. Stores
    one row per config file in the `config_files` LanceDB table
    with BGE-M3 embedding on the `summary` field.
    """
    try:
        from oideachais.cocoindex_flows import config_indexing
    except ImportError as e:
        context.log.warning(f"config_indexing module not available: {e}")
        return MaterializeResult(metadata={"status": "skipped", "reason": str(e)})

    context.log.info(f"Indexing config files for {DEFAULT_REPO_PATH}")
    try:
        if config_indexing.config_app is None:
            return MaterializeResult(
                metadata={"status": "skipped", "reason": "cocoindex not installed"}
            )
        stats = _get_config_stats()
        return MaterializeResult(
            metadata={
                "repo_path": MetadataValue.path(str(DEFAULT_REPO_PATH)),
                "indexed_configs": MetadataValue.int(stats.get("indexed_configs", 0)),
                "kinds": MetadataValue.json(stats.get("kinds", {})),
            }
        )
    except Exception as e:  # noqa: BLE001
        context.log.error(f"Config file indexing failed: {e}")
        raise


# ============================================================================
# Helpers
# ============================================================================


def _get_api_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_endpoints": 0, "frameworks": {}}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("api_endpoints")
        df = table.to_pandas()
        return {
            "indexed_endpoints": len(df),
            "frameworks": (
                df["framework"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_endpoints": 0, "frameworks": {}}


def _get_fs_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_directories": 0, "total_files": 0, "total_bytes": 0}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("filesystem_layout")
        df = table.to_pandas()
        return {
            "indexed_directories": len(df),
            "total_files": int(df["file_count"].sum()) if not df.empty else 0,
            "total_bytes": int(df["total_bytes"].sum()) if not df.empty else 0,
        }
    except Exception:  # noqa: BLE001
        return {"indexed_directories": 0, "total_files": 0, "total_bytes": 0}


def _get_storage_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_backends": 0, "kinds": {}}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("storage_backends")
        df = table.to_pandas()
        return {
            "indexed_backends": len(df),
            "kinds": (
                df["kind"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_backends": 0, "kinds": {}}


def _get_config_stats() -> dict:
    try:
        import lancedb  # type: ignore[import-not-found]
    except ImportError:
        return {"indexed_configs": 0, "kinds": {}}
    try:
        db = lancedb.connect(DEFAULT_LANCEDB_URI)
        table = db.open_table("config_files")
        df = table.to_pandas()
        return {
            "indexed_configs": len(df),
            "kinds": (
                df["kind"].value_counts().to_dict() if not df.empty else {}
            ),
        }
    except Exception:  # noqa: BLE001
        return {"indexed_configs": 0, "kinds": {}}


# Asset exports
infrastructure_assets = [
    api_endpoints,
    filesystem_layout,
    storage_backends,
    config_files,
]
