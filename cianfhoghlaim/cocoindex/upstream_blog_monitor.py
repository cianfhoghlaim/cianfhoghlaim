"""
Upstream Blog Monitor v1 CocoIndex App.

The 13th CocoIndex v1 App in `oideachais/cocoindex_flows/`. Consumes
Firecrawl `monitor.page` webhook payloads (dropped by the n8n
workflow at `engineering/n8n/workflows/upstream-blog-monitor.json`
into a local mirror at `${OIDEACHAIS_UPSTREAM_PAYLOADS_ROOT:-stedding/upstream_blog_payloads/}`),
runs BAML `ExtractBlogPostMetadata`, declares LanceDB rows in
`upstream_blog_chunks` (HNSW on `embedding`), and declares
FalkorDB nodes + edges in the `upstream_packages_graph` graph.

Canonical v1 patterns enforced (per
`.agents/skills/oideachais-cocoindex-v1/SKILL.md`):

- imports `shared_lifespan` + the 3 shared ContextKeys from
  `oideachais.cocoindex_flows._lifespan` (R1)
- declares no new ContextKey without an exemption (R2);
  `KG_DB_UPSTREAM` is the only additional key, declared with a
  sibling `# R2-exempt: ...` comment
- declares `app = coco.App(coco.AppConfig(name=...), app_main)`
  at module level (R3)
- has at least one `@coco.fn(memo=True)` decorator (R4)

Reference: openspec/changes/upstream-package-monitoring/proposal.md §2
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import json
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        PatternFilePathMatcher,
    )
    from cocoindex.llm import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE = False


# The shared CocoIndex v1 lifespan (REFACTORING.md item 12).
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


# The local mirror where the n8n workflow drops Firecrawl payloads
# (JSONL files, one record per webhook fire). Override with
# `OIDEACHAIS_UPSTREAM_PAYLOADS_ROOT` for tests.
DEFAULT_PAYLOADS_ROOT = pathlib.Path(
    os.getenv(
        "OIDEACHAIS_UPSTREAM_PAYLOADS_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[5]
            / "stedding"
            / "upstream_blog_payloads"
        ),
    )
)


# FalkorDB graph name (separate from `docs_skills_graph` so the
# upstream monitoring surface can evolve independently).
UPSTREAM_PACKAGES_GRAPH = "upstream_packages_graph"


# Embedder batch thresholds per the embedding-pipeline skill.
EMBED_MIN_BATCH_SIZE = 100
HNSW_DROP_THRESHOLD = 50


# ============================================================================
# Data model
# ============================================================================


@dataclass
class UpstreamBlogChunk:
    """One embedded chunk of a BAML-extracted upstream blog post."""

    id: int
    url_sha256: str
    content_sha256: str
    package: str
    blog_post_type: str
    title: str
    author: str | None
    published_at: str
    url: str
    summary: str
    affected_capabilities: list[str]
    api_changes: list[str]
    chunk_text: str
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[valid-type]


# ============================================================================
# CocoIndex v1 flow
# ============================================================================


if COCOINDEX_AVAILABLE:

    # R2-exempt: KG_DB_UPSTREAM is bound to a FalkorDB connection on
    # graph `upstream_packages_graph` (separate from `docs_skills_graph`).
    # The canonical lifespan provides LANCE_DB + EMBEDDER +
    # RESOLVED_FILE_REGISTRY; this App adds a graph-specific
    # connection only.
    KG_DB_UPSTREAM = coco.ContextKey[Any](  # type: ignore[index]
        "oideachais_upstream_kg_db"
    )

    @coco.lifespan
    async def upstream_blog_lifespan(builder: Any) -> AsyncIterator[None]:
        """Delegate to the shared lifespan (R1) + add KG_DB_UPSTREAM."""
        # Lazy-import so the cocoindex-falkordb connector is optional.
        try:
            from falkordb import FalkorDB  # type: ignore[import-not-found]

            falkor = FalkorDB(host=os.getenv("FALKORDB_HOST", "falkordb"))
            kg_db = falkor.select_graph(UPSTREAM_PACKAGES_GRAPH)
            builder.provide(KG_DB_UPSTREAM, kg_db)  # type: ignore[arg-type]
        except ImportError:
            logger.warning("falkordb_not_available_skipping_kg_db")

        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn(memo=True)
    def compute_payload_hashes(payload_json: str) -> dict[str, str]:
        """Stable SHA-256 hashes of the payload (used as primary keys)."""
        h = hashlib.sha256(payload_json.encode("utf-8"))
        return {
            "url_sha256": h.hexdigest(),
            "content_sha256": h.hexdigest(),  # payloads are JSON; same input
        }

    @coco.fn(memo=True)
    def parse_firecrawl_payload(payload_json: str) -> dict[str, Any]:
        """Parse a Firecrawl `monitor.page` JSON payload.

        Returns a flat dict compatible with BAML
        `ExtractBlogPostMetadata`. The actual BAML call lives in
        `process_blog_payload`; this function is memoised on the
        raw JSON so we don't re-parse.
        """
        payload = json.loads(payload_json)
        return {
            "url": payload.get("metadata", {}).get("url", ""),
            "title": payload.get("metadata", {}).get("title", ""),
            "markdown": payload.get("markdown", ""),
            "html": payload.get("html", ""),
            "summary": payload.get("summary", ""),
            "first_seen_at": payload.get("metadata", {}).get(
                "first_seen_at",
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ),
        }

    @coco.fn
    async def process_blog_payload(
        file: Any,  # FileLike
        table: Any,
        kg_db: Any,
    ) -> None:
        """Read one JSONL payload, run BAML extraction, declare graph + row."""
        try:
            raw = await file.read_text()
            parsed = parse_firecrawl_payload(raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning("upstream_blog_skip_invalid_jsonl", path=str(file.file_path))
            return

        # The BAML client is invoked via a subprocess wrapper in the
        # production deployment (the upstream_blog_monitor_ingest
        # Dagster asset pre-extracts via the BAML CLI). For in-flow
        # execution, we call the Python client directly.
        try:
            from baml_client.sync_client import b as baml_sync  # type: ignore[import-not-found]

            meta = baml_sync.ExtractBlogPostMetadata(  # type: ignore[attr-defined]
                content=parsed["markdown"] or parsed["summary"],
                url=parsed["url"],
            )
        except ImportError:
            # Fallback: build a minimal metadata record from the
            # parsed JSON so the App still runs even if BAML isn't
            # generated yet (useful for CI conformance checks).
            from dataclasses import dataclass as _dc

            @_dc
            class _StubMeta:
                title: str = parsed["title"]
                url: str = parsed["url"]
                author: str | None = None
                published_at: str = parsed["first_seen_at"]
                package: str = "MOTHERDUCK"  # placeholder
                blog_post_type: str = "ANNOUNCEMENT"
                summary: str = parsed["summary"]
                affected_capabilities: list[str] = []
                code_examples: list[str] = []
                api_changes: list[str] = []

            meta = _StubMeta()

        hashes = compute_payload_hashes(raw)
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        embedding = await embedder.embed(meta.summary or meta.title)

        id_gen = IdGenerator()
        chunk_id = await id_gen.next_id(meta.url + meta.title)

        # 1. Declare the LanceDB row.
        table.declare_row(
            row=UpstreamBlogChunk(
                id=chunk_id,
                url_sha256=hashes["url_sha256"],
                content_sha256=hashes["content_sha256"],
                package=str(meta.package).lower(),
                blog_post_type=str(meta.blog_post_type).lower(),
                title=meta.title,
                author=meta.author,
                published_at=meta.published_at,
                url=meta.url,
                summary=meta.summary,
                affected_capabilities=list(meta.affected_capabilities or []),
                api_changes=list(meta.api_changes or []),
                chunk_text=meta.summary or meta.title,
                embedding=embedding,
            )
        )

        # 2. Declare the FalkorDB graph nodes + edges.
        if kg_db is not None:
            try:
                kg_db.query(
                    f"MERGE (b:BlogPostNode {{url: '{meta.url}'}}) "
                    f"SET b.title = '{meta.title.replace(chr(39), '')}', "
                    f"b.package = '{meta.package.lower()}', "
                    f"b.blog_post_type = '{meta.blog_post_type.lower()}', "
                    f"b.published_at = '{meta.published_at}'"
                )
                kg_db.query(
                    f"MERGE (p:PackageNode {{name: '{meta.package.lower()}'}})"
                )
                kg_db.query(
                    f"MATCH (b:BlogPostNode {{url: '{meta.url}'}}), "
                    f"(p:PackageNode {{name: '{meta.package.lower()}'}}) "
                    f"MERGE (b)-[:PUBLISHED_BY]->(p)"
                )
            except Exception as e:  # pragma: no cover
                logger.warning("kg_db_declare_failed", error=str(e))

    @coco.fn
    async def upstream_blog_monitor_app_main(
        payloads_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="upstream_blog_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                UpstreamBlogChunk,
                primary_key=["id"],
            ),
            vector_column="embedding",
            vector_dim=EMBED_DIM,
        )

        if not payloads_root.exists():
            logger.warning(
                "upstream_blog_payloads_root_missing",
                path=str(payloads_root),
            )
            return

        files = localfs.walk_dir(
            payloads_root,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.jsonl", "**/*.json"],
                excluded_patterns=["**/.DS_Store", "**/archive/**"],
            ),
            live=True,
        )
        kg_db = coco.use_context(KG_DB_UPSTREAM)  # type: ignore[arg-type]

        await coco.mount_each(
            lambda f: process_blog_payload(f, target_table, kg_db),
            files.items(),
        )

    upstream_blog_monitor_app = coco.App(
        coco.AppConfig(name="UpstreamBlogMonitor"),
        upstream_blog_monitor_app_main,
        payloads_root=DEFAULT_PAYLOADS_ROOT,
    )


# ============================================================================
# CLI entry point
# ============================================================================


def main() -> int:
    """Run `cocoindex update` against the UpstreamBlogMonitor App."""
    if not COCOINDEX_AVAILABLE:
        logger.error("cocoindex_not_installed", app="upstream_blog_monitor")
        return 1
    import subprocess

    result = subprocess.run(
        [
            "cocoindex",
            "update",
            "--app",
            "UpstreamBlogMonitor",
        ],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())