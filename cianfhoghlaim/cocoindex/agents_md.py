"""
AGENTS.md CocoIndex v1 App — the canonical AGENTS.md discovery surface.

Indexes the root `AGENTS.md` + the 5 per-area AGENTS.md files (oideachais,
meaisinfhoghlaim, tuatha, croilar, bonneagar) into a new `agents_md`
LanceDB table. Chunked at 2048 tokens with 256-token overlap; embedded
with BAAI/bge-m3 1024-dim. Companion Dagster asset: `agents_md_index`.

This is one of the 4 v1 Apps added in the
`2026-06-30-agent-platform-cluster-hermes-cocoindex` change. Brings
the v1 App count from 13 → 17.

Source: `localfs.walk_dir(include_patterns=["**/AGENTS.md"], depth=3)`
— only the per-area AGENTS.md files, not the 100+ nested `agents.md`
instances in `node_modules`.

Query helper: `await search_agents_md(query, area=None, limit=10)`.
"""
from __future__ import annotations

import datetime
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

from ._lifespan import (
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    shared_lifespan,
)

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb, localfs  # type: ignore[import-not-found]
    from cocoindex.resources.file import PatternFilePathMatcher  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]
    from cocoindex.ops.text import RecursiveSplitter  # type: ignore[import-not-found]

    if COCOINDEX_AVAILABLE:
        from ._lifespan import LANCE_DB  # type: ignore[assignment]
    else:
        LANCE_DB = None  # type: ignore[assignment]
except ImportError as e:
    logger.warning("agents_md_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    RecursiveSplitter = None  # type: ignore[assignment]
    LANCE_DB = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_TABLE = "agents_md"
CHUNK_SIZE = 2048
CHUNK_OVERLAP = 256
REFRESH_INTERVAL_SECS = 300  # 5 min

# Default source root: the monorepo root
DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "AGENTS_MD_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[2]),
    )
)

# The 6 canonical AGENTS.md files (root + 5 per-area)
CANONICAL_AREAS = ["oideachais", "meaisinfhoghlaim", "tuatha", "croilar", "bonneagar"]


# =============================================================================
# Data model
# =============================================================================


@dataclass
class AgentsMdRecord:
    """One row per 2048-token chunk of an AGENTS.md file."""

    id: str
    area: str  # "oideachais" | "meaisinfhoghlaim" | "tuatha" | "croilar" | "bonneagar" | "root"
    file_path: str
    chunk_index: int
    text: str
    routing_tables: str  # serialized JSON of the 4 markdown table blocks
    embedding: Annotated[list[float], "BAAI/bge-m3"]


# =============================================================================
# CocoIndex v1 App
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.App(shared_lifespan)  # type: ignore[misc]
    def agents_md_app(
        builder: coco.AppBuilder,  # type: ignore[valid-type]
    ) -> None:
        """Index the 6 AGENTS.md files into the agents_md table."""
        builder.set_dynamic_input_source(  # type: ignore[attr-defined]
            "files",
            localfs.walk_dir(  # type: ignore[union-attr]
                path=DEFAULT_REPO_ROOT,
                recursive=True,
                path_matcher=PatternFilePathMatcher(  # type: ignore[union-attr]
                    included_patterns=[
                        "AGENTS.md",
                        "**/oideachais/AGENTS.md",
                        "**/meaisinfhoghlaim/AGENTS.md",
                        "**/tuatha/AGENTS.md",
                        "**/croilar/AGENTS.md",
                        "**/bonneagar/AGENTS.md",
                    ],
                ),
                live=True,
                refresh_interval=datetime.timedelta(seconds=REFRESH_INTERVAL_SECS),
            ),
        )

        id_gen = IdGenerator()  # type: ignore[call-arg]
        splitter = RecursiveSplitter(  # type: ignore[call-arg]
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def parse_agents_md(file_path: str) -> AsyncIterator[AgentsMdRecord]:  # type: ignore[no-untyped-def,unused-ignore]
            """Parse the AGENTS.md file, extract the 4 routing tables, chunk."""
            content = pathlib.Path(file_path).read_text(encoding="utf-8")
            area = _detect_area(file_path)
            routing_tables = _extract_routing_tables(content)
            chunks = splitter.chunks(content)  # type: ignore[union-attr]
            for i, chunk in enumerate(chunks):
                yield AgentsMdRecord(
                    id=await id_gen.next_id(f"{area}::{i}::{chunk[:50]}"),  # type: ignore[union-attr]
                    area=area,
                    file_path=file_path,
                    chunk_index=i,
                    text=chunk,
                    routing_tables=routing_tables,
                    embedding=[],
                )

        @coco.index(  # type: ignore[misc]
            target=lancedb.mount_table_target(  # type: ignore[union-attr]
                LANCE_DB,  # type: ignore[arg-type]
                table_name=LANCEDB_TABLE,
                table_schema=AgentsMdRecord,
                primary_key="id",
            ),
        )
        async def index_chunks(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[AgentsMdRecord],
        ) -> AsyncIterator[AgentsMdRecord]:
            async for record in records:
                record.embedding = await _embed(record.text)  # type: ignore[attr-defined]
                yield record

    def _detect_area(file_path: str) -> str:  # type: ignore[no-untyped-def]
        """Detect which of the 6 canonical areas the AGENTS.md file belongs to."""
        p = pathlib.Path(file_path)
        if p.name == "AGENTS.md" and p.parent == DEFAULT_REPO_ROOT:
            return "root"
        for area in CANONICAL_AREAS:
            if p.name == "AGENTS.md" and area in p.parts:
                return area
        return "root"

    def _extract_routing_tables(content: str) -> str:  # type: ignore[no-untyped-def,return-any]
        """Extract the 4 routing-table blocks from the AGENTS.md file as JSON."""
        import json
        import re

        # The 4 routing tables are the markdown tables that follow the
        # "Where things live" / "Stack inventory" / "Priority quick reference"
        # sections. We extract them as a list of (heading, table_text) tuples.
        tables: list[dict[str, str]] = []
        current_heading = ""
        in_table = False
        current_table: list[str] = []
        for line in content.split("\n"):
            if line.startswith("#"):
                if current_table and current_heading:
                    tables.append({"heading": current_heading, "table": "\n".join(current_table)})
                    current_table = []
                current_heading = line.lstrip("#").strip()
                in_table = False
            elif line.startswith("|") and line.endswith("|"):
                in_table = True
                current_table.append(line)
            elif in_table and not line.strip():
                if current_table and current_heading:
                    tables.append({"heading": current_heading, "table": "\n".join(current_table)})
                    current_table = []
                in_table = False
        if current_table and current_heading:
            tables.append({"heading": current_heading, "table": "\n".join(current_table)})
        return json.dumps(tables)

    async def _embed(text: str) -> list[float]:  # type: ignore[no-untyped-def]
        from ._lifespan import EMBEDDER  # type: ignore[assignment]

        return await EMBEDDER.embed(text)  # type: ignore[union-attr]


# =============================================================================
# Query helpers (the public API)
# =============================================================================


async def search_agents_md(
    query: str,
    area: str | None = None,
    limit: int = 10,
) -> list[AgentsMdRecord]:
    """Search the agents_md LanceDB table for the top-N matches.

    Parameters
    ----------
    query : str
        The natural-language query (e.g. "how do I add a new
        Docker Compose stack").
    area : str | None
        Filter to one of the 6 canonical areas
        ("oideachais" | "meaisinfhoghlaim" | "tuatha" | "croilar"
        | "bonneagar" | "root"); default None = no filter.
    limit : int
        Number of results to return (default: 10).

    Returns
    -------
    list[AgentsMdRecord]
        Ranked matches, sorted by BGE-m3 cosine similarity.
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("search_agents_md: CocoIndex not available; returning empty list")
        return []

    from ._lifespan import EMBEDDER  # type: ignore[assignment]
    from ._lifespan import LANCE_DB as _LANCE_DB  # type: ignore[assignment]

    query_embedding = await EMBEDDER.embed(query)  # type: ignore[union-attr]

    where = ""
    if area is not None:
        where = f"area = '{area}'"

    results: list[AgentsMdRecord] = []
    async for record in _LANCE_DB.search(  # type: ignore[attr-defined]
        LANCEDB_TABLE,
        query_embedding=query_embedding,
        limit=limit,
        where=where,
    ):
        results.append(record)
    return results
