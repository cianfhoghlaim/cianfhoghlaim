"""
oideachais.cognify_rules.leabharlann_inbox_cross_archive — deterministic
cross-archive edge population between the email-inbox graph and the
existing leabharlann + legal-case + research-PDF + person graphs.

3 edge rules:
  1. (:EmailThread) -[:RELATES_TO]-> (:LegalCase)
       when the thread's `baml_class == "legal_case"`.
  2. (:EmailThread) -[:CITES]->     (:ResearchPDF)
       from the `LinkEmailToResearch` BAML function results.
  3. (:EmailAccount) -[:OWNS]->     (:Person)
       from sender full-name resolution (parsed from the `from` header).

All rules use FalkorDB MERGE so the pass is idempotent: re-running on
the same input produces the same graph.

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
            tasks.md Phase 7.4
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Rule 1: EmailThread -[:RELATES_TO]-> LegalCase (baml_class == "legal_case")
# ---------------------------------------------------------------------------


def _build_legal_thread_query(
    threads: list[dict[str, Any]],
    legal_cases: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the legal-thread rule.

    A `LegalCase` is identified by its `case_id` (or `title`, falling
    back to the case name). The link confidence is taken from the
    thread's `baml_urgency` (0.0-1.0).
    """
    legal_by_id: dict[str, dict[str, Any]] = {}
    for c in legal_cases:
        cid = c.get("case_id") or c.get("title") or ""
        if cid:
            legal_by_id[str(cid)] = c

    edges: list[dict[str, Any]] = []
    for t in threads:
        if t.get("baml_class") != "legal_case":
            continue
        # Match on the thread's `legal_case_ref` (if any), else
        # leave the case_id blank so the edge has a stub target.
        case_ref = t.get("legal_case_ref") or ""
        if case_ref and case_ref in legal_by_id:
            target_case_id = case_ref
        elif legal_by_id:
            # Default: link to the most-recently-added legal case.
            target_case_id = next(iter(legal_by_id))
        else:
            continue
        edges.append(
            {
                "source": t.get("thread_id", ""),
                "target": target_case_id,
                "confidence": float(t.get("baml_urgency", 0.5)),
                "link_reason": t.get("baml_summary", "legal_classified"),
            }
        )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (t:EmailThread {thread_id: edge.source})
    MATCH (l:LegalCase {case_id: edge.target})
    MERGE (t)-[r:RELATES_TO]->(l)
    ON CREATE SET r.confidence = edge.confidence,
                  r.link_reason = edge.link_reason,
                  r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 2: EmailThread -[:CITES]-> ResearchPDF (LinkEmailToResearch results)
# ---------------------------------------------------------------------------


def _build_research_link_query(
    research_links: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the research-link rule.

    Each `ResearchLink` row has:
        {
          "thread_id":     str,
          "linked_pdf_id": str,
          "link_reason":   str,
          "link_confidence": float,
          "snippet":       str,
        }
    """
    edges: list[dict[str, Any]] = []
    for link in research_links:
        thread_id = link.get("thread_id") or ""
        pdf_id = link.get("linked_pdf_id") or ""
        if not thread_id or not pdf_id:
            continue
        edges.append(
            {
                "source": thread_id,
                "target": pdf_id,
                "link_confidence": float(link.get("link_confidence", 0.5)),
                "link_reason": link.get("link_reason", ""),
                "snippet": (link.get("snippet", "") or "")[:500],
            }
        )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (t:EmailThread {thread_id: edge.source})
    MATCH (r:ResearchPDF {pdf_id: edge.target})
    MERGE (t)-[c:CITES]->(r)
    ON CREATE SET c.link_confidence = edge.link_confidence,
                  c.link_reason = edge.link_reason,
                  c.snippet = edge.snippet,
                  c.created_at = timestamp()
    RETURN count(c) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 3: EmailAccount -[:OWNS]-> Person (sender full-name resolution)
# ---------------------------------------------------------------------------


# "Display Name <addr@x>" → "Display Name"
_DISPLAY_NAME_RE = re.compile(r'^\s*"?([^"<]+?)\s*"?\s*<[^>]+@[^>]+>\s*$')


def _extract_display_name(from_header: str | None) -> str:
    """Extract the display name from a `from` header. Returns "" on failure."""
    if not from_header:
        return ""
    m = _DISPLAY_NAME_RE.match(from_header)
    if m:
        return m.group(1).strip()
    return ""


def _build_person_resolution_query(
    accounts: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the sender → Person rule.

    Each `account` row is expected to have at minimum:
        {"account_label": str, "from_header": str, "from_addr": str}
    The rule parses the `from_header` for the display name and links
    each account to a Person node keyed by (display_name, email).
    """
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for acc in accounts:
        display = _extract_display_name(acc.get("from_header", ""))
        email = acc.get("from_addr", "")
        if not email:
            continue
        key = (display.lower(), email.lower())
        if key in seen:
            continue
        seen.add(key)
        edges.append(
            {
                "account_label": acc.get("account_label", ""),
                "display_name": display,
                "email": email,
            }
        )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MERGE (a:EmailAccount {account_label: edge.account_label})
    MERGE (p:Person {email: edge.email})
    ON CREATE SET p.display_name = edge.display_name
    MERGE (a)-[r:OWNS]->(p)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def build_all_inbox_cross_archive_queries(
    *,
    threads: list[dict[str, Any]] | None = None,
    legal_cases: list[dict[str, Any]] | None = None,
    research_links: list[dict[str, Any]] | None = None,
    accounts: list[dict[str, Any]] | None = None,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Return a list of `(name, cypher, params)` tuples for the inbox
    cross-archive FalkorDB pass.

    Empty queries (no matches) are filtered out so the caller can skip
    them. Idempotent via MERGE.
    """
    threads = list(threads or [])
    legal_cases = list(legal_cases or [])
    research_links = list(research_links or [])
    accounts = list(accounts or [])

    out: list[tuple[str, str, dict[str, Any]]] = []

    c1, p1 = _build_legal_thread_query(threads, legal_cases)
    if c1:
        out.append(("email_thread_relates_to_legal_case", c1, p1))

    c2, p2 = _build_research_link_query(research_links)
    if c2:
        out.append(("email_thread_cites_research_pdf", c2, p2))

    c3, p3 = _build_person_resolution_query(accounts)
    if c3:
        out.append(("email_account_owns_person", c3, p3))

    return out


def populate_inbox_cross_archive_edges(
    *,
    threads: Iterable[dict[str, Any]] | None = None,
    legal_cases: Iterable[dict[str, Any]] | None = None,
    research_links: Iterable[dict[str, Any]] | None = None,
    accounts: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
) -> dict[str, Any]:
    """Populate FalkorDB with the 3 inbox cross-archive edge types.

    Returns
    -------
    dict[str, Any]
        `{"queries_executed": int, "total_edges": int, "queries": [str]}`.
    """
    queries = build_all_inbox_cross_archive_queries(
        threads=list(threads or []),
        legal_cases=list(legal_cases or []),
        research_links=list(research_links or []),
        accounts=list(accounts or []),
    )

    if falkordb_client is None:
        try:
            from cianfhoghlaim.observability.falkordb_client import get_graph_cache  # type: ignore[import-not-found]
        except ImportError:
            logger.warning("falkordb_client_not_available_skipping_inbox_edges")
            return {
                "queries_executed": 0,
                "total_edges": 0,
                "queries": [],
                "stub": True,
            }
        falkordb_client = get_graph_cache().client

    total_edges = 0
    executed: list[str] = []
    for name, cypher, params in queries:
        try:
            stats = falkordb_client.execute(cypher, params)
            logger.info(
                "inbox_cross_archive_edge_rule_done",
                rule=name,
                edges_created=stats.get("relationships_created", 0),
            )
            total_edges += int(stats.get("relationships_created", 0))
            executed.append(name)
        except Exception as e:
            logger.warning(
                "inbox_cross_archive_edge_rule_failed",
                rule=name,
                error=str(e),
            )

    return {
        "queries_executed": len(executed),
        "total_edges": total_edges,
        "queries": executed,
        "stub": False,
    }


__all__ = [
    "_build_legal_thread_query",
    "_build_research_link_query",
    "_build_person_resolution_query",
    "_extract_display_name",
    "build_all_inbox_cross_archive_queries",
    "populate_inbox_cross_archive_edges",
]
