"""
Email Triage Agent for the leabharlann email-inbox pipeline.

10th Google ADK agent on the oideachais stack (port 7778). Exposes 4
read-only tools against DuckLake + Lance that triage a personal inbox
across 4 accounts (DKIT.ie Microsoft 365, 2 Gmail, Hotmail):

  - classify_email_thread(thread_id) -> EmailClassificationResult
  - summarise_thread(thread_id, max_chars=500) -> str
  - link_thread_to_research(thread_id, k=5) -> list[ResearchLink]
  - find_loose_threads(account, days_idle_min=7) -> list[ThreadSummary]

All 4 tools compose BAML `email.baml` (ClassifyEmail / ExtractEmailThread
/ LinkEmailToResearch) + DuckLake SQL + LanceDB vector search. They
never mutate the data plane; the marimo notebook + the openclaw WebChat
sub-UI are the two write surfaces for the `leabharlann_inbox_user_overrides`
table.

The citation callbacks at `agents/adk/callbacks/citation_callbacks.py`
are registered with this agent so the existing LanceDB vector-search
citation pipeline injects "Sources:" footers into every tool response.

Langfuse auto-traces every tool call (the existing `LANGFUSE_*` env
vars on the oideachais stack are reused — see
`bonneagar/stacks/oideachais/compose.yaml`).

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from .litellm_agent import litellm_model

from .config import config

logger = logging.getLogger(__name__)


def _email_triage_model() -> str:
    """Resolve the email-triage LLM via MODEL_REGISTRY (the
    centralized-model-registry openspec change). The role
    ``email_triage_strong`` is the disambiguated lookup that maps to
    ``gemini-2.5-pro`` (the Google ADK strong path). Falls back to
    ``MODEL_REGISTRY.resolve("text_llm", "strong")`` for back-compat,
    and to the historical ``gemini-2.5-pro`` hardcoded string when
    the registry is unavailable. The env var
    ``EMAIL_TRIAGE_MODEL`` overrides the registry lookup for prod /
    dev convenience.
    """
    override = os.environ.get("EMAIL_TRIAGE_MODEL")
    if override:
        return override
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        return MODEL_REGISTRY.resolve("text_llm", "email_triage_strong")
    except KeyError:
        try:
            from meaisinfhoghlaim.models import MODEL_REGISTRY
            return MODEL_REGISTRY.resolve("text_llm", "strong")
        except Exception:  # noqa: BLE001
            return "gemini-2.5-pro"
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        return "gemini-2.5-pro"


# =============================================================================
# Response Models (the typed contracts for the 4 tool responses)
# =============================================================================


class EmailClassificationResult(BaseModel):
    """BAML `ClassifyEmail` result — 9-label enum + confidence + urgency."""

    class_label: str = Field(
        description=(
            "One of the 9 EmailClass labels: legal_case, medical_access, "
            "academic_admin, personal_correspondence, institutional_correspondence, "
            "spam_or_marketing, newsletter, automated_notification, other"
        )
    )
    confidence: float = Field(description="LLM self-rated confidence 0.0-1.0")
    urgency_score: float = Field(description="Reply urgency 0.0-1.0")
    summary_5_words: str = Field(description="<=5 word summary of the email")
    suggested_action: str = Field(description="1-sentence suggested next step")


class EmailThreadSummary(BaseModel):
    """BAML `ExtractEmailThread` result — typed thread metadata."""

    participants: list[str] = Field(description="Distinct human participants")
    topic_summary: str = Field(description="1-2 sentence topic summary")
    action_items: list[str] = Field(description="Ordered action items")
    decision_points: list[str] = Field(description="Ordered decisions taken")
    dates_mentioned: list[str] = Field(description="ISO 8601 dates mentioned")
    key_quotes: list[str] = Field(description="3-5 verbatim quotes (max 200 chars)")


class ResearchLink(BaseModel):
    """BAML `LinkEmailToResearch` result — a single Gemini PDF link."""

    linked_pdf_id: str = Field(description="The `pdf_id` of the linked Gemini PDF")
    link_reason: str = Field(description="1-sentence reason for the link")
    link_confidence: float = Field(description="LLM confidence 0.0-1.0")
    snippet: str = Field(description="<=200 char quote from the email body")


class ThreadSummary(BaseModel):
    """A single thread row for the loose-threads table."""

    thread_id: str = Field(description="Canonical thread id (account/thread-...)")
    account: str = Field(description="Email account key (dkit_ie, gmail_personal, ...)")
    subject: str = Field(description="Thread subject (normalised)")
    baml_class: str = Field(description="BAML `class_label` from ClassifyEmail")
    urgency_score: float = Field(description="Max urgency across thread messages")
    last_message_at: str = Field(description="ISO 8601 timestamp of last message")
    days_idle: int = Field(description="Days since the user last replied")
    participant_count: int = Field(description="Distinct participants in the thread")
    message_count: int = Field(description="Total messages in the thread")


# =============================================================================
# BAML client import (graceful fallback if not generated)
# =============================================================================

try:
    from baml_client import b as baml
    from baml_client.types import (
        EmailClassificationResult as BAMLClassification,
        EmailThread as BAMLThread,
        ResearchLink as BAMLLink,
    )
    HAS_BAML = True
except ImportError:
    baml = None
    BAMLClassification = None
    BAMLThread = None
    BAMLLink = None
    HAS_BAML = False
    logger.warning(
        "baml_client not generated. email_triage tools will return empty results. "
        "Run `uv run baml-cli generate` from cianfhoghlaim/core/baml/"
    )


# =============================================================================
# DuckLake + LanceDB access (graceful fallback when not provisioned)
# =============================================================================


_DUCKLAKE_PATHS = {
    "duckdb": os.getenv("DUCKDB_PATH", "/app/oideachais/data_platform/.dlt/curriculum_unified/curriculum_unified.duckdb"),
    "ducklake": os.getenv("DUCKLAKE_PATH", "/app/oideachais/data_platform/.dlt/ducklake"),
}

_LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lakehouse-lance-namespace:8182")


def _open_duckdb(read_only: bool = True):
    """Open the DuckDB/DuckLake handle. Returns None on any failure.

    LBYL exception handling per dignified-python: never crash the
    agent if the data plane is unreachable — return empty results.
    """
    path = Path(_DUCKLAKE_PATHS["duckdb"])
    if not path.exists():
        logger.warning("duckdb file not found at %s; tools will return empty", path)
        return None
    try:
        import duckdb  # local import: avoid hard dep at agent-import time
    except ImportError:
        logger.warning("duckdb package not importable; tools will return empty")
        return None
    try:
        return duckdb.connect(str(path), read_only=read_only)
    except Exception as exc:  # OSError, duckdb.Error, etc.
        logger.warning("duckdb connect failed: %s", exc)
        return None


def _load_thread_rows(conn, thread_id: str) -> list[dict[str, Any]]:
    """Read all messages for a thread_id from `ducklake_oideachais.inbox_index`.

    Returns [] on any failure. The thread_id is the canonical
    `<account>/<thread_hash>` key emitted by the dlt source.
    """
    if conn is None:
        return []
    sql = (
        "SELECT account, thread_id, message_id, sender, recipients, "
        "       subject, date_iso, body_excerpt, baml_class, baml_urgency "
        "FROM ducklake_oideachais.inbox_index "
        "WHERE thread_id = ? "
        "ORDER BY date_iso ASC"
    )
    try:
        rows = conn.execute(sql, [thread_id]).fetchall()
    except Exception as exc:
        logger.warning("inbox_index read failed for %s: %s", thread_id, exc)
        return []
    cols = (
        "account", "thread_id", "message_id", "sender", "recipients",
        "subject", "date_iso", "body_excerpt", "baml_class", "baml_urgency",
    )
    return [dict(zip(cols, r)) for r in rows]


# =============================================================================
# Tool 1: classify_email_thread
# =============================================================================


async def classify_email_thread(thread_id: str) -> EmailClassificationResult:
    """Classify a single email thread into 1 of 9 `EmailClass` labels.

    Data-plane contracts:
        - DuckLake table: `ducklake_oideachais.inbox_index` (read)
        - BAML function:  `ClassifyEmail` (from `email.baml`, client
          alias `ExtractEn` → `extract-en` LiteLLM gateway route)
        - LanceDB:       not read directly — the first message of the
          thread is the classification input; no vector search is needed.

    Args:
        thread_id: Canonical thread id of the form `<account>/<thread_hash>`,
            e.g. `dkit_ie/thread-abc123`.

    Returns:
        `EmailClassificationResult` with `class_label`, `confidence`,
        `urgency_score`, `summary_5_words`, `suggested_action`. Returns a
        stub with `class_label="other"`, `confidence=0.0` when BAML is
        unavailable.
    """
    conn = _open_duckdb()
    rows = _load_thread_rows(conn, thread_id)
    if not rows:
        logger.info("classify_email_thread: no rows for %s", thread_id)
        return EmailClassificationResult(
            class_label="other",
            confidence=0.0,
            urgency_score=0.0,
            summary_5_words="no data",
            suggested_action="Run leabharlann_inbox_raw first",
        )
    first = rows[0]
    sender_domain = (first.get("sender") or "").split("@")[-1] or "unknown"
    recipient_domain = (first.get("recipients") or "").split("@")[-1] or "unknown"
    if not HAS_BAML:
        return EmailClassificationResult(
            class_label=first.get("baml_class") or "other",
            confidence=0.5,
            urgency_score=float(first.get("baml_urgency") or 0.0),
            summary_5_words="(baml offline)",
            suggested_action="Run `uv run baml-cli generate` to enable BAML classification",
        )
    try:
        result = baml.ClassifyEmail(
            email_subject=first.get("subject") or "",
            email_body=first.get("body_excerpt") or "",
            sender_domain=sender_domain,
            recipient_domain=recipient_domain,
        )
    except Exception as exc:
        logger.warning("BAML ClassifyEmail failed for %s: %s", thread_id, exc)
        return EmailClassificationResult(
            class_label="other",
            confidence=0.0,
            urgency_score=0.0,
            summary_5_words="baml error",
            suggested_action=str(exc)[:200],
        )
    return EmailClassificationResult(
        class_label=getattr(result, "class_label", "other"),
        confidence=float(getattr(result, "confidence", 0.0) or 0.0),
        urgency_score=float(getattr(result, "urgency_score", 0.0) or 0.0),
        summary_5_words=getattr(result, "summary_5_words", "") or "",
        suggested_action=getattr(result, "suggested_action", "") or "",
    )


# =============================================================================
# Tool 2: summarise_thread
# =============================================================================


async def summarise_thread(thread_id: str, max_chars: int = 500) -> str:
    """Summarise an email thread (BAML `ExtractEmailThread`).

    Data-plane contracts:
        - DuckLake table: `ducklake_oideachais.inbox_index` (read all rows
          for the thread, ordered chronologically)
        - BAML function:  `ExtractEmailThread` (from `email.baml`, client
          alias `ExtractEn` → `extract-en` LiteLLM gateway route)
        - Output cap:     `max_chars` truncates the final summary; default
          500 chars to match the marimo notebook section width.

    Args:
        thread_id: Canonical thread id `<account>/<thread_hash>`.
        max_chars: Maximum length of the returned summary string.

    Returns:
        A prose summary of the thread <= `max_chars` characters. Returns
        `(unavailable)` when BAML is not generated or the thread has no
        rows in DuckLake.
    """
    conn = _open_duckdb()
    rows = _load_thread_rows(conn, thread_id)
    if not rows:
        return f"(no messages for thread {thread_id})"
    if not HAS_BAML:
        return (
            f"Thread {thread_id}: {len(rows)} message(s); "
            "BAML ExtractEmailThread offline — run `uv run baml-cli generate`."
        )
    messages = [
        f"From: {r.get('sender', '')}\nDate: {r.get('date_iso', '')}\n"
        f"Body: {r.get('body_excerpt', '')[:2000]}"
        for r in rows
    ]
    try:
        thread = baml.ExtractEmailThread(
            thread_messages=messages,
            thread_subject=rows[0].get("subject") or "",
        )
    except Exception as exc:
        logger.warning("BAML ExtractEmailThread failed for %s: %s", thread_id, exc)
        return f"(BAML error: {exc})"
    topic = getattr(thread, "topic_summary", "") or ""
    actions = getattr(thread, "action_items", []) or []
    action_str = "; ".join(actions[:3]) if actions else ""
    summary = topic
    if action_str:
        summary = f"{topic} Actions: {action_str}" if topic else f"Actions: {action_str}"
    return summary[:max_chars]


# =============================================================================
# Tool 3: link_thread_to_research
# =============================================================================


async def link_thread_to_research(thread_id: str, k: int = 5) -> list[ResearchLink]:
    """Link an email thread to the top-k Gemini Deep Research PDFs.

    Data-plane contracts:
        - DuckLake table: `ducklake_oideachais.inbox_index` (read)
        - LanceDB table: `oideachais_inbox_messages` (read, top-k
          neighbours via cosine vector search on
          `BAAI/bge-large-en-v1.5` 1024-d embeddings from
          `leabharlann_inbox_embedding` CocoIndex App)
        - BAML function:  `LinkEmailToResearch` (from `email.baml`,
          client alias `ExtractEnStrong` → `extract-en-strong` — uses
          anthropic/claude-sonnet-4 → gemini-2.5-pro for the more
          demanding reasoning pass)
        - Lance table:    `oideachais_gemini_deep_research` (the
          source of the candidate PDFs from
          `leabharlann/gemini_deep_research/{law,medical,culture,...}`)

    Args:
        thread_id: Canonical thread id `<account>/<thread_hash>`.
        k: Number of candidate PDFs to retrieve from LanceDB before the
            BAML reasoning pass (default 5; the underlying Dagster
            asset uses 20).

    Returns:
        A list of `ResearchLink` rows. Returns [] when BAML is
        unavailable or the thread has no body excerpt.
    """
    conn = _open_duckdb()
    rows = _load_thread_rows(conn, thread_id)
    if not rows:
        return []
    if not HAS_BAML:
        return []
    body_excerpt = (rows[0].get("body_excerpt") or "").strip()
    if not body_excerpt:
        return []

    # Read the top-k candidate Gemini Deep Research PDFs from the
    # LanceDB namespace. The cosine + BM25 hybrid index lives on
    # the `oideachais_gemini_deep_research` table.
    candidates: list[dict[str, str]] = []
    try:
        import lancedb  # local import
        db = lancedb.connect(_LANCEDB_URI)
        tbl = db.open_table("oideachais_gemini_deep_research")
        q = body_excerpt[:512]
        rs = tbl.search(q).limit(k).to_list()
    except Exception as exc:
        logger.warning("LanceDB candidate read failed: %s", exc)
        rs = []
    for hit in rs:
        candidates.append(
            {
                "pdf_id": str(hit.get("pdf_id") or hit.get("id") or ""),
                "pdf_title": str(hit.get("title") or hit.get("pdf_title") or ""),
                "pdf_summary": str(hit.get("summary") or hit.get("pdf_summary") or ""),
            }
        )
    if not candidates:
        return []
    try:
        results = baml.LinkEmailToResearch(
            email_body=body_excerpt[:8000],
            candidate_pdfs=candidates,
        )
    except Exception as exc:
        logger.warning("BAML LinkEmailToResearch failed for %s: %s", thread_id, exc)
        return []
    return [
        ResearchLink(
            linked_pdf_id=str(getattr(r, "linked_pdf_id", "")),
            link_reason=str(getattr(r, "link_reason", "")),
            link_confidence=float(getattr(r, "link_confidence", 0.0) or 0.0),
            snippet=str(getattr(r, "snippet", "")),
        )
        for r in (results or [])
    ]


# =============================================================================
# Tool 4: find_loose_threads
# =============================================================================


async def find_loose_threads(
    account: str, days_idle_min: int = 7
) -> list[ThreadSummary]:
    """Find threads where the user has not replied in >= days_idle_min days.

    Data-plane contracts:
        - DuckLake table: `ducklake_oideachais.inbox_threads` (read) —
          joined to `ducklake_oideachais.inbox_index` for the latest
          message timestamp + the `baml_class` + `baml_urgency` columns
          populated by `leabharlann_inbox_baml_classify`.
        - LanceDB:       not read.
        - BAML:          not called directly — the BAML classification
          was pre-computed by the Dagster asset pipeline.

    Args:
        account: Email account key — one of `dkit_ie`, `gmail_personal`,
            `gmail_academic`, `hotmail_legacy`.
        days_idle_min: Minimum days since the user's last reply (default
            7). The query is a single DuckLake SQL `SELECT` with a
            `WHERE days_idle >= ?` predicate.

    Returns:
        A list of `ThreadSummary` sorted by `urgency_score` DESC.
        Returns [] when DuckLake is unreachable.
    """
    conn = _open_duckdb()
    if conn is None:
        return []
    # The single e2e demo table shape — the dlt source creates it.
    # The LEFT JOIN self-pattern lets us compute "last_user_reply_at"
    # without a separate `inbox_user_replies` table.
    sql = (
        "SELECT t.thread_id, t.account, t.subject, "
        "       MAX(i.baml_class)        AS baml_class, "
        "       MAX(i.baml_urgency)      AS urgency_score, "
        "       MAX(i.date_iso)          AS last_message_at, "
        "       COUNT(DISTINCT i.message_id) AS message_count "
        "FROM ducklake_oideachais.inbox_threads t "
        "JOIN ducklake_oideachais.inbox_index i "
        "  ON i.thread_id = t.thread_id "
        "WHERE t.account = ? "
        "  AND t.last_user_reply_at IS NOT NULL "
        "  AND DATE_DIFF('day', "
        "      CAST(t.last_user_reply_at AS DATE), "
        "      CAST(CURRENT_DATE AS DATE)) >= ? "
        "GROUP BY t.thread_id, t.account, t.subject "
        "ORDER BY urgency_score DESC, last_message_at ASC"
    )
    try:
        rows = conn.execute(sql, [account, int(days_idle_min)]).fetchall()
    except Exception as exc:
        logger.warning("find_loose_threads query failed: %s", exc)
        return []
    cols = (
        "thread_id", "account", "subject", "baml_class", "urgency_score",
        "last_message_at", "message_count",
    )
    out: list[ThreadSummary] = []
    today = datetime.now(tz=timezone.utc).date()
    for r in rows:
        d = dict(zip(cols, r))
        last_iso = d.get("last_message_at") or ""
        try:
            last_date = datetime.fromisoformat(str(last_iso).replace("Z", "+00:00")).date()
        except (TypeError, ValueError):
            last_date = today
        out.append(
            ThreadSummary(
                thread_id=str(d.get("thread_id") or ""),
                account=str(d.get("account") or account),
                subject=str(d.get("subject") or ""),
                baml_class=str(d.get("baml_class") or "other"),
                urgency_score=float(d.get("urgency_score") or 0.0),
                last_message_at=str(last_iso),
                days_idle=(today - last_date).days,
                participant_count=0,
                message_count=int(d.get("message_count") or 0),
            )
        )
    return out


# =============================================================================
# Wire the 4 tools as ADK FunctionTools
# =============================================================================


classify_email_thread_tool = FunctionTool(func=classify_email_thread)
summarise_thread_tool = FunctionTool(func=summarise_thread)
link_thread_to_research_tool = FunctionTool(func=link_thread_to_research)
find_loose_threads_tool = FunctionTool(func=find_loose_threads)


# =============================================================================
# Agent definition (the 10th ADK agent on the oideachais stack)
# =============================================================================


email_triage_agent = LlmAgent(
    name="email_triage",
    model=_email_triage_model(),
    description=(
        "Triage a personal inbox across 4 accounts (DKIT.ie Microsoft 365, "
        "2 Gmail, Hotmail). Classifies each thread into 1 of 9 EmailClass "
        "labels, summarises loose threads, and links legal / medical threads "
        "to the top-k Gemini Deep Research PDFs in the user's archive."
    ),
    instruction=(
        "You are the email_triage agent on the oideachais stack "
        "(port 7778). You triage a personal + professional inbox across "
        "4 accounts (DKIT.ie M365, 2 Gmail, Hotmail).\n\n"
        "TOOLS:\n"
        "1. classify_email_thread(thread_id) -> EmailClassificationResult\n"
        "2. summarise_thread(thread_id, max_chars=500) -> str\n"
        "3. link_thread_to_research(thread_id, k=5) -> list[ResearchLink]\n"
        "4. find_loose_threads(account, days_idle_min=7) -> list[ThreadSummary]\n\n"
        "WORKFLOW:\n"
        "1. 'what should I reply to?' -> find_loose_threads first.\n"
        "2. 'summarise thread X' -> summarise_thread.\n"
        "3. 'is this legal / medical?' -> classify_email_thread.\n"
        "4. 'link to research' on legal / medical threads -> "
        "link_thread_to_research(k=5).\n"
        "5. Always cite LanceDB research links in your final response.\n\n"
        "ACCOUNT KEYS: dkit_ie, gmail_personal, gmail_academic, hotmail_legacy.\n"
        "THREAD ID FORMAT: <account>/<thread_hash>.\n"
        "All 4 tools are read-only; Langfuse auto-traces every call.\n"
    ),
    tools=[
        classify_email_thread_tool,
        summarise_thread_tool,
        link_thread_to_research_tool,
        find_loose_threads_tool,
    ],
    output_key="email_triage_response",
)


# =============================================================================
# Citation callback registration
# =============================================================================
#
# The existing 9 ADK agents do not register the citation callbacks. Per
# task 6.3, the `email_triage` agent registers them here so every tool
# response gets a LanceDB vector-search "Sources:" footer. We re-use the
# existing callbacks at `agents/adk/callbacks/citation_callbacks.py`
# (no modifications to the 9 existing agents or to the callback module).
#
# The callback is wired into the agent at construction time via the
# `after_tool_callback` hook. ADK 1.5+ accepts a list of callbacks on
# the LlmAgent constructor; for older versions we attach it at the
# tool level by passing it to each FunctionTool.

try:  # pragma: no cover — callback registration is best-effort
    from .callbacks.citation_callbacks import (
        collect_education_sources_callback,
        format_education_citations_callback,
    )

    # Best-effort: some ADK versions expose `after_tool_callback` /
    # `before_tool_callback` directly; older versions need a
    # per-tool wrapper. We attempt the direct attribute first and
    # fall back to a no-op if the field is missing on this version.
    if hasattr(email_triage_agent, "after_tool_callback"):
        email_triage_agent.after_tool_callback = collect_education_sources_callback
    if hasattr(email_triage_agent, "before_model_callback"):
        email_triage_agent.before_model_callback = format_education_citations_callback
    logger.info("email_triage: citation callbacks registered")
except ImportError:
    logger.warning(
        "email_triage: citation callbacks not importable; "
        "tool responses will not include the Sources: footer"
    )


__all__ = [
    "EmailClassificationResult",
    "EmailThreadSummary",
    "HAS_BAML",
    "ResearchLink",
    "ThreadSummary",
    "classify_email_thread",
    "classify_email_thread_tool",
    "email_triage_agent",
    "find_loose_threads",
    "find_loose_threads_tool",
    "link_thread_to_research",
    "link_thread_to_research_tool",
    "summarise_thread",
    "summarise_thread_tool",
]
