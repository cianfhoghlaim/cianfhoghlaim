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

import json
import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# URL regex used for the Takeout-citation rule (Rule 6)
_URL_RE = re.compile(r"https?://[^\s<>\"']+")


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
# Rule 3: UoGArtifact -[:TEACHES]-> ZoteroPaper (module title match)
# Copied from oideachais/cognify_rules/leabharlann_cross_archive.py
# ---------------------------------------------------------------------------


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
# Rule 5: GeminiReport -[:CITES]-> ZoteroPaper (arxiv_id match)
# Copied from oideachais/cognify_rules/leabharlann_cross_archive.py
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
# Rule 6: TakeoutDoc -[:CITES]-> GeminiReport (URL match)
# Copied from oideachais/cognify_rules/leabharlann_cross_archive.py
# ---------------------------------------------------------------------------


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

    # Normalise DuckDB JSON-string columns so the rule matchers can
    # iterate the lists without manual JSON parsing.
    for g in (gemini_reports or []):
        for col in ("cited_urls", "gemini_citations"):
            v = g.get(col)
            if isinstance(v, str):
                try:
                    g[col] = json.loads(v)
                except (ValueError, TypeError):
                    g[col] = []
    for u in uog_modules:
        v = u.get("key_topics")
        if isinstance(v, str):
            try:
                u["key_topics"] = json.loads(v)
            except (ValueError, TypeError):
                u["key_topics"] = []

    # Build the arxiv-id citation list with `source_file_hash` resolved
    # to the parent Gemini report's `file_hash`.
    arxiv_citations: list[dict[str, Any]] = []
    for g in (gemini_reports or []):
        gh = g.get("file_hash", "")
        for c in g.get("cited_urls") or g.get("gemini_citations") or []:
            if isinstance(c, dict):
                url = c.get("url")
                src = c.get("source_file_hash", gh)
            else:
                url = str(c)
                src = gh
            arxiv_citations.append({"url": url, "source_file_hash": src})

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

    # Rules 3, 5, 6 — newly added by complete-cognee-knowledge-graph
    c6, p6 = _build_module_title_match_query(uog_modules, zotero_papers)
    if c6:
        out.append(("uog_teaches_zotero_title", c6, p6))

    c7, p7 = _build_arxiv_match_query(arxiv_citations, zotero_papers)
    if c7:
        out.append(("gemini_cites_zotero_arxiv", c7, p7))

    c8, p8 = _build_takeout_citation_query(takeout_docs or [], gemini_reports or [])
    if c8:
        out.append(("takeout_cites_gemini_url", c8, p8))

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
        except Exception as e:
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
    "_build_arxiv_match_query",
    # Newly added in complete-cognee-knowledge-graph
    "_build_module_title_match_query",
    "_build_om_discusses_uog_query",
    "_build_om_publishes_zotero_query",
    "_build_personal_affiliated_query",
    "_build_personal_awarded_uog_query",
    "_build_takeout_citation_query",
    "_build_uog_located_in_om_query",
    "_extract_urls_from_text",
    "_normalise_title",
    "build_all_cross_corpus_queries",
    "populate_cross_corpus_edges",
]
