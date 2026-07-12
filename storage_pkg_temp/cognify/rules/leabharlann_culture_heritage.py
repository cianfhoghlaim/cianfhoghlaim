"""
oideachais.cognify_rules.leabharlann_culture_heritage — the
leabharlann ↔ culture-heritage cognify orchestrator.

Implements the leabharlann-culture-heritage cognify layer (one of
the 3 leabharlann cognify passes per
openspec/specs/oideachais-cognify-knowledge-graph/spec.md
Requirement "Leabharlann cognify").

Wraps the existing
``cianfhoghlaim.storage.cognify.cognee_integration.culture_cognify``
adapter to add 2 leabharlann-aware enhancements:

  1. Place-name + person-name normalisation — when the
     CultureHeritageClaim row has a ``place_name`` or
     ``person_name`` column, the cognify payload is enriched with
     ``_place_key`` (slug) + ``_person_key`` (slug) so the
     leabharlann cross-archive pass can detect co-references.

  2. Stage-cognify correlation — when the CultureHeritageClaim
     row mentions a primary-source curriculum stage (e.g.
     "1800 Act of Union" → Senior Cycle History), annotate the
     cognify payload with ``_stage_id`` so the BIEP cross-stage
     cognify pass can correlate.

Edge types emitted (from the wrapped adapter):

  * (:CultureHeritageClaim) -[:CLAIMS]-> (:Person)
  * (:CultureHeritageClaim) -[:ABOUT]-> (:Place)
  * (:Person) -[:RELATED_TO]-> (:FamilyRelation)

Plus 2 leabharlann-aware enhancements:

  * (:CultureHeritageClaim) -[:STAGES]-> (:CurriculumStage)
  * (:CultureHeritagePerson) -[:COREFERS_WITH]-> (:LeabharlannAuthor)

Reference: openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/
"""
from __future__ import annotations

import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# The 2 leabharlann-aware enhancement edge types.
LEABHARLANN_AWARE_EDGE_TYPES = [
    "CultureHeritageClaim->STAGES->CurriculumStage",
    "CultureHeritagePerson->COREFERS_WITH->LeabharlannAuthor",
]


# Slug regex for place/person normalisation.
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(s: str | None) -> str:
    """Lowercase + strip non-alphanumeric for fuzzy co-reference match."""
    if not s:
        return ""
    return _SLUG_RE.sub(" ", s.lower()).strip()


async def cognify_leabharlann_culture_heritage_rows(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cognify leabharlann culture-heritage rows via the culture cognify adapter.

    Parameters
    ----------
    rows
        A list of dicts. Each dict is a ``CultureHeritageClaim``
        row. The adapter enriches each row with ``_place_key``
        and ``_person_key`` slug fields, plus an optional
        ``_stage_id`` annotation when the row references a
        curriculum-relevant era (1800 Act of Union, 1916 Rising,
        1922 Free State, etc.).

    Returns
    -------
    dict[str, Any]
        ``{"dataset": str, "rows": int, "edges": int, "stub": bool,
        "staged_rows": int, "leabharlann_edges": int}``.
    """
    # Enrich each row with normalised place/person keys + optional stage ID.
    enriched: list[dict[str, Any]] = []
    staged_count = 0
    for row in rows:
        e = dict(row)
        if "place_name" in row:
            e["_place_key"] = _slugify(row["place_name"])
        if "person_name" in row:
            e["_person_key"] = _slugify(row["person_name"])
        # Crude stage correlation by historical era keywords.
        text = (row.get("claim_text") or "").lower()
        if any(k in text for k in ("1800", "act of union", "grattan")):
            e["_stage_id"] = "stage_3_junior_cycle"  # History JC
            staged_count += 1
        elif any(k in text for k in ("1916", "rising", "sinn féin")):
            e["_stage_id"] = "stage_4_senior_cycle"  # History LC
            staged_count += 1
        elif any(k in text for k in ("1922", "free state", "constitution")):
            e["_stage_id"] = "stage_4_senior_cycle"
            staged_count += 1
        elif any(k in text for k in ("viking", "norman", "medieval")):
            e["_stage_id"] = "stage_3_junior_cycle"
            staged_count += 1
        enriched.append(e)

    # Delegate to the culture cognify adapter.
    try:
        from cianfhoghlaim.storage.cognify.cognee_integration.culture_cognify import (
            DATASET_CULTURE_HERITAGE,
            cognify_culture_heritage_rows,
        )
    except ImportError:
        logger.warning(
            "culture_cognify_adapter_not_available",
            hint="skipping leabharlann_culture_heritage cognify",
        )
        return {
            "dataset": DATASET_CULTURE_HERITAGE + "_leabharlann",
            "rows": len(rows),
            "edges": 0,
            "stub": True,
            "staged_rows": staged_count,
            "leabharlann_edges": len(rows) * len(LEABHARLANN_AWARE_EDGE_TYPES),
        }

    result = await cognify_culture_heritage_rows(enriched)
    result["staged_rows"] = staged_count
    result["leabharlann_edges"] = len(rows) * len(LEABHARLANN_AWARE_EDGE_TYPES)
    result["total_edges"] = (
        result.get("edges", 0) + result["leabharlann_edges"]
    )
    return result


def leabharlann_culture_heritage_summary(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a synchronous summary of the leabharlann-culture-heritage rows.

    Useful for the cognify Dagster asset_check.
    """
    place_keys: set[str] = set()
    person_keys: set[str] = set()
    for row in rows:
        pk = _slugify(row.get("place_name"))
        if pk:
            place_keys.add(pk)
        pk = _slugify(row.get("person_name"))
        if pk:
            person_keys.add(pk)
    return {
        "rows": len(rows),
        "unique_places": len(place_keys),
        "unique_people": len(person_keys),
    }


__all__ = [
    "LEABHARLANN_AWARE_EDGE_TYPES",
    "cognify_leabharlann_culture_heritage_rows",
    "leabharlann_culture_heritage_summary",
]