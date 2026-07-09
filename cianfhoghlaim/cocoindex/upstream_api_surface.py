"""
Upstream API Surface Monitor v1 CocoIndex App.

The 14th CocoIndex v1 App. Watches the canonical CocoIndex v1 docs
URLs + `llms-full.txt`, runs BAML `ExtractCocoIndexApiChange`,
declares LanceDB rows in `upstream_api_chunks` (HNSW on
`embedding`), and declares FalkorDB nodes + edges in the
`upstream_packages_graph` graph. The
`upstream_breaking_change_sensor` Dagster sensor polls the graph
and fires Slack alerts on `severity="BREAKING"`.

Canonical v1 patterns enforced (same as `upstream_blog_monitor.py`):

- imports `shared_lifespan` (R1)
- declares no new ContextKey without an exemption (R2);
  `KG_DB_UPSTREAM` (re-declared with `# R2-exempt: ...`) +
  `BAML_CLIENT_UPSTREAM` are the only additional keys
- declares `app = coco.App(...)` at module level (R3)
- has at least one `@coco.fn(memo=True)` decorator (R4)

Reference: openspec/changes/upstream-package-monitoring/proposal.md §4
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.llm import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE = False


from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    LANCEDB_URI,
    RESOLVED_FILE_REGISTRY,
    shared_lifespan,
)


# ============================================================================
# Configuration
# ============================================================================


# The 4 canonical CocoIndex v1 docs URLs (per the cocoindex_docs.yml
# Firecrawl monitor + the docs skill). Each is fetched on every
# refresh and the markdown body is processed.
WATCHED_DOCS_URLS: list[str] = [
    "https://cocoindex.io/docs/skill.md",
    "https://cocoindex.io/docs/getting_started/quickstart",
    "https://cocoindex.io/docs/advanced_topics/live_component",
    "https://cocoindex.io/docs/connectors/falkordb",
    "https://cocoindex.io/llms-full.txt",
]


# Local cache root for the fetched markdown (avoids hammering
# cocoindex.io on every run).
CACHE_ROOT = pathlib.Path(
    os.getenv(
        "OIDEACHAIS_COCOINDEX_DOCS_CACHE",
        str(
            pathlib.Path(__file__).resolve().parents[5]
            / "stedding"
            / "cocoindex_docs_cache"
        ),
    )
)


UPSTREAM_PACKAGES_GRAPH = "upstream_packages_graph"
EMBED_MIN_BATCH_SIZE = 100
HNSW_DROP_THRESHOLD = 50


# ============================================================================
# Data model
# ============================================================================


@dataclass
class ApiChangeChunk:
    """One embedded chunk of a BAML-extracted CocoIndex API change."""

    id: int
    symbol: str
    package: str
    severity: str  # BREAKING | MAJOR | MINOR | PATCH
    old_signature: str
    new_signature: str
    migration_steps: list[str]
    example_code: str | None
    changelog_url: str
    detected_at: str
    v1_app_affected: str | None
    chunk_text: str
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[valid-type]


# ============================================================================
# CocoIndex v1 flow
# ============================================================================


if COCOINDEX_AVAILABLE:

    # R2-exempt: KG_DB_UPSTREAM is bound to a FalkorDB connection on
    # graph `upstream_packages_graph`. Re-declared from
    # `upstream_blog_monitor.py` so this App's lifespan is
    # self-contained (each App declares all its ContextKeys).
    KG_DB_UPSTREAM = coco.ContextKey[Any](  # type: ignore[index]
        "oideachais_upstream_kg_db"
    )

    # R2-exempt: BAML_CLIENT_UPSTREAM is the pre-initialised BAML
    # client for the `upstream_monitoring.baml` schema. Pre-init
    # avoids per-call client construction overhead.
    BAML_CLIENT_UPSTREAM = coco.ContextKey[Any](  # type: ignore[index]
        "oideachais_baml_client_upstream"
    )

    @coco.lifespan
    async def upstream_api_lifespan(builder: Any) -> AsyncIterator[None]:
        """Delegate to the shared lifespan (R1) + add 2 extra keys."""
        # FalkorDB graph connection.
        try:
            from falkordb import FalkorDB  # type: ignore[import-not-found]

            falkor = FalkorDB(host=os.getenv("FALKORDB_HOST", "falkordb"))
            builder.provide(  # type: ignore[arg-type]
                KG_DB_UPSTREAM,
                falkor.select_graph(UPSTREAM_PACKAGES_GRAPH),
            )
        except ImportError:
            logger.warning("falkordb_not_available_skipping_kg_db")

        # BAML client.
        try:
            from baml_client.sync_client import b as baml_sync  # type: ignore[import-not-found]

            builder.provide(BAML_CLIENT_UPSTREAM, baml_sync)  # type: ignore[arg-type]
        except ImportError:
            logger.warning("baml_client_not_available_skipping_extraction")

        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn(memo=True)
    async def fetch_doc_markdown(url: str) -> str:
        """Fetch markdown from a watched URL, with local-file cache."""
        cache_path = CACHE_ROOT / (hashlib.sha256(url.encode()).hexdigest() + ".md")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
        try:
            import httpx  # type: ignore[import-not-found]

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, follow_redirects=True)
                resp.raise_for_status()
                text = resp.text
        except Exception as e:  # pragma: no cover
            logger.warning("doc_fetch_failed", url=url, error=str(e))
            return ""
        cache_path.write_text(text, encoding="utf-8")
        return str(text)

    @coco.fn(memo=True)
    def chunk_markdown(markdown: str, chunk_size: int = 2000) -> list[str]:
        """Naive chunker — splits on double newlines, returns non-empty chunks."""
        chunks: list[str] = []
        for block in markdown.split("\n\n"):
            block = block.strip()
            if block:
                chunks.append(block[:chunk_size])
        return chunks

    @coco.fn
    async def process_doc_chunk(
        chunk_text: str,
        url: str,
        table: Any,
        kg_db: Any,
    ) -> None:
        """Run BAML extraction on one chunk + declare graph + row."""
        baml_sync = coco.use_context(BAML_CLIENT_UPSTREAM)  # type: ignore[arg-type]
        if baml_sync is None:
            return

        try:
            change = baml_sync.ExtractCocoIndexApiChange(
                content=chunk_text,
                url=url,
            )
        except Exception as e:  # pragma: no cover
            logger.warning(
                "baml_extract_failed",
                url=url,
                error=str(e),
            )
            return

        if not change or not change.symbol:
            return

        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        embedding = await embedder.embed(change.new_signature or change.symbol)

        id_gen = IdGenerator()
        chunk_id = await id_gen.next_id(
            change.symbol + change.changelog_url + (change.detected_at or "")
        )

        # 1. LanceDB row.
        table.declare_row(
            row=ApiChangeChunk(
                id=chunk_id,
                symbol=change.symbol,
                package=str(change.package or "COCOINDEX").lower(),
                severity=str(change.severity or "MINOR").upper(),
                old_signature=change.old_signature or "",
                new_signature=change.new_signature or "",
                migration_steps=list(change.migration_steps or []),
                example_code=change.example_code,
                changelog_url=change.changelog_url or url,
                detected_at=change.detected_at
                or datetime.datetime.now(datetime.timezone.utc).isoformat(),
                v1_app_affected=change.v1_app_affected,
                chunk_text=chunk_text,
                embedding=embedding,
            )
        )

        # 2. FalkorDB nodes + edges.
        if kg_db is not None:
            try:
                # ApiChangeNode
                kg_db.query(
                    f"MERGE (a:ApiChangeNode {{symbol: '{change.symbol}', "
                    f"version: '{change.detected_at}'}}) "
                    f"SET a.severity = '{str(change.severity or 'MINOR').upper()}', "
                    f"a.old_signature = '{(change.old_signature or '').replace(chr(39), '')}', "
                    f"a.new_signature = '{(change.new_signature or '').replace(chr(39), '')}'"
                )
                if change.v1_app_affected:
                    kg_db.query(
                        f"MERGE (v:V1AppNode {{name: '{change.v1_app_affected}'}})"
                    )
                    kg_db.query(
                        f"MATCH (a:ApiChangeNode {{symbol: '{change.symbol}'}}), "
                        f"(v:V1AppNode {{name: '{change.v1_app_affected}'}}) "
                        f"MERGE (a)-[:AFFECTS_APP]->(v)"
                    )
            except Exception as e:  # pragma: no cover
                logger.warning("kg_db_declare_failed", error=str(e))

    @coco.fn
    async def upstream_api_surface_app_main(cache_root: pathlib.Path) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="upstream_api_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                ApiChangeChunk,
                primary_key=["id"],
            ),
            vector_column="embedding",
            vector_dim=EMBED_DIM,
        )
        target_table.declare_vector_index(column="embedding")
        kg_db = coco.use_context(KG_DB_UPSTREAM)  # type: ignore[arg-type]

        # In a real deployment, the Firecrawl `cocoindex_docs.yml`
        # monitor feeds a S3-cached mirror. For this App, we walk the
        # WATCHED_DOCS_URLS list and fetch each one through the
        # memoised `fetch_doc_markdown` helper.
        for url in WATCHED_DOCS_URLS:
            markdown = await fetch_doc_markdown(url)
            if not markdown:
                continue
            chunks = chunk_markdown(markdown)
            for chunk_text in chunks:
                await process_doc_chunk(chunk_text, url, target_table, kg_db)

    upstream_api_surface_app = coco.App(
        coco.AppConfig(name="UpstreamApiSurface"),
        upstream_api_surface_app_main,
        cache_root=CACHE_ROOT,
    )


# ============================================================================
# CLI entry point
# ============================================================================


def main() -> int:
    """Run `cocoindex update` against the UpstreamApiSurface App."""
    if not COCOINDEX_AVAILABLE:
        logger.error("cocoindex_not_installed", app="upstream_api_surface")
        return 1
    import subprocess

    result = subprocess.run(
        [
            "cocoindex",
            "update",
            "--app",
            "UpstreamApiSurface",
        ],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())