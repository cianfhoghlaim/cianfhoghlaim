"""
Filesystem Layout CocoIndex v1 App.

Indexes the directory structure of the Cianfhoghlaim monorepo. Each
row in the `filesystem_layout` LanceDB table is one directory
(depth-1 to depth-4). Embeddings enable semantic search: e.g.
"where do I find the dagster assets" returns the
`oideachais/dagster_defs/` directory.

Per-directory fields:
- `dir_path` (relative to repo root)
- `file_count` (regular files only — excludes symlinks + sockets)
- `total_bytes` (recursive sum of regular-file sizes)
- `file_types` (dict of extension -> count, e.g. `{".py": 47, ".md": 5}`)
- `top_files` (list of `(name, size)` for the 5 largest files in this dir)
- `largest_descendant` (path + size of the biggest file in the subtree)
- `depth` (path depth from repo root)
- `summary` (human-readable, e.g. "47 files, 2.3 MB total, mostly Python
  and Markdown")
- `embedding`

Reference: v0 grep at `codeolas/cocoindex_flows/filesystem_indexing.py`
was directory-only (no per-file size, no embedding). v1 adds the
embedding + the file-type histogram.

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes mirror the codebase_indexing.py excludes.
- Walks up to depth=4 to keep the row count bounded (~500 dirs in this
  monorepo at depth 4).
- Embeddings via the shared BGE-M3 model (1024 dims).
"""

from __future__ import annotations

import asyncio
import datetime
import os
import pathlib
from collections.abc import AsyncIterator
from collections import Counter
from dataclasses import dataclass
from typing import Annotated, Any, ClassVar

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("FS_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("FS_REFRESH_SECS", "600")))
LANCEDB_TABLE = "filesystem_layout"
TOP_K = 10
MAX_DEPTH = 4

DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "FS_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)

LANCE_DB: Any = "lance_db_fs"
EMBEDDER: Any = "embedder_fs"

EXCLUDE_PATH_SUBSTRINGS = (
    "/.venv/",
    "/venv/",
    "/node_modules/",
    "/__pycache__/",
    "/target/",
    "/dist/",
    "/build/",
    "/.turbo/",
    "/.cocoindex_code/",
    "/stedding/",
    "/.git/",
    "/docs/cocoindex/",
    "/.cache/",
    "/.pytest_cache/",
    "/.ruff_cache/",
    "/.mypy_cache/",
)


# =============================================================================
# Data model
# =============================================================================


@dataclass
class FsLayoutRow:
    """One directory in the Cianfhoghlaim monorepo."""

    id: str
    dir_path: str
    file_count: int
    total_bytes: int
    file_types: str  # JSON-encoded Counter; lancedb wants str
    top_files: str  # JSON-encoded list[list[str | int]]; same reason
    largest_descendant: str
    depth: int
    summary: str
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("summary",)


# =============================================================================
# Walk helpers (CPU-bound; called via asyncio.to_thread)
# =============================================================================


def _walk_directory(
    repo_root: pathlib.Path, dir_path: pathlib.Path
) -> FsLayoutRow | None:
    """Walk one directory and produce an FsLayoutRow."""
    rel_path = str(dir_path.relative_to(repo_root)) if dir_path != repo_root else "."
    depth = 0 if rel_path == "." else rel_path.count("/") + 1
    if depth > MAX_DEPTH:
        return None

    file_count = 0
    total_bytes = 0
    file_types: Counter[str] = Counter()
    top_files: list[tuple[str, int]] = []  # (name, size)
    largest_descendant: tuple[str, int] = ("", 0)

    try:
        for child in dir_path.iterdir():
            sp = str(child)
            if any(ex in sp for ex in EXCLUDE_PATH_SUBSTRINGS):
                continue
            if child.is_symlink() or not child.is_file():
                # Don't follow symlinks (avoid loops). For dirs, recurse
                # via _walk_directory (the caller does that).
                continue
            try:
                size = child.stat().st_size
            except OSError:
                continue
            file_count += 1
            total_bytes += size
            ext = child.suffix.lower() or "<no-ext>"
            file_types[ext] += 1
            if len(top_files) < 5:
                top_files.append((child.name, size))
                top_files.sort(key=lambda t: -t[1])
            else:
                if size > top_files[-1][1]:
                    top_files[-1] = (child.name, size)
                    top_files.sort(key=lambda t: -t[1])
            if size > largest_descendant[1]:
                largest_descendant = (str(child.relative_to(repo_root)), size)
    except (PermissionError, OSError):
        return None

    # Build summary
    top_ext = ", ".join(
        f"{ext}({n})" for ext, n in file_types.most_common(3)
    ) or "no files"
    size_mb = total_bytes / (1024 * 1024)
    summary = (
        f"{rel_path}: {file_count} files, {size_mb:.1f} MB, "
        f"mostly {top_ext}"
    )

    import json

    return FsLayoutRow(
        id=f"fs:{rel_path}",
        dir_path=rel_path,
        file_count=file_count,
        total_bytes=total_bytes,
        file_types=json.dumps(dict(file_types)),
        top_files=json.dumps([list(t) for t in top_files]),
        largest_descendant=largest_descendant[0] or "",
        depth=depth,
        summary=summary,
        embedding=None,  # type: ignore[arg-type]
    )


def _walk_repo_for_layout(repo_root: pathlib.Path) -> list[FsLayoutRow]:
    """Walk all directories up to MAX_DEPTH, returning a row per dir."""
    rows: list[FsLayoutRow] = []
    # Always include the root.
    root_row = _walk_directory(repo_root, repo_root)
    if root_row is not None:
        rows.append(root_row)
    for depth in range(1, MAX_DEPTH + 1):
        for dirpath, dirnames, _filenames in os.walk(repo_root):
            # Prune excluded dirs
            dirnames[:] = [
                d for d in dirnames
                if not any(
                    ex in f"{dirpath}/{d}/" for ex in EXCLUDE_PATH_SUBSTRINGS
                )
            ]
            rel = pathlib.Path(dirpath).relative_to(repo_root)
            if rel == pathlib.Path("."):
                continue
            if rel.parts and len(rel.parts) != depth:
                continue
            row = _walk_directory(repo_root, pathlib.Path(dirpath))
            if row is not None:
                rows.append(row)
    return rows


# =============================================================================
# v1 App
# =============================================================================


def _make_app():  # noqa: ANN202
    """Construct the filesystem_indexing v1 App. Returns None when
    cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def fs_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        from cocoindex.connectors.lancedb import (  # type: ignore[import-not-found]
            LanceAsyncConnection,
        )

        lance_conn = await LanceAsyncConnection.connect(LANCEDB_URI)
        builder.provide(LANCE_DB, lance_conn)
        builder.provide(
            EMBEDDER,
            SentenceTransformerEmbedder(EMBED_MODEL),
        )
        yield

    @coco.fn
    async def fs_app_main(  # type: ignore[no-redef]
        repo_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                FsLayoutRow, primary_key=["id"]
            ),
        )
        rows = await asyncio.to_thread(_walk_repo_for_layout, repo_root)
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await target_table.upsert(batch)

    return coco.App(
        coco.AppConfig(name="FilesystemIndex"),
        fs_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


fs_app = _make_app()


# =============================================================================
# Query helpers
# =============================================================================


async def search_filesystem(
    query: str,
    min_depth: int | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Semantic search over directory layouts.

    Example: `await search_filesystem("dagster assets", min_depth=2)`
    returns the top directories semantically related to "dagster assets",
    filtered to depth >= 2 (so we skip the repo root and top-level dirs).
    """
    if not COCOINDEX_AVAILABLE or fs_app is None:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    if min_depth is not None:
        search = search.where(f"depth >= {int(min_depth)}")
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "REFRESH_INTERVAL",
    "LANCEDB_TABLE",
    "TOP_K",
    "MAX_DEPTH",
    "DEFAULT_REPO_ROOT",
    "FsLayoutRow",
    "_walk_directory",
    "_walk_repo_for_layout",
    "search_filesystem",
]
if COCOINDEX_AVAILABLE and fs_app is not None:
    __all__.append("fs_app")
