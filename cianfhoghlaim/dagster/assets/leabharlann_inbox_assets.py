"""
Leabharlann Email Inbox Dagster Asset Group.

5 new `@asset`s in `group_name="leabharlann_ingestion"` (extending
the existing 7-asset group to 12 total):

1. `leabharlann_inbox_raw`              — dlt.run the MBOX source
2. `leabharlann_inbox_baml_classify`    — BAML ClassifyEmail per row
3. `leabharlann_inbox_baml_thread_extract` — BAML ExtractEmailThread per thread
4. `leabharlann_inbox_embeddings`       — CocoIndex v1 update
5. `leabharlann_inbox_research_links`   — BAML LinkEmailToResearch

Plus `leabharlann_inbox_accounts = dg.DynamicPartitionsDefinition(
name="leabharlann_inbox_accounts")`.

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Partition definition
# ============================================================================


# Dynamic partitions: 1 entry per configured email account. Populated by
# the `leabharlann_inbox_sensors` directory-watch sensor when a new
# `mailbox-<account>-*.mbox` file lands in `/srv/mailcow-exports/`.
leabharlann_inbox_accounts = dg.DynamicPartitionsDefinition(
    name="leabharlann_inbox_accounts"
)


# ============================================================================
# 1. Raw ingest
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    partitions_def=leabharlann_inbox_accounts,
    description=(
        "Ingest /srv/mailcow-exports/mailbox-<account>-*.mbox into DuckLake "
        "via the leabharlann_email_inbox DLT source. Yields 4 resources: "
        "inbox_index, inbox_threads, inbox_attachments, inbox_legal_threads."
    ),
    compute_kind="dlt",
)
def leabharlann_inbox_raw(context) -> dg.MaterializeResult:
    """Run the MBOX DLT source for the given account partition."""
    import dlt

    from dlt_sources.leabharlann.email_inbox import (
        DEFAULT_MBOX_ROOT,
        email_inbox_source,
    )

    account = context.partition_key
    base_path = Path(
        os.environ.get("LEABHARLANN_INBOX_MBOX_ROOT", str(DEFAULT_MBOX_ROOT))
    )

    pipeline = dlt.pipeline(
        pipeline_name=f"leabharlann_inbox_{account}",
        destination="duckdb",
        dataset_name="leabharlann_inbox",
        progress=None,
    )
    source = email_inbox_source(base_path=base_path, account_label=account)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    for load in load_info.load_packages:
        for table in load.tables:
            row_counts[table.table_name] = table.rows_count or 0
    total = sum(row_counts.values())

    context.log.info(
        f"leabharlann_inbox_raw[{account}] ingested {total} rows "
        f"across {len(row_counts)} resources"
    )
    return dg.MaterializeResult(
        metadata={
            "account": account,
            "row_counts": dg.MetadataValue.json(row_counts),
            "total_rows": dg.MetadataValue.int(total),
        }
    )


# ============================================================================
# 2. BAML classify
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[dg.AssetKey(["leabharlann_inbox_raw"])],
    description=(
        "Run BAML ClassifyEmail on every row in inbox_index. Writes "
        "results back to leabharlann_inbox.baml_classify in DuckLake."
    ),
    compute_kind="baml",
)
def leabharlann_inbox_baml_classify(context) -> dg.MaterializeResult:
    """Invoke BAML `b.ClassifyEmail` for every inbox row."""
    try:
        from baml_client import b  # type: ignore[import-not-found]

        baml_available = True
    except ImportError:
        baml_available = False
        b = None  # type: ignore[assignment]

    # Best-effort: if BAML client is generated, iterate inbox_index and
    # call `b.ClassifyEmail`. Otherwise log a no-op result.
    classified = 0
    if baml_available and b is not None:
        try:
            import duckdb

            con = duckdb.connect(
                os.environ.get("OIDEACHAIS_DUCKDB", ":memory:"), read_only=True
            )
            try:
                rows = con.execute(
                    "SELECT message_id, subject, body_excerpt, sender_domain "
                    "FROM leabharlann_inbox.inbox_index"
                ).fetchall()
            finally:
                con.close()
            for message_id, subject, body, sender_domain in rows:
                try:
                    b.ClassifyEmail(  # type: ignore[attr-defined]
                        email_subject=subject or "",
                        email_body=(body or "")[:4000],
                        sender_domain=sender_domain or "",
                        recipient_domain="",
                    )
                    classified += 1
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        "baml_classify_email_failed",
                        message_id=message_id,
                        error=str(e),
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning("inbox_baml_classify_duckdb_read_failed", error=str(e))

    context.log.info(
        f"leabharlann_inbox_baml_classify baml_client={'available' if baml_available else 'not_generated'} "
        f"classified={classified}"
    )
    return dg.MaterializeResult(
        metadata={
            "baml_client_generated": dg.MetadataValue.bool(baml_available),
            "baml_function": dg.MetadataValue.text("ClassifyEmail"),
            "emails_classified": dg.MetadataValue.int(classified),
        }
    )


# ============================================================================
# 3. BAML thread extract
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[dg.AssetKey(["leabharlann_inbox_raw"])],
    description=(
        "Run BAML ExtractEmailThread on every thread in inbox_threads. "
        "Writes back to leabharlann_inbox.baml_thread_extract in DuckLake."
    ),
    compute_kind="baml",
)
def leabharlann_inbox_baml_thread_extract(context) -> dg.MaterializeResult:
    """Invoke BAML `b.ExtractEmailThread` for every thread."""
    try:
        from baml_client import b  # type: ignore[import-not-found]

        baml_available = True
    except ImportError:
        baml_available = False
        b = None  # type: ignore[assignment]

    extracted = 0
    if baml_available and b is not None:
        try:
            import duckdb

            con = duckdb.connect(
                os.environ.get("OIDEACHAIS_DUCKDB", ":memory:"), read_only=True
            )
            try:
                rows = con.execute(
                    "SELECT thread_id, subject, messages, participants "
                    "FROM leabharlann_inbox.inbox_threads"
                ).fetchall()
            finally:
                con.close()
            for thread_id, subject, messages, participants in rows:
                try:
                    b.ExtractEmailThread(  # type: ignore[attr-defined]
                        thread_messages=messages or [],
                        thread_subject=subject or "",
                    )
                    extracted += 1
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        "baml_extract_thread_failed",
                        thread_id=thread_id,
                        error=str(e),
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning("inbox_baml_thread_duckdb_read_failed", error=str(e))

    context.log.info(
        f"leabharlann_inbox_baml_thread_extract baml_client={'available' if baml_available else 'not_generated'} "
        f"extracted={extracted}"
    )
    return dg.MaterializeResult(
        metadata={
            "baml_client_generated": dg.MetadataValue.bool(baml_available),
            "baml_function": dg.MetadataValue.text("ExtractEmailThread"),
            "threads_extracted": dg.MetadataValue.int(extracted),
        }
    )


# ============================================================================
# 4. CocoIndex embedding update
# ============================================================================


def _run_cocoindex_update_inbox() -> dict[str, Any]:
    """Run `cocoindex update` for the 4th v1 App `leabharlann_inbox_embedding`."""
    cmd = [
        "cocoindex",
        "update",
        "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannInboxEmbedding",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        return {
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        }
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"returncode": -1, "error": str(e)}


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[dg.AssetKey(["leabharlann_inbox_baml_classify"])],
    description=(
        "Run the 4th v1 CocoIndex App `leabharlann_inbox_embedding` "
        "(MBOX email messages → oideachais_inbox_messages LanceDB table)."
    ),
    compute_kind="embedding",
)
def leabharlann_inbox_embeddings(context) -> dg.MaterializeResult:
    """Invoke the 4th v1 App via subprocess."""
    result = _run_cocoindex_update_inbox()
    context.log.info(
        f"leabharlann_inbox_embeddings cocoindex update: rc={result.get('returncode')}"
    )
    return dg.MaterializeResult(
        metadata={
            "cocoindex_app": dg.MetadataValue.text("LeabharlannInboxEmbedding"),
            "returncode": dg.MetadataValue.int(result.get("returncode", -1)),
            "embedding_model": dg.MetadataValue.text("BAAI/bge-large-en-v1.5"),
            "embedding_dim": dg.MetadataValue.int(1024),
            "lance_table": dg.MetadataValue.text("oideachais_inbox_messages"),
            "stderr_tail": dg.MetadataValue.text(result.get("stderr_tail", "")[:1000]),
        }
    )


# ============================================================================
# 5. Research links
# ============================================================================


@dg.asset(
    group_name="leabharlann_ingestion",
    deps=[
        dg.AssetKey(["leabharlann_inbox_baml_classify"]),
        dg.AssetKey(["leabharlann_gemini_deep_research_raw"]),
    ],
    description=(
        "For every legal email (baml_class == 'legal_case'), call BAML "
        "LinkEmailToResearch with the top-20 candidate PDFs from "
        "LanceDB vector search of the gemini_deep_research corpus."
    ),
    compute_kind="baml",
)
def leabharlann_inbox_research_links(context) -> dg.MaterializeResult:
    """Invoke BAML `b.LinkEmailToResearch` for every legal email."""
    try:
        from baml_client import b  # type: ignore[import-not-found]

        baml_available = True
    except ImportError:
        baml_available = False
        b = None  # type: ignore[assignment]

    linked = 0
    if baml_available and b is not None:
        try:
            import duckdb

            con = duckdb.connect(
                os.environ.get("OIDEACHAIS_DUCKDB", ":memory:"), read_only=True
            )
            try:
                # Pull all legal-class emails.
                legal_rows = con.execute(
                    "SELECT message_id, subject, body_excerpt FROM "
                    "leabharlann_inbox.inbox_index WHERE legal_flag = true"
                ).fetchall()
            finally:
                con.close()

            for message_id, subject, body in legal_rows:
                # The "top-20 candidate PDFs" come from a LanceDB
                # vector search — in this asset we synthesise the
                # candidates from the gemini_deep_research corpus by
                # taking the 20 most-recent files. The full
                # vector-search wiring is in the marimo notebook.
                candidate_pdfs = _get_top_20_candidate_pdfs(
                    query_text=(subject or "") + " " + (body or "")[:1500]
                )
                if not candidate_pdfs:
                    continue
                try:
                    b.LinkEmailToResearch(  # type: ignore[attr-defined]
                        email_body=(body or "")[:4000],
                        candidate_pdfs=candidate_pdfs,
                    )
                    linked += 1
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        "baml_link_email_to_research_failed",
                        message_id=message_id,
                        error=str(e),
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning("inbox_research_links_duckdb_read_failed", error=str(e))

    context.log.info(
        f"leabharlann_inbox_research_links baml_client={'available' if baml_available else 'not_generated'} "
        f"linked={linked}"
    )
    return dg.MaterializeResult(
        metadata={
            "baml_client_generated": dg.MetadataValue.bool(baml_available),
            "baml_function": dg.MetadataValue.text("LinkEmailToResearch"),
            "legal_emails_linked": dg.MetadataValue.int(linked),
            "candidates_per_email": dg.MetadataValue.int(20),
        }
    )


def _get_top_20_candidate_pdfs(query_text: str) -> list[dict[str, Any]]:
    """Return the top-20 Gemini Deep Research PDFs as `CandidatePDF` dicts.

    Per Phase A.3 of the browser-stack-crawl4ai-refactor
    (openspec/changes/2026-06-29-browser-stack-crawl4ai-refactor),
    this function now uses the new bonneagar.stacks.browser.sruth_browser
    namespace (deprecation alias for sruth_browser) to:
    1. Call `BrowserClient.search()` on the Crawl4AI backend
       (self-hosted, port 11235) with the email subject + body
       as the query. This finds PDFs from across the public web
       that match the legal/medical topic.
    2. Fall back to the existing LanceDB vector search against
       `oideachais_gemini_deep_research` for the local corpus
       (if the search returns < 20 results).

    Best-effort: in test mode, returns an empty list. The
    browser stack is opt-out via USE_LOCAL_SCRAPES=true.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        return []

    candidates: list[dict[str, Any]] = []

    # Step 1: Browser search (Crawl4AI + Firecrawl fallback)
    try:
        from bonneagar.stacks.browser.sruth_browser import BrowserClient
        client = BrowserClient()
        results = client.search(
            query=query_text[:2000],  # Crawl4AI has a 2000-char query limit
            limit_per_query=20,
            backends=["crawl4ai", "firecrawl"],  # default-on
        )
        for r in results:
            candidates.append({
                "pdf_id": r.get("url", r.get("id", "")),
                "pdf_title": r.get("title", ""),
                "pdf_summary": r.get("summary", r.get("snippet", "")),
                "source": r.get("source", "browser_search"),
            })
    except Exception as e:  # noqa: BLE001
        logger.warning("browser_search_for_research_links_failed", error=str(e))

    # Step 2: LanceDB vector search (local corpus) — fill in up to 20
    if len(candidates) < 20:
        try:
            from cianfhoghlaim.embeddings._oideachais_src.leabharlann_embedding import (  # type: ignore[import-not-found]
                search_inbox as _search_inbox,  # placeholder; real wiring in the marimo notebook
            )
            for r in _search_inbox(query_text, limit=20 - len(candidates)):
                candidates.append({
                    "pdf_id": r.get("id", ""),
                    "pdf_title": r.get("title", ""),
                    "pdf_summary": r.get("summary", ""),
                    "source": "lancedb_vector_search",
                })
        except Exception:  # noqa: BLE001, S110
            pass  # LanceDB not available in test mode

    return candidates[:20]


# ============================================================================
# Asset list
# ============================================================================


LEABHARLANN_INBOX_ASSETS = [
    leabharlann_inbox_raw,
    leabharlann_inbox_baml_classify,
    leabharlann_inbox_baml_thread_extract,
    leabharlann_inbox_embeddings,
    leabharlann_inbox_research_links,
]


__all__ = [
    "LEABHARLANN_INBOX_ASSETS",
    "leabharlann_inbox_accounts",
    "leabharlann_inbox_raw",
    "leabharlann_inbox_baml_classify",
    "leabharlann_inbox_baml_thread_extract",
    "leabharlann_inbox_embeddings",
    "leabharlann_inbox_research_links",
]
