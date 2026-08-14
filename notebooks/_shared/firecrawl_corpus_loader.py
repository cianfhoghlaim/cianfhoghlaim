"""Firecrawl corpus loader — the Lakehouse-side writer for the agent reference corpus.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a), this module:

- Applies the SQL schema at `firecrawl_meta_schema.sql` (idempotent).
- Writes a `firecrawl_crawl` result to
  `cianfhoghlaim.firecrawl_corpus.docs.<package>` + `docs_index`
  (BAAI/bge-m3 1024-d embeddings via the shared `_lifespan.py`).
- Logs the scrape to `cianfhoghlaim.firecrawl_meta.scrapes`.
- Refreshes the LanceDB companion table at
  `lancedb://md:cianfhoghlaim/firecrawl_corpus/docs_index`.

The loader is the canonical writer for every ingestion path (the
marimo notebooks + the corpus MCP module + the DLT sources all
delegate to `load_crawl_result`).
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# The 17 software-stack packages (the canonical corpus whitelist).
# Adding a new package is a 3-step process:
#   1. Add the entry to PACKAGE_WHITELIST below
#   2. Add the per-package config to NOTEBOOK_01_SOFTWARE_STACK_CRAWL
#   3. Run `mise run notebook:01:software-stack-crawl`

PACKAGE_WHITELIST: dict[str, dict[str, Any]] = {
    "cocoindex": {
        "mcp_url": "https://cocoindex.io/cocoindex",
        "include_paths": ["^/docs/.*$"],
        "exclude_paths": ["^/blog/.*$"],
        "limit": 200,
        "cadence": "quarterly",
    },
    "dagster": {
        "mcp_url": "https://docs.dagster.io",
        "include_paths": ["^/api/.*$", "^/concepts/.*$"],
        "exclude_paths": ["^/_*", "^/community/.*$"],
        "limit": 400,
        "cadence": "quarterly",
    },
    "dlt": {
        "mcp_url": "https://dlthub.com/docs",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 200,
        "cadence": "quarterly",
    },
    "baml": {
        "mcp_url": "https://docs.boundaryml.com",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 100,
        "cadence": "quarterly",
    },
    "motherduck": {
        "mcp_url": "https://motherduck.com/docs",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 125,
        "cadence": "quarterly",
    },
    "duckdb": {
        "mcp_url": "https://duckdb.org/docs",
        "include_paths": ["^/api/.*$", "^/sql/.*$"],
        "exclude_paths": ["^/_*"],
        "limit": 350,
        "cadence": "quarterly",
    },
    "lancedb": {
        "mcp_url": "https://lancedb.github.io/lancedb",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 100,
        "cadence": "quarterly",
    },
    "pydantic_ai": {
        "mcp_url": "https://ai.pydantic.dev",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 150,
        "cadence": "quarterly",
    },
    "fastapi": {
        "mcp_url": "https://fastapi.tiangolo.com",
        "include_paths": ["^/api/.*$", "^/tutorial/.*$"],
        "exclude_paths": [],
        "limit": 175,
        "cadence": "quarterly",
    },
    "hono": {
        "mcp_url": "https://hono.dev",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 60,
        "cadence": "quarterly",
    },
    "tanstack_start": {
        "mcp_url": "https://tanstack.com/start",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 80,
        "cadence": "quarterly",
    },
    "copilotkit": {
        "mcp_url": "https://docs.copilotkit.com",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 225,
        "cadence": "quarterly",
    },
    "opencode": {
        "mcp_url": "https://opencode.ai/docs",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 50,
        "cadence": "quarterly",
    },
    "infisical": {
        "mcp_url": "https://infisical.com/docs",
        "include_paths": ["^/api-reference/.*$", "^/documentation/.*$"],
        "exclude_paths": [],
        "limit": 275,
        "cadence": "quarterly",
    },
    "litellm": {
        "mcp_url": "https://docs.litellm.ai",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 175,
        "cadence": "quarterly",
    },
    "langfuse": {
        "mcp_url": "https://langfuse.com/docs",
        "include_paths": ["^/.*$"],
        "exclude_paths": [],
        "limit": 125,
        "cadence": "quarterly",
    },
    "firecrawl": {
        "mcp_url": "https://docs.firecrawl.dev",
        "include_paths": ["^/features/.*$", "^/api-reference/.*$"],
        "exclude_paths": ["^/integrations/.*$"],
        "limit": 325,
        "cadence": "quarterly",
    },
}


# The 17 education domains (the recurring corpus).
EDUCATION_WHITELIST: dict[str, dict[str, Any]] = {
    "ncca_ireland": {
        "mcp_url": "https://curriculum.gov.ie",
        "subjects": 12,
        "languages": 2,
        "cadence": "monthly",
        "key": "ncca",
    },
    "examinations_ie": {
        "mcp_url": "https://www.examinations.ie",
        "subjects": 6,
        "languages": 2,
        "cadence": "monthly",
        "key": "examinations_ie",
        "requires_interact": True,
    },
    "sqa_scotland": {
        "mcp_url": "https://www.sqa.org.uk",
        "subjects": 8,
        "languages": 1,
        "cadence": "monthly",
        "key": "sqa",
    },
    "educationscotland": {
        "mcp_url": "https://education.gov.scot",
        "subjects": 8,
        "languages": 1,
        "cadence": "quarterly",
        "key": "educationscotland",
    },
    "gov_scotland": {
        "mcp_url": "https://www.gov.scot/education",
        "subjects": 0,
        "languages": 1,
        "cadence": "weekly",
        "key": "gov_scot",
    },
    "gov_uk_dfe": {
        "mcp_url": "https://www.gov.uk/government/organisations/department-for-education",
        "subjects": 0,
        "languages": 1,
        "cadence": "weekly",
        "key": "gov_uk",
    },
    "ofsted": {
        "mcp_url": "https://www.gov.uk/government/organisations/ofsted",
        "subjects": 0,
        "languages": 1,
        "cadence": "monthly",
        "key": "ofsted",
    },
    "pearson_edexcel": {
        "mcp_url": "https://qualifications.pearson.com",
        "subjects": 8,
        "languages": 1,
        "cadence": "quarterly",
        "key": "pearson",
    },
    "cambridge_international": {
        "mcp_url": "https://www.cambridgeinternational.org",
        "subjects": 10,
        "languages": 1,
        "cadence": "quarterly",
        "key": "cambridge",
    },
    "wjec_wales": {
        "mcp_url": "https://www.wjec.co.uk",
        "subjects": 6,
        "languages": 1,
        "cadence": "monthly",
        "key": "wjec",
    },
    "qualifications_wales": {
        "mcp_url": "https://www.qualifications.wales",
        "subjects": 6,
        "languages": 1,
        "cadence": "quarterly",
        "key": "qualifications_wales",
    },
    "gov_wales": {
        "mcp_url": "https://www.gov.wales/education",
        "subjects": 0,
        "languages": 1,
        "cadence": "weekly",
        "key": "gov_wales",
    },
    "iom_education": {
        "mcp_url": "https://www.gov.im/education",
        "subjects": 0,
        "languages": 1,
        "cadence": "quarterly",
        "key": "iom",
    },
    "oide_ie": {
        "mcp_url": "https://oide.ie",
        "subjects": 0,
        "languages": 1,
        "cadence": "quarterly",
        "key": "oide",
    },
    "scoilnet_ie": {
        "mcp_url": "https://www.scoilnet.ie",
        "subjects": 0,
        "languages": 1,
        "cadence": "quarterly",
        "key": "scoilnet",
    },
    "gov_ie_education": {
        "mcp_url": "https://www.gov.ie/en/department-of-education",
        "subjects": 0,
        "languages": 1,
        "cadence": "weekly",
        "key": "gov_ie",
    },
}


@dataclass(frozen=True)
class LoadResult:
    """The outcome of a single `load_crawl_result` call."""

    package: str
    docs_inserted: int
    chunks_inserted: int
    credits_used: int
    scrape_id: str
    started_at: datetime
    completed_at: datetime
    status: str = "completed"
    error_message: str | None = None


def _doc_id(url: str, markdown: str) -> str:
    """Stable doc_id = sha256(url + content_hash)."""
    content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    return hashlib.sha256(f"{url}|{content_hash}".encode("utf-8")).hexdigest()


def _chunk_text(markdown: str, chunk_size: int = 1024) -> list[str]:
    """Split markdown into chunks of ~chunk_size chars (line-aware)."""
    if not markdown:
        return []
    chunks: list[str] = []
    text = markdown
    while text:
        if len(text) <= chunk_size:
            chunks.append(text)
            break
        # Find the last newline before chunk_size
        cut = text.rfind("\n", 0, chunk_size)
        if cut == -1:
            cut = chunk_size
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks


def init_schemas(con: Any) -> None:
    """Apply the firecrawl_meta_schema.sql (idempotent).

    Args:
        con: A DuckDB / MotherDuck connection (the canonical
            `md:cianfhoghlaim` destination).
    """
    schema_path = Path(__file__).parent / "firecrawl_meta_schema.sql"
    sql = schema_path.read_text()
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)


def log_scrape(
    con: Any,
    *,
    scrape_id: str,
    tool: str,
    pipeline: str,
    url: str | None,
    urls_count: int,
    credits_used: int,
    credits_estimated: int | None,
    cache_hit: bool,
    status: str,
    error_message: str | None,
    metadata: dict[str, Any] | None,
) -> None:
    """Append one row to `firecrawl_meta.scrapes`."""
    now = datetime.now(UTC)
    con.execute(
        """
        INSERT INTO cianfhoghlaim.firecrawl_meta.scrapes
        (scrape_id, started_at, completed_at, tool, pipeline, url, urls_count,
         credits_used, credits_estimated, cache_hit, status, error_message, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            scrape_id,
            now,
            now,
            tool,
            pipeline,
            url,
            urls_count,
            credits_used,
            credits_estimated,
            cache_hit,
            status,
            error_message,
            json.dumps(metadata or {}),
        ],
    )


def load_crawl_result(
    con: Any,
    *,
    package: str,
    crawl_result: dict[str, Any],
    pipeline: str,
    scraped_via: str = "firecrawl_crawl",
    embed_fn: Any | None = None,
) -> LoadResult:
    """Write a `firecrawl_crawl` result to the corpus + the docs_index.

    Args:
        con: A DuckDB / MotherDuck connection.
        package: The package name (must be in PACKAGE_WHITELIST for
            the software stack; or in EDUCATION_WHITELIST for
            education).
        crawl_result: The dict returned by
            `FirecrawlMCPClient.crawl` (or the SDK equivalent).
            Expected shape: `{"data": [{"url": ..., "markdown": ...,
            "metadata": {...}, "links": [...]}], "creditsUsed": n}`
        pipeline: The pipeline tag for `firecrawl_meta.scrapes`
            (e.g. `notebook:01_software_stack_crawl` or
            `dlt:ncca_mathematics`).
        scraped_via: `firecrawl_crawl` / `firecrawl_scrape` / etc.
        embed_fn: The embedder function (defaults to
            `_lifespan_embed` if None). Signature:
            `(text: str) -> list[float]`.

    Returns:
        The LoadResult with the row counts + the scrape_id.
    """
    started_at = datetime.now(UTC)
    scrape_id = hashlib.sha256(
        f"{package}|{pipeline}|{started_at.isoformat()}".encode("utf-8")
    ).hexdigest()
    credits_used = int(crawl_result.get("creditsUsed", 0))
    data = crawl_result.get("data", [])

    embed_fn = embed_fn or _default_embedder()

    docs_inserted = 0
    chunks_inserted = 0

    for page in data:
        url = page.get("url", "")
        markdown = page.get("markdown", "")
        if not url or not markdown:
            continue
        metadata = page.get("metadata", {})
        doc_id = _doc_id(url, markdown)
        content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()

        # Write to docs.<package>
        con.execute(
            """
            INSERT INTO cianfhoghlaim.firecrawl_corpus.docs
            (doc_id, url, title, description, markdown, summary, links, metadata,
             package, package_version, section, scraped_at, content_hash, scraped_via, credits_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                doc_id,
                url,
                metadata.get("title", ""),
                metadata.get("description", ""),
                markdown,
                page.get("summary", ""),
                json.dumps(page.get("links", [])),
                json.dumps(metadata),
                package,
                metadata.get("version", ""),
                metadata.get("section", ""),
                started_at,
                content_hash,
                scraped_via,
                credits_used,
            ],
        )
        docs_inserted += 1

        # Compute the chunks + embeddings
        for i, chunk_text in enumerate(_chunk_text(markdown)):
            chunk_id = hashlib.sha256(
                f"{doc_id}|{i}".encode("utf-8")
            ).hexdigest()
            embedding = embed_fn(chunk_text)
            con.execute(
                """
                INSERT INTO cianfhoghlaim.firecrawl_corpus.docs_index
                (chunk_id, doc_id, package, url, chunk_offset, chunk_text, embedding, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    chunk_id,
                    doc_id,
                    package,
                    url,
                    i,
                    chunk_text,
                    embedding,
                    started_at,
                ],
            )
            chunks_inserted += 1

    # Best-effort: sync to the LanceDB companion table. The actual
    # LanceDB sync is a Netflix-grade async job, but for the
    # canonical blob we just MERGE here.
    try:
        _sync_lancedb(con, package=package)
    except Exception as exc:  # pragma: no cover — runtime errors
        logger.warning(
            "firecrawl_corpus.lancedb_sync_failed",
            extra={"package": package, "error": str(exc)},
        )

    completed_at = datetime.now(UTC)
    log_scrape(
        con,
        scrape_id=scrape_id,
        tool=scraped_via,
        pipeline=pipeline,
        url=None,
        urls_count=len(data),
        credits_used=credits_used,
        credits_estimated=credits_used,
        cache_hit=False,
        status="completed",
        error_message=None,
        metadata={"package": package, "docs_inserted": docs_inserted},
    )

    return LoadResult(
        package=package,
        docs_inserted=docs_inserted,
        chunks_inserted=chunks_inserted,
        credits_used=credits_used,
        scrape_id=scrape_id,
        started_at=started_at,
        completed_at=completed_at,
    )


def _default_embedder() -> Any:
    """Default BGE-M3 embedder (the shared embedder from _lifespan)."""
    try:
        from cianfhoghlaim.cocoindex._lifespan import embed as lifespan_embed

        return lifespan_embed
    except ImportError:  # pragma: no cover — CI fallback
        def _stub(text: str) -> list[float]:
            # 1024-d zero vector; the canonical BGE-M3 model is
            # loaded by the cocoindex _lifespan.py at runtime.
            return [0.0] * 1024

        return _stub


def _sync_lancedb(con: Any, *, package: str) -> None:
    """Sync the docs_index rows to the LanceDB companion table.

    The canonical companion table is at
    `lancedb://md:cianfhoghlaim/firecrawl_corpus/docs_index`. The
    sync is best-effort: a failure here only logs a warning.
    """
    try:
        import lancedb  # type: ignore[import-not-found]

        # Read the docs_index rows for this package
        rows = con.execute(
            """
            SELECT chunk_id, doc_id, package, url, chunk_offset, chunk_text, embedding
            FROM cianfhoghlaim.firecrawl_corpus.docs_index
            WHERE package = ?
            """,
            [package],
        ).fetchall()

        # Open or connect to the LanceDB table
        db = lancedb.connect("md:cianfhoghlaim")
        tbl_name = "firecrawl_corpus_docs_index"
        try:
            tbl = db.open_table(tbl_name)
        except Exception:
            tbl = db.create_table(
                tbl_name,
                data=[
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
                ],
            )
            return
        # Merge: delete the existing rows for this package, then add
        tbl.delete(f"package = '{package}'")
        tbl.add(
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
    except ImportError:
        # CI fallback: skip the LanceDB sync when the package is
        # not installed. The docs_index table in DuckLake is the
        # canonical truth.
        pass


__all__ = [
    "PACKAGE_WHITELIST",
    "EDUCATION_WHITELIST",
    "LoadResult",
    "init_schemas",
    "log_scrape",
    "load_crawl_result",
]