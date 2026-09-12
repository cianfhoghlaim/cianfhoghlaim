"""ciancheiltis Phase 2 (en-ga / Republic of Ireland) BAML extraction adapter.

Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.6). Mirrors the
shape of `baml_src/british_isles/_shared/ciancheiltis_extraction.py`:
wraps the 3 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractIrelandGAURLPair
  - baml_src/british_isles/ireland/ciancheiltis_en_ga_roi.baml
        ExtractIrishStatuteBook
        ExtractIrelandBilingualSyllabus

Each adapter function:
  1. Defers the import of the generated BAML runtime to inside the function
     body, so the module is importable even before `baml-cli generate` has
     been run (the `baml_client` package is gitignored and generated on
     demand via `mise run baml:generate` / `uv run baml-cli generate`).
  2. Returns `{"json": <pydantic_json>}` when the result is a Pydantic
     model, otherwise `{"raw": <str>}`.
  3. Catches every exception with a structlog warning (mirrors the
     `extract_bilingual_lo` / `extract_cross_linguistic_ga` pattern in
     `baml_src/british_isles/ireland/education/_cross/bilingual_extraction.py`)
     and returns `{"error": <str(exc)>}`. The ciancheiltis Phase 2 dlt
     sources downstream can therefore rely on `result.get("error")`
     being non-None to gate RAGAS asset checks without crashing.

Usage from the Phase 2 dlt source / Dagster asset layer:

    from baml_src.british_isles.ireland.ciancheiltis_en_ga_roi_extraction import (
        extract_irish_statute_book,
        extract_ireland_bilingual_syllabus,
        extract_ireland_ga_url_pair,
    )

    pair = extract_irish_statute_book(
        url="https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html",
        body=html_to_markdown(body),
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_irish_statute_book(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual Act / SI on `irishstatutebook.ie` (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 2
    per-phase function). Routes to the `CiancheiltisGaRoiExtract` client
    (`uccix-mistral-24b`, modern Irish — UCCIX Mistral fine-tune).

    The canonical smoke test from the umbrella spec is the 1937
    Constitution Act at
    `https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html`
    which MUST pair with the `/enacted/en/html` sibling. Article 4
    declares Irish as the first official language of the Republic of
    Ireland.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractIrishStatuteBook(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_irish_statute_book_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_ireland_bilingual_syllabus(
    en_text: str,
    ga_text: str,
) -> dict[str, Any]:
    """Pair a bilingual NCCA / curriculumonline.ie syllabus (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 2
    per-phase function for theme T3 Education). Routes to the
    `CiancheiltisGaRoiExtract` client. The existing Ireland education
    pipeline (`baml_src/british_isles/ireland/education/_cross/`)
    already handles concept-level pairing via `ExtractCrossLinguisticConcept`
    — this function is the page-level wrapper that emits a
    `BilingualPagePair` row for the ciancheiltis registry.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractIrelandBilingualSyllabus(
            en_text=en_text,
            ga_text=ga_text,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_ireland_bilingual_syllabus_failed",
            error=str(e),
        )
        return {"error": str(e)}


def extract_ireland_ga_url_pair(
    url_en: str,
    url_ga: str,
    body_en: str,
    body_ga: str,
) -> dict[str, Any]:
    """Pair a bilingual gov.ie parallel page (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 2
    shared extraction function for themes T1/T2/T4/T5/T7/T8/T9/T10).
    Routes to the `CiancheiltisGaRoiExtract` client. The canonical
    gov.ie parallel-page pattern is `https://www.gov.ie/en/<slug>` ↔
    `https://www.gov.ie/ga/<slug>` — the function corroborates the
    pairing from the markdown body of each side before emitting a
    `BilingualPagePair` row.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractIrelandGAURLPair(
            url_en=url_en,
            url_ga=url_ga,
            body_en=body_en,
            body_ga=body_ga,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_ireland_ga_url_pair_failed",
            url_en=url_en,
            url_ga=url_ga,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_irish_statute_book",
    "extract_ireland_bilingual_syllabus",
    "extract_ireland_ga_url_pair",
]
