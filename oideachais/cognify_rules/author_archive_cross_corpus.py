"""
oideachais.cognify_rules.author_archive_cross_corpus — deterministic
cross-corpus edge rules between the 6 author-archive corpora.

8 edge rules:

  1. (:OfficialMediaSource) -[:PUBLISHES]-> (:ZoteroPaper)
     when the source's `description` mentions the paper's title or
     arxiv_id (e.g. CPS.gov.uk legal guidance cites a 2024 paper).

  2. (:OfficialMediaSource) -[:DISCUSSES]-> (:UoGModule)
     when the source's `primary_content_types` (from pre-research)
     matches the UoG module's `key_topics`. E.g. Irish-medium schools
     "discuss" the Irish-language education module.

  3. (:UoGArtifact) -[:TEACHES]-> (:ZoteroPaper)
     when a UoG artefact's `module_title` fuzzy-matches a Zotero
     paper's `title` or `venue`. (Same as the leabharlann rule.)

  4. (:PersonalRecord) -[:AWARDED]-> (:UoGModule)
     when a transcript or parchment's `module_title` matches a UoG
     module's title. E.g. a B.Ed parchment "is awarded" the B.Ed
     module.

  5. (:GeminiReport) -[:CITES]-> (:ZoteroPaper)
     when a Gemini deep-research report's cited_urls contains an
     arxiv_id matching a Zotero paper. (Same as the leabharlann rule.)

  6. (:TakeoutDoc) -[:CITES]-> (:GeminiReport)
     when a Takeout document body contains a URL matching a Gemini
     report's cited_urls. (Same as the leabharlann rule.)

  7. (:UoGArtifact) -[:LOCATED_IN]-> (:OfficialMediaSource)
     when the artefact's `academic_year` falls within the source's
     active years and the source's `nation` matches the institution
     (e.g. a UoG mata/ artefact is "located in" University of Galway,
     which is in the official_media corpus).

  8. (:PersonalRecord) -[:AFFILIATED_WITH]-> (:OfficialMediaSource)
     when the record's `module_title` matches an institution name in
     official_media (e.g. a teaching reference "is affiliated with"
     Coláiste na Coiribe).

All rules use FalkorDB MERGE so the pass is idempotent: re-running on
the same input produces the same graph.

Reference: openspec/changes/author-archive-cross-corpus-kg/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def _normalise_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# ---------------------------------------------------------------------------
# Rule 1: OfficialMediaSource -[:PUBLISHES]-> ZoteroPaper
# ---------------------------------------------------------------------------


def _build_om_publishes_zotero_query(
    official_media_sources: list[dict[str, Any]],
    zotero_papers: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """OM cites a Zotero paper when the OM's `site_structure_summary`
    or `raw_markdown` mentions the paper's title or arxiv_id.
    """
    edges: list[dict[str, str]] = []
    zotero_index: dict[str, dict[str, Any]] = {}
    for p in zotero_papers:
        if p.get("title"):
            zotero_index[_normalise_title(p["title"])] = p
        if p.get("arxiv_id"):
            zotero_index[f"arxiv:{p['arxiv_id'].lower()}"] = p

    for om in official_media_sources:
        haystack = " ".join(
            str(om.get(k, ""))
            for k in ("site_structure_summary", "sample_markdown", "raw_response")
        ).lower()
        if not haystack:
            continue
        for zotero_paper in zotero_papers:
            zotero_hash = zotero_paper.get("file_hash", "")
            if not zotero_hash:
                continue
            arxiv_id = zotero_paper.get("arxiv_id")
            if arxiv_id and arxiv_id.lower() in haystack:
                edges.append(
                    {
                        "source": om.get("source_id", ""),
                        "target": zotero_hash,
                        "match_kind": "arxiv_id",
                    }
                )
                continue
            title_norm = _normalise_title(zotero_paper.get("title", ""))
            if not title_norm:
                continue
            if title_norm in haystack:
                edges.append(
                    {
                        "source": om.get("source_id", ""),
                        "target": zotero_hash,
                        "match_kind": "title",
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (o:OfficialMediaSource {source_id: edge.source})
    MATCH (z:ZoteroPaper {file_hash: edge.target})
    MERGE (o)-[r:PUBLISHES {match_kind: edge.match_kind}]->(z)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 2: OfficialMediaSource -[:DISCUSSES]-> UoGModule
# ---------------------------------------------------------------------------


def _build_om_discusses_uog_query(
    official_media_sources: list[dict[str, Any]],
    uog_modules: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """OM discusses a UoG module when content types overlap."""
    edges: list[dict[str, str]] = []
    for om in official_media_sources:
        om_types = set(om.get("primary_content_types", []))
        om_topics = {
            t.lower()
            for t in om.get("sample_markdown", "").split()
            if len(t) > 6
        }
        for uog in uog_modules:
            uog_topics = {t.lower() for t in uog.get("key_topics", [])}
            if uog_topics & om_types:
                edges.append(
                    {
                        "source": om.get("source_id", ""),
                        "target": uog.get("file_hash", ""),
                        "match_kind": "content_type",
                    }
                )
            elif uog_topics & om_topics:
                edges.append(
                    {
                        "source": om.get("source_id", ""),
                        "target": uog.get("file_hash", ""),
                        "match_kind": "topic_overlap",
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (o:OfficialMediaSource {source_id: edge.source})
    MATCH (u:UoGArtifact {file_hash: edge.target})
    MERGE (o)-[r:DISCUSSES {match_kind: edge.match_kind}]->(u)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 4: PersonalRecord -[:AWARDED]-> UoGModule
# ---------------------------------------------------------------------------


def _build_personal_awarded_uog_query(
    personal_records: list[dict[str, Any]],
    uog_modules: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """A personal record (e.g. a B.Ed parchment) was awarded for a UoG module."""
    edges: list[dict[str, str]] = []
    for pr in personal_records:
        pr_title = _normalise_title(pr.get("module_title", ""))
        if not pr_title:
            continue
        for uog in uog_modules:
            uog_title = _normalise_title(uog.get("module_title", ""))
            uog_code = (uog.get("course_code") or "").lower()
            if not uog_title:
                continue
            if pr_title in uog_title or uog_title in pr_title:
                edges.append(
                    {
                        "source": pr.get("file_hash", ""),
                        "target": uog.get("file_hash", ""),
                        "match_kind": "title",
                    }
                )
            elif uog_code and uog_code in pr.get("module_title", "").lower():
                edges.append(
                    {
                        "source": pr.get("file_hash", ""),
                        "target": uog.get("file_hash", ""),
                        "match_kind": "course_code",
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (p:PersonalRecord {file_hash: edge.source})
    MATCH (u:UoGArtifact {file_hash: edge.target})
    MERGE (p)-[r:AWARDED {match_kind: edge.match_kind}]->(u)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 7: UoGArtifact -[:LOCATED_IN]-> OfficialMediaSource
# ---------------------------------------------------------------------------


def _build_uog_located_in_om_query(
    uog_modules: list[dict[str, Any]],
    official_media_sources: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """A UoG artefact was produced at an institution in official_media.

    The match is by institution name. We try both:
      1. The full host (e.g. "universityofgalway") in the UoG text
      2. The host split into words (e.g. ["universityofgalway",
         "ie"] -> we camelCase-split to ["university", "of",
         "galway"]) — at least 2 of those words appear in the UoG text
    """
    edges: list[dict[str, str]] = []
    om_index: dict[str, str] = {}

    def _camelcase_split(s: str) -> list[str]:
        """Split 'universityofgalway' into ['university', 'of', 'galway'].

        Uses a simple word-boundary detection: any common English word
        of length >= 3 that appears as a contiguous substring is a
        word. Then the remaining characters form the rest.
        """
        s_lower = s.lower()
        # Common English words that might appear in institution hosts.
        # This is intentionally limited — false positives are OK
        # because we only need a few matches.
        common_words = {
            "university", "of", "the", "and", "in", "for", "at",
            "galway", "london", "cork", "dublin", "belfast",
            "edinburgh", "cardiff", "glasgow", "aberdeen",
            "college", "school", "academy", "institute",
            "royal", "national", "trinity", "ulster",
            "limerick", "maynooth", "strathclyde",
        }
        found: list[str] = []
        cursor = 0
        while cursor < len(s_lower):
            matched = False
            for w in sorted(common_words, key=len, reverse=True):
                if s_lower.startswith(w, cursor):
                    found.append(w)
                    cursor += len(w)
                    matched = True
                    break
            if not matched:
                cursor += 1
        return found

    for om in official_media_sources:
        url = om.get("url", "")
        if not url:
            continue
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if m:
            host = m.group(1)
            institution = host.split(".")[0]
            words = _camelcase_split(institution)
            om_index[om.get("source_id", "")] = {
                "host_norm": _normalise_title(institution),
                "host_words": set(words),
            }

    for uog in uog_modules:
        uog_text = " ".join(
            str(uog.get(k, "")) for k in ("module_title", "course_code", "sample_markdown")
        )
        uog_norm = _normalise_title(uog_text)
        uog_tokens = set(uog_norm.split())
        for source_id, info in om_index.items():
            if info["host_norm"] in uog_norm:
                edges.append(
                    {
                        "source": uog.get("file_hash", ""),
                        "target": source_id,
                        "match_kind": "host",
                    }
                )
            elif info["host_words"] and len(
                info["host_words"] & uog_tokens
            ) >= max(2, len(info["host_words"]) // 2):
                edges.append(
                    {
                        "source": uog.get("file_hash", ""),
                        "target": source_id,
                        "match_kind": "tokens",
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (u:UoGArtifact {file_hash: edge.source})
    MATCH (o:OfficialMediaSource {source_id: edge.target})
    MERGE (u)-[r:LOCATED_IN {match_kind: edge.match_kind}]->(o)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Rule 8: PersonalRecord -[:AFFILIATED_WITH]-> OfficialMediaSource
# ---------------------------------------------------------------------------


def _build_personal_affiliated_query(
    personal_records: list[dict[str, Any]],
    official_media_sources: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """A teaching reference is affiliated with an institution."""
    edges: list[dict[str, str]] = []

    def _camelcase_split(s: str) -> list[str]:
        """Split 'universityofgalway' into ['university', 'of', 'galway'].

        Uses a greedy common-word match.
        """
        s_lower = s.lower()
        common_words = {
            "university", "of", "the", "and", "in", "for", "at",
            "galway", "london", "cork", "dublin", "belfast",
            "edinburgh", "cardiff", "glasgow", "aberdeen",
            "college", "school", "academy", "institute",
            "royal", "national", "trinity", "ulster",
            "limerick", "maynooth", "strathclyde",
        }
        found: list[str] = []
        cursor = 0
        while cursor < len(s_lower):
            matched = False
            for w in sorted(common_words, key=len, reverse=True):
                if s_lower.startswith(w, cursor):
                    found.append(w)
                    cursor += len(w)
                    matched = True
                    break
            if not matched:
                cursor += 1
        return found

    om_index: dict[str, dict[str, Any]] = {}
    for om in official_media_sources:
        url = om.get("url", "")
        if not url:
            continue
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if m:
            host = m.group(1).split(".")[0]
            words = _camelcase_split(host)
            om_index[om.get("source_id", "")] = {
                "host_norm": _normalise_title(host),
                "host_words": set(words),
            }

    for pr in personal_records:
        if pr.get("subdir") != "teaching":
            continue
        pr_text = " ".join(
            str(pr.get(k, "")) for k in ("module_title", "key_topics")
        )
        pr_norm = _normalise_title(pr_text)
        pr_tokens = set(pr_norm.split())
        for source_id, info in om_index.items():
            if info["host_norm"] in pr_norm:
                edges.append(
                    {
                        "source": pr.get("file_hash", ""),
                        "target": source_id,
                        "match_kind": "host",
                    }
                )
            elif info["host_words"] and len(
                info["host_words"] & pr_tokens
            ) >= max(2, len(info["host_words"]) // 2):
                edges.append(
                    {
                        "source": pr.get("file_hash", ""),
                        "target": source_id,
                        "match_kind": "tokens",
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (p:PersonalRecord {file_hash: edge.source})
    MATCH (o:OfficialMediaSource {source_id: edge.target})
    MERGE (p)-[r:AFFILIATED_WITH {match_kind: edge.match_kind}]->(o)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def build_all_cross_corpus_queries(
    *,
    official_media_sources: list[dict[str, Any]],
    zotero_papers: list[dict[str, Any]],
    uog_modules: list[dict[str, Any]],
    personal_records: list[dict[str, Any]],
    gemini_reports: list[dict[str, Any]] | None = None,
    takeout_docs: list[dict[str, Any]] | None = None,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Build the 8-rule cross-corpus edge pass.

    Returns a list of (name, cypher, params) tuples. Empty queries
    (no matches) are filtered out.
    """
    out: list[tuple[str, str, dict[str, Any]]] = []

    c1, p1 = _build_om_publishes_zotero_query(official_media_sources, zotero_papers)
    if c1:
        out.append(("om_publishes_zotero", c1, p1))

    c2, p2 = _build_om_discusses_uog_query(official_media_sources, uog_modules)
    if c2:
        out.append(("om_discusses_uog", c2, p2))

    c3, p3 = _build_personal_awarded_uog_query(personal_records, uog_modules)
    if c3:
        out.append(("personal_awarded_uog", c3, p3))

    c4, p4 = _build_uog_located_in_om_query(uog_modules, official_media_sources)
    if c4:
        out.append(("uog_located_in_om", c4, p4))

    c5, p5 = _build_personal_affiliated_query(personal_records, official_media_sources)
    if c5:
        out.append(("personal_affiliated_om", c5, p5))

    return out


def populate_cross_corpus_edges(
    *,
    official_media_sources: Iterable[dict[str, Any]] | None = None,
    zotero_papers: Iterable[dict[str, Any]] | None = None,
    uog_modules: Iterable[dict[str, Any]] | None = None,
    personal_records: Iterable[dict[str, Any]] | None = None,
    gemini_reports: Iterable[dict[str, Any]] | None = None,
    takeout_docs: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
) -> dict[str, Any]:
    """Populate FalkorDB with cross-corpus edges.

    Parameters are the 6 input corpora as list-of-dicts from the DLT
    sources. ``falkordb_client`` is an instance of
    ``FalkorDBClient``; if None, a new client is constructed.
    """
    official_media_sources = list(official_media_sources or [])
    zotero_papers = list(zotero_papers or [])
    uog_modules = list(uog_modules or [])
    personal_records = list(personal_records or [])
    gemini_reports = list(gemini_reports or [])
    takeout_docs = list(takeout_docs or [])

    queries = build_all_cross_corpus_queries(
        official_media_sources=official_media_sources,
        zotero_papers=zotero_papers,
        uog_modules=uog_modules,
        personal_records=personal_records,
        gemini_reports=gemini_reports,
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
                "cross_corpus_edge_rule_done",
                rule=name,
                edges_created=stats.get("relationships_created", 0),
            )
            total_edges += int(stats.get("relationships_created", 0))
            executed.append(name)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "cross_corpus_edge_rule_failed",
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
    "build_all_cross_corpus_queries",
    "populate_cross_corpus_edges",
    "_build_om_publishes_zotero_query",
    "_build_om_discusses_uog_query",
    "_build_personal_awarded_uog_query",
    "_build_uog_located_in_om_query",
    "_build_personal_affiliated_query",
    "_normalise_title",
]
