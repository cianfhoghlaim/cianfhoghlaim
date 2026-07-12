"""Dagster L2 — Gaois BAML extraction assets.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Extracts BAML-typed records from the ingested Gaois DuckLake
tables (Téarma + Logainm + Ainm), dispatching through the shared
LlamaSwap routing table (`cianfhoghlaim.meaisinfhoghlaim.models.routing`).

Reference: openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Shared routing table
try:
    from cianfhoghlaim.meaisinfhoghlaim.models.routing import (  # type: ignore[import-not-found]
        route_language,
        get_baml_client,
    )
    _ROUTING_AVAILABLE = True
except Exception:
    _ROUTING_AVAILABLE = False
    route_language = None  # type: ignore[assignment]
    get_baml_client = None  # type: ignore[assignment]


# BAML client (graceful degradation)
try:
    from baml_client import b  # type: ignore[import-not-found]
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


def extract_tearma_terms(
    term_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Téarma terms.

    Args:
        term_rows: List of dicts from `oideachais.celtic.gaois.tearma_terms`
        language: The language partition (ga or en)

    Returns:
        List of BAML-extracted Téarma term dicts
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_tearma_terms")
        return []

    client_name = get_baml_client("gaois", language) if _ROUTING_AVAILABLE else "LitellmClient"
    logger.info("extract_tearma_terms routing=%s language=%s n=%d", client_name, language, len(term_rows))

    results = []
    for row in term_rows:
        try:
            # BAML extraction function name (per baml/celtic/gaois/tearma.baml)
            extracted = b.ExtractTearmaTerm(
                term_en=row.get("term_en", ""),
                term_ga=row.get("term_ga", ""),
                domain=row.get("domain", ""),
                description=row.get("description", ""),
            )
            results.append({
                "term_en": row.get("term_en"),
                "term_ga": row.get("term_ga"),
                "domain": row.get("domain"),
                "extracted": extracted,
                "language": language,
                "routing_client": client_name,
            })
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("tearma_extract_failed: %s", exc)
            continue
    return results


def extract_logainm_places(
    place_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Logainm places."""
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_logainm_places")
        return []

    client_name = get_baml_client("gaois", language) if _ROUTING_AVAILABLE else "LitellmClient"
    logger.info("extract_logainm_places routing=%s language=%s n=%d", client_name, language, len(place_rows))

    results = []
    for row in place_rows:
        try:
            extracted = b.ExtractLogainmPlace(
                place_name=row.get("place_name", ""),
                place_name_ga=row.get("place_name_ga", ""),
                county=row.get("county", ""),
                category=row.get("category", ""),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
            )
            results.append({
                "place_name": row.get("place_name"),
                "place_name_ga": row.get("place_name_ga"),
                "county": row.get("county"),
                "category": row.get("category"),
                "extracted": extracted,
                "language": language,
                "routing_client": client_name,
            })
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("logainm_extract_failed: %s", exc)
            continue
    return results


def extract_ainm_biographies(
    bio_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for Ainm biographies."""
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_ainm_biographies")
        return []

    client_name = get_baml_client("gaois", language) if _ROUTING_AVAILABLE else "LitellmClient"
    logger.info("extract_ainm_biographies routing=%s language=%s n=%d", client_name, language, len(bio_rows))

    results = []
    for row in bio_rows:
        try:
            extracted = b.ExtractAinmBiography(
                full_name=row.get("full_name", ""),
                forename=row.get("forename", ""),
                surname=row.get("surname", ""),
                profession=row.get("profession", ""),
                biography=row.get("biography", ""),
                birth_year=row.get("birth_year"),
                death_year=row.get("death_year"),
            )
            results.append({
                "ainm_id": row.get("ainm_id"),
                "full_name": row.get("full_name"),
                "extracted": extracted,
                "language": language,
                "routing_client": client_name,
            })
        except Exception as exc:  # noqa: BLE001 - defensive
            logger.warning("ainm_extract_failed: %s", exc)
            continue
    return results


__all__ = [
    "extract_tearma_terms",
    "extract_logainm_places",
    "extract_ainm_biographies",
]