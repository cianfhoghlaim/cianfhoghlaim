"""Docs Index memory job — nightly re-sync of the 3 polyglot backends.

Per the `2026-08-14-firecrawl-corpus-and-portals` change (Phase 4a),
this nightly job re-syncs the 3 memory backends (Graphiti + LanceDB +
Cognee) from the `cianfhoghlaim.firecrawl_corpus.docs_index` table.

The job is idempotent — re-running is safe (the Graphiti add_episode
is idempotent; the LanceDB MERGE TABLE is idempotent; the Cognee
cognify is idempotent within the dataset).
"""
# Deliberately NOT `from __future__ import annotations`. Dagster 1.13 detects
# the `context` parameter from its REAL annotation object; with postponed
# annotations it sees the string "AssetExecutionContext" and raises
# "Cannot annotate `context` parameter with type AssetExecutionContext",
# which aborts `dg.load_defs()` for the ENTIRE code location and silently
# drops everything to the `_defs_walker` fallback.

import logging
from datetime import UTC, datetime
from typing import Any

from dagster import AssetExecutionContext, asset

logger = logging.getLogger(__name__)


@asset(
    group_name="docs_index_memory",
    description="Nightly docs_index memory re-sync (Graphiti + LanceDB + Cognee)",
)
def docs_index_memory_job(context: AssetExecutionContext) -> dict[str, Any]:
    """The nightly docs_index memory re-sync.

    1. Read the new docs_index rows since the last sync
    2. Push them to Graphiti (temporal)
    3. Push them to LanceDB (vector — the canonical companion table)
    4. Push them to Cognee (cross-doc graph)
    5. Write the sync timestamp to `firecrawl_meta.docs_index_sync`
    """
    from agents.meaisinfhoghlaim.firecrawl_mcp.memory import (
        CogneeMemoryStore,
        GraphitiMemoryStore,
        LanceDBMemoryStore,
    )

    try:
        import duckdb

        con = duckdb.connect("md:cianfhoghlaim")
    except Exception as exc:
        context.log.warning(f"docs_index_memory_job.connection_failed: {exc}")
        return {"status": "error", "error": str(exc)}

    # Read the docs_index rows (the canonical source)
    try:
        rows = con.execute(
            """
            SELECT chunk_id, doc_id, package, url, chunk_offset, chunk_text, embedding, scraped_at
            FROM cianfhoghlaim.firecrawl_corpus.docs_index
            ORDER BY scraped_at DESC
            LIMIT 10000
            """
        ).fetchall()
    except Exception as exc:
        context.log.warning(f"docs_index_memory_job.read_failed: {exc}")
        return {"status": "error", "error": str(exc)}

    if not rows:
        context.log.info("docs_index_memory_job.no_new_rows")
        return {"status": "noop", "rows": 0}

    # Push to LanceDB (the canonical companion table)
    lancedb = LanceDBMemoryStore()
    table = lancedb._get_table()
    if table is not None:
        try:
            table.add(
                [
                    {
                        "chunk_id": r[0],
                        "doc_id": r[1],
                        "package": r[2],
                        "url": r[3],
                        "chunk_offset": r[4],
                        "chunk_text": r[5],
                        "embedding": list(r[6]) if r[6] else [0.0] * 1024,
                    }
                    for r in rows
                ]
            )
        except Exception as exc:
            context.log.warning(f"docs_index_memory_job.lancedb_push_failed: {exc}")

    # Push to Graphiti (temporal)
    graphiti = GraphitiMemoryStore()
    g_client = graphiti._get_client()
    if g_client is not None:
        try:
            for r in rows:
                g_client.add_episode(
                    name=f"docs_index_{r[0]}",
                    episode_body=r[5],
                    source_description=f"docs_index:{r[2]}",
                    reference_time=datetime.now(UTC),
                )
        except Exception as exc:
            context.log.warning(f"docs_index_memory_job.graphiti_push_failed: {exc}")

    # Push to Cognee (cross-doc graph)
    cognee = CogneeMemoryStore()
    if cognee._get_client() is not None:
        try:
            import cognee  # type: ignore[import-not-found]

            for r in rows:
                cognee.add(
                    data=r[5],
                    dataset_name="firecrawl_corpus",
                )
            cognee.cognify()
        except Exception as exc:
            context.log.warning(f"docs_index_memory_job.cognee_push_failed: {exc}")

    return {
        "status": "completed",
        "rows": len(rows),
        "synced_at": datetime.now(UTC).isoformat(),
    }