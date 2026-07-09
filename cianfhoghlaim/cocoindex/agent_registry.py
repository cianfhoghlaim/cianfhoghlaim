"""
Agent Registry CocoIndex v1 App — the canonical agent discovery surface.

Indexes the 7 `opencode.json` `agent.*` blocks + the 10 `mcp.*` server
blocks into a new `agent_registry` LanceDB table, embedded with
BAAI/bge-m3 1024-dim. Companion Dagster asset: `agent_registry_index`
in `cianfhoghlaim.orchestration/assets/agent_registry_assets.py`.

This is one of the 4 v1 Apps added in the
`2026-06-30-agent-platform-cluster-hermes-cocoindex` change (the other 3
are `agents_md`, `apple_photos_metadata`, `apple_photos_chunks`).
Brings the v1 App count from 13 → 17.

Source: `localfs.read_file("opencode.json")` (single file at repo root).
IdGenerator() for stable IDs across re-runs.

Query helper: `await search_agents(query, kind="agent", mode=None, limit=10)`.
"""
from __future__ import annotations

import json
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
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    if COCOINDEX_AVAILABLE:
        from ._lifespan import LANCE_DB  # type: ignore[assignment]
    else:
        LANCE_DB = None  # type: ignore[assignment]
except ImportError as e:
    logger.warning("agent_registry_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    LANCE_DB = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_TABLE = "agent_registry"

# Default source: the monorepo root opencode.json
DEFAULT_OPENCODE_JSON = pathlib.Path(
    os.getenv(
        "AGENT_REGISTRY_OPENCODE_JSON",
        str(pathlib.Path(__file__).resolve().parents[2] / "opencode.json"),
    )
)


# =============================================================================
# Data model
# =============================================================================


@dataclass
class AgentRecord:
    """One row per agent OR mcp server in the agent_registry table."""

    id: str
    kind: str  # "agent" | "mcp"
    name: str
    description: str
    model: str
    mode: str
    prompt: str  # for agents
    command: str  # for mcp servers
    tags: str  # comma-joined
    embedding: Annotated[list[float], "BAAI/bge-m3"]


# =============================================================================
# CocoIndex v1 App
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.App(shared_lifespan)  # type: ignore[misc]
    def agent_registry_app(
        builder: coco.AppBuilder,  # type: ignore[valid-type]
    ) -> None:
        """Index opencode.json agents + MCP servers into the agent_registry table."""
        builder.set_dynamic_input_source(  # type: ignore[attr-defined]
            "opencode", localfs.read_file(path=DEFAULT_OPENCODE_JSON)  # type: ignore[union-attr]
        )
        id_gen = IdGenerator()  # type: ignore[call-arg]
        builder.add_flow("agents", _agents_flow(id_gen))  # type: ignore[attr-defined]
        builder.add_flow("mcps", _mcps_flow(id_gen))  # type: ignore[attr-defined]

    def _agents_flow(id_gen: Any) -> Any:  # type: ignore[no-untyped-def]
        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def parse_agents(opencode_path: str) -> AsyncIterator[AgentRecord]:  # type: ignore[no-untyped-def,unused-ignore]
            """Parse the 7 `agent.*` blocks out of opencode.json."""
            content = pathlib.Path(opencode_path).read_text(encoding="utf-8")
            config = json.loads(content)
            agents = config.get("agent", {})
            for name, block in agents.items():
                yield AgentRecord(
                    id=await id_gen.next_id(f"agent::{name}"),  # type: ignore[union-attr]
                    kind="agent",
                    name=name,
                    description=block.get("description", ""),
                    model=block.get("model", ""),
                    mode=block.get("mode", ""),
                    prompt=block.get("prompt", ""),
                    command="",  # not applicable
                    tags=",".join(block.get("skill_filter", []) or []),
                    embedding=[],  # filled by the embedder
                )

        _agents_target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=AgentRecord,
            primary_key="id",
        )
        _agents_target.declare_vector_index(column="embedding")

        @coco.index(  # type: ignore[misc]
            target=_agents_target,
            refresh_interval=datetime.timedelta(seconds=300),  # 5 min
        )
        async def index_agents(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[AgentRecord],
        ) -> AsyncIterator[AgentRecord]:
            async for record in records:
                record.embedding = await _embed(  # type: ignore[attr-defined]
                    f"{record.description}\n{record.prompt}"
                )
                yield record

    def _mcps_flow(id_gen: Any) -> Any:  # type: ignore[no-untyped-def]
        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def parse_mcps(opencode_path: str) -> AsyncIterator[AgentRecord]:  # type: ignore[no-untyped-def,unused-ignore]
            """Parse the 10 `mcp.*` server blocks out of opencode.json."""
            content = pathlib.Path(opencode_path).read_text(encoding="utf-8")
            config = json.loads(content)
            mcps = config.get("mcp", {})
            for name, block in mcps.items():
                command = block.get("command")
                if isinstance(command, list):
                    command_str = " ".join(command)
                else:
                    command_str = str(command or block.get("url", ""))
                yield AgentRecord(
                    id=await id_gen.next_id(f"mcp::{name}"),  # type: ignore[union-attr]
                    kind="mcp",
                    name=name,
                    description=f"{name} MCP server",
                    model="",
                    mode="",
                    prompt="",
                    command=command_str,
                    tags=",".join(block.get("tags", []) or []),
                    embedding=[],
                )

        _mcps_target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=AgentRecord,
            primary_key="id",
        )
        _mcps_target.declare_vector_index(column="embedding")

        @coco.index(  # type: ignore[misc]
            target=_mcps_target,
            refresh_interval=datetime.timedelta(seconds=300),
        )
        async def index_mcps(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[AgentRecord],
        ) -> AsyncIterator[AgentRecord]:
            async for record in records:
                record.embedding = await _embed(record.command)  # type: ignore[attr-defined]
                yield record

    async def _embed(text: str) -> list[float]:  # type: ignore[no-untyped-def]
        from ._lifespan import EMBEDDER  # type: ignore[assignment]

        return await EMBEDDER.embed(text)  # type: ignore[union-attr]


# =============================================================================
# Query helpers (the public API)
# =============================================================================


async def search_agents(
    query: str,
    kind: str = "agent",
    mode: str | None = None,
    limit: int = 10,
) -> list[AgentRecord]:
    """Search the agent_registry LanceDB table for the top-N matches.

    Parameters
    ----------
    query : str
        The natural-language query (e.g. "which agent handles
        Dagster pipelines").
    kind : str
        Filter to "agent" or "mcp" (default: "agent").
    mode : str | None
        Filter to "primary" or "subagent" (default: None = no filter).
    limit : int
        Number of results to return (default: 10).

    Returns
    -------
    list[AgentRecord]
        Ranked matches, sorted by BGE-m3 cosine similarity.
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("search_agents: CocoIndex not available; returning empty list")
        return []

    from ._lifespan import EMBEDDER  # type: ignore[assignment]
    from ._lifespan import LANCE_DB as _LANCE_DB  # type: ignore[assignment]

    query_embedding = await EMBEDDER.embed(query)  # type: ignore[union-attr]

    # Build the filter
    where_clauses = [f"kind = '{kind}'"]
    if mode is not None:
        where_clauses.append(f"mode = '{mode}'")
    where = " AND ".join(where_clauses)

    # Search the table
    results: list[AgentRecord] = []
    async for record in _LANCE_DB.search(  # type: ignore[attr-defined]
        LANCEDB_TABLE,
        query_embedding=query_embedding,
        limit=limit,
        where=where,
    ):
        results.append(record)
    return results
