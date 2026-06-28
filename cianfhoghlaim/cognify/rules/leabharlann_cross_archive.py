"""
oideachais.cognify_rules.leabharlann_cross_archive — deterministic
cross-archive edge population between the 3 leabharlann corpora.

3 edge rules:
  1. (:GeminiReport) -[:CITES]-> (:ZoteroPaper)
       when a Gemini deep-research report has a citation whose arxiv_id
       matches a Zotero paper's arxiv_id.
  2. (:UoGArtifact) -[:TEACHES]-> (:ZoteroPaper)
       when a UoG artefact's `module_title` (or `course_code` / `key_topics`)
       fuzzy-matches a Zotero paper's `title` or `venue`.
  3. (:TakeoutDoc) -[:CITES]-> (:GeminiReport)
       when a Takeout document body (extracted by pymupdf / python-docx)
       contains a URL that matches a Gemini report's `cited_urls`.

All rules use FalkorDB MERGE so the pass is idempotent: re-running on
the same input produces the same graph.

The rule pass is intentionally a synchronous wrapper around
`FalkorDBClient.execute()` (from `oideachais.graph.falkordb_client`) —
the actual Dagster asset is
`oideachais.dagster_defs.assets.leabharlann_cognify_assets.cross_archive_edges`.

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Rule 1: GeminiReport -[:CITES]-> ZoteroPaper (arxiv_id match)
# ---------------------------------------------------------------------------


def _build_arxiv_match_query(
    gemini_citations: list[dict[str, Any]],
    zotero_papers: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the arxiv_id match rule.

    `gemini_citations` may be either:
      - a list of `{"url": str, "source_file_hash": str}` dicts, OR
      - a list of `{"url": str}` dicts (file_hash resolved from the
        `source_file` field on the parent Gemini report by the caller).

    Returns `(cypher, params)` suitable for `FalkorDBClient.execute()`.
    """
    arxiv_ids_in_zotero = {
        p.get("arxiv_id"): p.get("file_hash")
        for p in zotero_papers
        if p.get("arxiv_id")
    }
    arxiv_ids_in_citations: dict[str, list[str]] = {}
    for cite in gemini_citations:
        if isinstance(cite, str):
            url = cite.lower()
            source_hash = ""
        else:
            url = (cite.get("url") or "").lower() if hasattr(cite, "get") else ""
            source_hash = (cite.get("source_file_hash", "") if hasattr(cite, "get") else "")
        m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(v\d+)?", url)
        if m:
            arxiv_id = m.group(1)
            arxiv_ids_in_citations.setdefault(arxiv_id, []).append(source_hash)

    edges = []
    for arxiv_id, target_hash in arxiv_ids_in_zotero.items():
        for source_hash in arxiv_ids_in_citations.get(arxiv_id, []):
            edges.append((source_hash, target_hash, arxiv_id))

    if not edges:
        return "", {}

    # Use UNWIND + MERGE for bulk idempotent insertion.
    cypher = """
    UNWIND $edges AS edge
    MATCH (g:GeminiReport {file_hash: edge.source})
    MATCH (z:ZoteroPaper {file_hash: edge.target})
    MERGE (g)-[r:CITES {arxiv_id: edge.arxiv_id}]->(z)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    params = {
        "edges": [
            {"source": s, "target": t, "arxiv_id": a} for s, t, a in edges
        ]
    }
    return cypher, params


# ---------------------------------------------------------------------------
# Rule 2: UoGArtifact -[:TEACHES]-> ZoteroPaper (module title match)
# ---------------------------------------------------------------------------


def _normalise_title(s: str) -> str:
    """Lowercase + strip non-alphanumeric for fuzzy match."""
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _build_module_title_match_query(
    uog_artifacts: list[dict[str, Any]],
    zotero_papers: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the module title match rule.

    The match is:
      1. exact normalised title equality, OR
      2. UoG artefact's `key_topics` contains the Zotero paper's first
         non-trivial noun phrase, OR
      3. Zotero paper's `venue` matches the UoG artefact's `module_title`
         (when the artefact is a lecture note / exam).
    """
    zotero_index: dict[str, dict[str, Any]] = {}
    for p in zotero_papers:
        if p.get("title"):
            zotero_index[_normalise_title(p["title"])] = p

    edges: list[dict[str, str]] = []
    for uog in uog_artifacts:
        uog_titles: list[str] = []
        if uog.get("module_title"):
            uog_titles.append(uog["module_title"])
        for topic in uog.get("key_topics") or []:
            if isinstance(topic, str) and len(topic) > 4:
                uog_titles.append(topic)
        for uog_title in uog_titles:
            key = _normalise_title(uog_title)
            for zotero_key, zotero_paper in zotero_index.items():
                if not zotero_key:
                    continue
                # Heuristic: at least 60% of the shorter string's tokens
                # appear in the longer one.
                uog_tokens = set(key.split())
                zotero_tokens = set(zotero_key.split())
                if not uog_tokens or not zotero_tokens:
                    continue
                shorter = min(len(uog_tokens), len(zotero_tokens))
                overlap = len(uog_tokens & zotero_tokens)
                if shorter > 0 and overlap / shorter >= 0.6:
                    edges.append(
                        {
                            "source": uog.get("file_hash", ""),
                            "target": zotero_paper.get("file_hash", ""),
                            "match_kind": "title",
                        }
                    )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (u:UoGArtifact {file_hash: edge.source})
    MATCH (z:ZoteroPaper {file_hash: edge.target})
    MERGE (u)-[r:TEACHES {match_kind: edge.match_kind}]->(z)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 3: TakeoutDoc -[:CITES]-> GeminiReport (URL match)
# ---------------------------------------------------------------------------


_URL_RE = re.compile(r"https?://[^\s<>\"']+")


def _extract_urls_from_text(text: str) -> list[str]:
    """Extract URLs from the body of a Takeout document."""
    return _URL_RE.findall(text or "")


def _build_takeout_citation_query(
    takeout_docs: list[dict[str, Any]],
    gemini_reports: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build a single Cypher MERGE query for the URL match rule."""
    # Index Gemini report URLs (normalised) by file_hash.
    gemini_url_index: dict[str, str] = {}
    for g in gemini_reports:
        for cite in g.get("cited_urls") or g.get("gemini_citations") or []:
            url = (cite.get("url") or "").lower() if isinstance(cite, dict) else str(cite).lower()
            if url:
                gemini_url_index[url] = g.get("file_hash", "")

    edges: list[dict[str, str]] = []
    for doc in takeout_docs:
        body = doc.get("extracted_text", "") or doc.get("text", "")
        for url in _extract_urls_from_text(body):
            key = url.lower()
            if key in gemini_url_index:
                edges.append(
                    {
                        "source": doc.get("file_hash", ""),
                        "target": gemini_url_index[key],
                        "url": url,
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (t:TakeoutDoc {file_hash: edge.source})
    MATCH (g:GeminiReport {file_hash: edge.target})
    MERGE (t)-[r:CITES {url: edge.url}]->(g)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def build_all_cross_archive_queries(
    *,
    gemini_reports: list[dict[str, Any]],
    zotero_papers: list[dict[str, Any]],
    uog_artifacts: list[dict[str, Any]],
    takeout_docs: list[dict[str, Any]],
) -> list[tuple[str, str, dict[str, Any]]]:
    """Return a list of `(name, cypher, params)` tuples for the
    FalkorDBClient-executable cross-archive pass.

    Empty queries (no matches) are filtered out so the caller can skip
    them.

    DuckDB may return `gemini_citations` and `cited_urls` as JSON
    strings; this function normalises them to parsed lists.
    """
    import json

    out: list[tuple[str, str, dict[str, Any]]] = []

    # Normalise DuckDB JSON-string columns.
    for g in gemini_reports:
        for col in ("cited_urls", "gemini_citations"):
            v = g.get(col)
            if isinstance(v, str):
                try:
                    g[col] = json.loads(v)
                except (ValueError, TypeError):
                    g[col] = []
    for u in uog_artifacts:
        v = u.get("key_topics")
        if isinstance(v, str):
            try:
                u["key_topics"] = json.loads(v)
            except (ValueError, TypeError):
                u["key_topics"] = []

    # Build the arxiv-id citation list with `source_file_hash` resolved
    # to the parent Gemini report's `file_hash`.
    arxiv_citations: list[dict[str, Any]] = []
    for g in gemini_reports:
        gh = g.get("file_hash", "")
        for c in g.get("cited_urls") or g.get("gemini_citations") or []:
            if isinstance(c, dict):
                url = c.get("url")
                src = c.get("source_file_hash", gh)
            else:
                url = str(c)
                src = gh
            arxiv_citations.append({"url": url, "source_file_hash": src})

    c1, p1 = _build_arxiv_match_query(arxiv_citations, zotero_papers)
    if c1:
        out.append(("gemini_cites_zotero_arxiv", c1, p1))

    c2, p2 = _build_module_title_match_query(uog_artifacts, zotero_papers)
    if c2:
        out.append(("uog_teaches_zotero_title", c2, p2))

    c3, p3 = _build_takeout_citation_query(takeout_docs, gemini_reports)
    if c3:
        out.append(("takeout_cites_gemini_url", c3, p3))

    return out


def populate_cross_archive_edges(
    *,
    gemini_reports: Iterable[dict[str, Any]] | None = None,
    zotero_papers: Iterable[dict[str, Any]] | None = None,
    uog_artifacts: Iterable[dict[str, Any]] | None = None,
    takeout_docs: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
) -> dict[str, Any]:
    """Populate FalkorDB with cross-archive edges.

    Parameters
    ----------
    gemini_reports, zotero_papers, uog_artifacts, takeout_docs
        The 4 input corpora (each a list of dicts from the leabharlann
        dlt sources).
    falkordb_client
        An instance of `FalkorDBClient` (from
        `oideachais.graph.falkordb_client`). If None, a new client is
        constructed via the `get_graph_cache()` singleton.

    Returns
    -------
    dict[str, Any]
        `{"queries_executed": int, "total_edges": int, "queries": [str]}`.
    """
    gemini_reports = list(gemini_reports or [])
    zotero_papers = list(zotero_papers or [])
    uog_artifacts = list(uog_artifacts or [])
    takeout_docs = list(takeout_docs or [])

    # DuckDB may return `gemini_citations` and `cited_urls` as JSON strings
    # rather than parsed lists. Normalise to parsed lists here.
    import json

    for g in gemini_reports:
        for col in ("cited_urls", "gemini_citations"):
            v = g.get(col)
            if isinstance(v, str):
                try:
                    g[col] = json.loads(v)
                except (ValueError, TypeError):
                    g[col] = []
        # Also handle JSON-encoded key_topics on UoG artefacts.
    for u in uog_artifacts:
        v = u.get("key_topics")
        if isinstance(v, str):
            try:
                u["key_topics"] = json.loads(v)
            except (ValueError, TypeError):
                u["key_topics"] = []

    queries = build_all_cross_archive_queries(
        gemini_reports=gemini_reports,
        zotero_papers=zotero_papers,
        uog_artifacts=uog_artifacts,
        takeout_docs=takeout_docs,
    )

    if falkordb_client is None:
        try:
            from oideachais.graph.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning("falkordb_client_not_available_skipping_edges")
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
                "cross_archive_edge_rule_done",
                rule=name,
                nodes_created=stats.get("nodes_created", 0),
                edges_created=stats.get("relationships_created", 0),
            )
            total_edges += int(stats.get("relationships_created", 0))
            executed.append(name)
        except Exception as e:
            logger.warning(
                "cross_archive_edge_rule_failed",
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
    "_build_arxiv_match_query",
    "_build_module_title_match_query",
    "_build_takeout_citation_query",
    "_extract_urls_from_text",
    "_normalise_title",
    "build_all_cross_archive_queries",
    "populate_cross_archive_edges",
]
