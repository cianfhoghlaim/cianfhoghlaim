"""
oideachais.cognify_rules.cross_archive_biep_edges — the 3 BIEP
cross-archive FalkorDB edge rules per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "Cross-archive edges (FalkorDB)".

This module adds 3 new cross-archive edge rules ON TOP OF the
existing 3 leabharlann-internal rules in
``leabharlann_cross_archive.py`` (CITES-arxiv, TEACHES-title,
CITES-URL):

  Edge 1: BIEP -> leabharlann
  ---------------------------
  ``(:SCLearningOutcome) -[:REFERENCED_IN]-> (:LeabharlannDoc)``
  when an SC learning outcome mentions a book / zotero paper /
  takeout document that exists in the leabharlann corpus. Match
  heuristic: 60% token overlap between the LO's ``key_topics``
  list and the leabharlann doc's ``title`` / ``key_phrases``.

  Edge 2: BIEP -> official-media
  ------------------------------
  ``(:LCSubject) -[:ANNOUNCED_BY]-> (:OfficialMediaSource)``
  when an LC subject's official NCCA / DES announcement has
  been mirrored by an official-media source (instagram export,
  fediverse account, companies house entity). Match heuristic:
  exact subject_code match (e.g. LC code "LC-CHEM" ↔ official
  source ``topic_tags`` containing "LC-CHEM").

  Edge 3: leabharlann -> culture-heritage
  ---------------------------------------
  ``(:LeabharlannAuthor) -[:COREFERS_WITH]-> (:CultureHeritagePerson)``
  when a leabharlann author row's ``surname_forename_slug`` matches
  a culture-heritage claim's ``_person_key`` slug. Plus the
  reciprocal edge:
  ``(:LeabharlannDoc) -[:ABOUT]-> (:CultureHeritagePlace)``
  when a leabharlann doc's ``place_key`` matches a culture-heritage
  claim's ``_place_key`` slug.

All 3 rules use FalkorDB MERGE so the pass is idempotent.
Empty match lists return ``("", {})`` so the caller can skip
the empty MERGE.

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(s: str | None) -> str:
    """Lowercase + strip non-alphanumeric for fuzzy co-reference match."""
    if not s:
        return ""
    return _SLUG_RE.sub(" ", s.lower()).strip()


def _token_overlap(a: str, b: str) -> float:
    """Token-Jaccard overlap in [0.0, 1.0]."""
    a_tokens = set(_slugify(a).split())
    b_tokens = set(_slugify(b).split())
    if not a_tokens or not b_tokens:
        return 0.0
    union = a_tokens | b_tokens
    if not union:
        return 0.0
    return len(a_tokens & b_tokens) / len(union)


# ---------------------------------------------------------------------------
# Edge 1: BIEP -> leabharlann  (SCLearningOutcome -[:REFERENCED_IN]-> LeabharlannDoc)
# ---------------------------------------------------------------------------


def build_biep_references_leabharlann_query(
    sc_learning_outcomes: list[dict[str, Any]],
    leabharlann_docs: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.6,
) -> tuple[str, dict[str, Any]]:
    """Build the Cypher MERGE query for the BIEP -> leabharlann edge.

    Match heuristic: 60% token overlap (configurable) between the
    ``key_topics`` list on the SC LO and the ``title`` or
    ``key_phrases`` on the leabharlann doc.
    """
    if not sc_learning_outcomes or not leabharlann_docs:
        return "", {}

    # Index leabharlann docs by their titles + key_phrases.
    doc_index: list[tuple[str, dict[str, Any]]] = []
    for doc in leabharlann_docs:
        title = doc.get("title") or doc.get("name") or ""
        if title:
            doc_index.append((title, doc))
        for kp in doc.get("key_phrases") or []:
            if isinstance(kp, str) and len(kp) > 4:
                doc_index.append((kp, doc))

    edges: list[dict[str, Any]] = []
    for lo in sc_learning_outcomes:
        source = lo.get("learning_outcome_id") or lo.get("id") or ""
        if not source:
            continue
        topics = lo.get("key_topics") or []
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            if not isinstance(topic, str) or not topic:
                continue
            best_sim = 0.0
            best_doc: dict[str, Any] | None = None
            for doc_title, doc in doc_index:
                sim = _token_overlap(topic, doc_title)
                if sim > best_sim:
                    best_sim = sim
                    best_doc = doc
            if best_sim >= fuzzy_threshold and best_doc is not None:
                edges.append(
                    {
                        "source": source,
                        "target": best_doc.get("file_hash") or best_doc.get("id") or "",
                        "match_kind": "key_topic_overlap",
                        "match_confidence": round(best_sim, 4),
                    }
                )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (lo:SCLearningOutcome {learning_outcome_id: edge.source})
    MATCH (d:LeabharlannDoc {file_hash: edge.target})
    MERGE (lo)-[r:REFERENCED_IN {match_kind: edge.match_kind, match_confidence: edge.match_confidence}]->(d)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Edge 2: BIEP -> official-media  (LCSubject -[:ANNOUNCED_BY]-> OfficialMediaSource)
# ---------------------------------------------------------------------------


def build_lc_subject_announced_by_query(
    lc_subjects: list[dict[str, Any]],
    official_media_sources: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Build the Cypher MERGE query for the BIEP -> official-media edge.

    Match heuristic: exact subject_code match between an LC subject
    row's ``subject_code`` (e.g. ``"LC-CHEM"``) and an
    official-media source's ``topic_tags`` list.
    """
    if not lc_subjects or not official_media_sources:
        return "", {}

    # Index official-media sources by topic_tags (set intersection lookup).
    sources_by_tag: dict[str, list[dict[str, Any]]] = {}
    for src in official_media_sources:
        tags = src.get("topic_tags") or src.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag_upper = tag.strip().upper()
            if tag_upper:
                sources_by_tag.setdefault(tag_upper, []).append(src)

    edges: list[dict[str, Any]] = []
    for subject in lc_subjects:
        code = (subject.get("subject_code") or "").strip().upper()
        if not code:
            continue
        source = subject.get("subject_code")  # use code as node id
        for src in sources_by_tag.get(code, []):
            edges.append(
                {
                    "source": source,
                    "target": src.get("source_id") or src.get("url") or src.get("id") or "",
                    "match_kind": "subject_code_exact",
                    "match_confidence": 1.0,
                }
            )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (s:LCSubject {subject_code: edge.source})
    MATCH (o:OfficialMediaSource {source_id: edge.target})
    MERGE (s)-[r:ANNOUNCED_BY {match_kind: edge.match_kind, match_confidence: edge.match_confidence}]->(o)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Edge 3: leabharlann -> culture-heritage
# ---------------------------------------------------------------------------


def build_leabharlann_corefers_culture_query(
    leabharlann_authors: list[dict[str, Any]],
    culture_heritage_people: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    """Build the Cypher MERGE query for the people co-reference edge.

    Match heuristic: ``surname_forename_slug`` match between the
    leabharlann author and the culture-heritage person's
    ``_person_key`` slug.
    """
    if not leabharlann_authors or not culture_heritage_people:
        return "", {}

    culture_keys: dict[str, dict[str, Any]] = {}
    for person in culture_heritage_people:
        key = _slugify(
            person.get("_person_key")
            or person.get("person_name")
            or person.get("name")
        )
        if key:
            culture_keys[key] = person

    edges: list[dict[str, Any]] = []
    for author in leabharlann_authors:
        author_key = _slugify(
            author.get("surname_forename_slug")
            or author.get("slug")
            or f"{author.get('surname', '')} {author.get('forename', '')}"
        )
        if not author_key:
            continue
        match = culture_keys.get(author_key)
        if match is None:
            # Try fuzzy match fallback.
            best_sim = 0.0
            best_match: dict[str, Any] | None = None
            for ckey, person in culture_keys.items():
                sim = _token_overlap(author_key, ckey)
                if sim > best_sim:
                    best_sim = sim
                    best_match = person
            if best_sim >= fuzzy_threshold:
                match = best_match

        if match is not None:
            edges.append(
                {
                    "source": author.get("file_hash") or author.get("id") or "",
                    "target": match.get("id") or match.get("_person_key") or "",
                    "match_kind": "slug_match",
                    "match_confidence": 1.0,
                }
            )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (a:LeabharlannAuthor {file_hash: edge.source})
    MATCH (p:CultureHeritagePerson {id: edge.target})
    MERGE (a)-[r:COREFERS_WITH {match_kind: edge.match_kind, match_confidence: edge.match_confidence}]->(p)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


def build_leabharlann_about_culture_place_query(
    leabharlann_docs: list[dict[str, Any]],
    culture_heritage_places: list[dict[str, Any]],
    *,
    fuzzy_threshold: float = 0.85,
) -> tuple[str, dict[str, Any]]:
    """Build the Cypher MERGE query for the place co-reference edge.

    Match heuristic: ``place_key`` match between a leabharlann
    doc's ``place_key`` (or derived from ``place_name``) and a
    culture-heritage place's ``_place_key`` slug.
    """
    if not leabharlann_docs or not culture_heritage_places:
        return "", {}

    place_keys: dict[str, dict[str, Any]] = {}
    for place in culture_heritage_places:
        key = _slugify(
            place.get("_place_key")
            or place.get("place_name")
            or place.get("name")
        )
        if key:
            place_keys[key] = place

    edges: list[dict[str, Any]] = []
    for doc in leabharlann_docs:
        doc_key = _slugify(
            doc.get("place_key")
            or doc.get("place_name")
        )
        if not doc_key:
            continue
        match = place_keys.get(doc_key)
        if match is None:
            best_sim = 0.0
            best_match: dict[str, Any] | None = None
            for pkey, place in place_keys.items():
                sim = _token_overlap(doc_key, pkey)
                if sim > best_sim:
                    best_sim = sim
                    best_match = place
            if best_sim >= fuzzy_threshold:
                match = best_match

        if match is not None:
            edges.append(
                {
                    "source": doc.get("file_hash") or doc.get("id") or "",
                    "target": match.get("id") or match.get("_place_key") or "",
                    "match_kind": "place_slug_match",
                    "match_confidence": 1.0,
                }
            )

    if not edges:
        return "", {}

    cypher = """
    UNWIND $edges AS edge
    MATCH (d:LeabharlannDoc {file_hash: edge.source})
    MATCH (p:CultureHeritagePlace {id: edge.target})
    MERGE (d)-[r:ABOUT {match_kind: edge.match_kind, match_confidence: edge.match_confidence}]->(p)
    ON CREATE SET r.created_at = timestamp()
    RETURN count(r) AS edges_created
    """
    return cypher, {"edges": edges}


# ---------------------------------------------------------------------------
# Public entry point — execute all 3 BIEP cross-archive edge rules
# ---------------------------------------------------------------------------


def build_all_biep_cross_archive_queries(
    *,
    sc_learning_outcomes: Iterable[dict[str, Any]] | None = None,
    leabharlann_docs: Iterable[dict[str, Any]] | None = None,
    lc_subjects: Iterable[dict[str, Any]] | None = None,
    official_media_sources: Iterable[dict[str, Any]] | None = None,
    leabharlann_authors: Iterable[dict[str, Any]] | None = None,
    culture_heritage_people: Iterable[dict[str, Any]] | None = None,
    leabharlann_docs_for_places: Iterable[dict[str, Any]] | None = None,
    culture_heritage_places: Iterable[dict[str, Any]] | None = None,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Build all 3 BIEP cross-archive edge queries.

    Returns a list of ``(name, cypher, params)`` tuples for the
    FalkorDBClient-executable cross-archive pass. Empty queries
    (no matches) are filtered out.
    """
    out: list[tuple[str, str, dict[str, Any]]] = []

    c1, p1 = build_biep_references_leabharlann_query(
        list(sc_learning_outcomes or []),
        list(leabharlann_docs or []),
    )
    if c1:
        out.append(("biep_references_leabharlann", c1, p1))

    c2, p2 = build_lc_subject_announced_by_query(
        list(lc_subjects or []),
        list(official_media_sources or []),
    )
    if c2:
        out.append(("lc_subject_announced_by_official_media", c2, p2))

    c3, p3 = build_leabharlann_corefers_culture_query(
        list(leabharlann_authors or []),
        list(culture_heritage_people or []),
    )
    if c3:
        out.append(("leabharlann_author_corefers_culture_heritage_person", c3, p3))

    c4, p4 = build_leabharlann_about_culture_place_query(
        list(leabharlann_docs_for_places or []),
        list(culture_heritage_places or []),
    )
    if c4:
        out.append(("leabharlann_doc_about_culture_heritage_place", c4, p4))

    return out


def populate_biep_cross_archive_edges(
    *,
    sc_learning_outcomes: Iterable[dict[str, Any]] | None = None,
    leabharlann_docs: Iterable[dict[str, Any]] | None = None,
    lc_subjects: Iterable[dict[str, Any]] | None = None,
    official_media_sources: Iterable[dict[str, Any]] | None = None,
    leabharlann_authors: Iterable[dict[str, Any]] | None = None,
    culture_heritage_people: Iterable[dict[str, Any]] | None = None,
    leabharlann_docs_for_places: Iterable[dict[str, Any]] | None = None,
    culture_heritage_places: Iterable[dict[str, Any]] | None = None,
    falkordb_client: Any = None,
) -> dict[str, Any]:
    """Populate the 3 BIEP cross-archive edges in FalkorDB.

    Returns
    -------
    dict[str, Any]
        ``{"queries_executed": int, "total_edges": int, "queries": [str]}``.
    """
    queries = build_all_biep_cross_archive_queries(
        sc_learning_outcomes=sc_learning_outcomes,
        leabharlann_docs=leabharlann_docs,
        lc_subjects=lc_subjects,
        official_media_sources=official_media_sources,
        leabharlann_authors=leabharlann_authors,
        culture_heritage_people=culture_heritage_people,
        leabharlann_docs_for_places=leabharlann_docs_for_places,
        culture_heritage_places=culture_heritage_places,
    )

    if falkordb_client is None:
        try:
            from cianfhoghlaim.storage.falkordb_client import get_graph_cache
        except ImportError:
            logger.warning(
                "falkordb_client_not_available_skipping_biep_edges",
                hint="skipping 3 BIEP cross-archive edges",
            )
            return {
                "queries_executed": 0,
                "total_edges": 0,
                "queries": [name for name, _, _ in queries],
                "stub": True,
            }
        falkordb_client = get_graph_cache().client

    total_edges = 0
    executed: list[str] = []
    for name, cypher, params in queries:
        try:
            stats = falkordb_client.execute(cypher, params)
            logger.info(
                "biep_cross_archive_edge_rule_done",
                rule=name,
                nodes_created=stats.get("nodes_created", 0),
                edges_created=stats.get("relationships_created", 0),
            )
            total_edges += int(stats.get("relationships_created", 0))
            executed.append(name)
        except Exception as e:
            logger.warning(
                "biep_cross_archive_edge_rule_failed",
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
    "build_all_biep_cross_archive_queries",
    "build_biep_references_leabharlann_query",
    "build_lc_subject_announced_by_query",
    "build_leabharlann_about_culture_place_query",
    "build_leabharlann_corefers_culture_query",
    "populate_biep_cross_archive_edges",
]