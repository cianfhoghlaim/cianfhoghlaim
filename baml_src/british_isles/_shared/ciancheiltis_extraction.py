"""ciancheiltis bilingual extraction BAML adapter.

Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.4). Mirrors the
shape of `baml_src/british_isles/ireland/education/_cross/bilingual_extraction.py`:
wraps the 4 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractCiancheiltisBilingualPage
        ExtractBilingualExplanatoryNote
  - baml_src/british_isles/wales/ciancheiltis_en_cy.baml
        ExtractWalesBilingualSyllabus
        ExtractWelshSI

Each adapter function:
  1. Defers the import of the generated BAML runtime to inside the function
     body, so the module is importable even before `baml-cli generate` has
     been run (the `baml_client` package is gitignored and generated on
     demand via `mise run baml:generate` / `uv run baml-cli generate`).
  2. Returns `{"json": <pydantic_json>}` when the result is a Pydantic
     model, otherwise `{"raw": <str>}`.
  3. Catches every exception with a structlog warning (mirrors the
     `extract_bilingual_lo` / `extract_cross_linguistic_ga` pattern) and
     returns `{"error": <str(exc)>}`. The ciancheiltis dlt sources
     downstream can therefore rely on `result.get("error")` being non-None
     to gate RAGAS asset checks without crashing.

Usage from the dlt source / Dagster asset layer:

    from baml_src.british_isles._shared.ciancheiltis_extraction import (
        extract_cianocheiltis_bilingual_page,
        extract_bilingual_explanatory_note,
        extract_wales_bilingual_syllabus,
        extract_welsh_si,
    )

    pair = extract_cianocheiltis_bilingual_page(
        page_markdown=html_to_markdown(body),
        language_pair="en-cy",
        theme_code="T1",
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_cianocheiltis_bilingual_page(
    page_markdown: str,
    language_pair: str,
    theme_code: str,
) -> dict[str, Any]:
    """Extract a `BilingualPagePair` row from a single half-page.

    Per the 2026-09-06 spec §Requirement BAML extraction suite: pairs the
    input page with its translation partner (cy / ga / gd / gv side) and
    emits the pair URL, language_pair, is_same_article, metadata_mismatch,
    theme_code. The catch-all `metadata_mismatch` flag is the canonical
    signal that fires on `legislation.gov.uk/uksi/2007/1484/made`.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractCiancheiltisBilingualPage(
            page_markdown=page_markdown,
            language_pair=language_pair,
            theme_code=theme_code,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_cianocheiltis_bilingual_page_failed",
            language_pair=language_pair,
            theme_code=theme_code,
            error=str(e),
        )
        return {"error": str(e)}


def extract_bilingual_explanatory_note(
    en_note: str,
    cy_note: str,
) -> dict[str, Any]:
    """Pair a parallel EN + Celtic-language explanatory note.

    Per the 2026-09-06 spec §Requirement BAML extraction suite: emits a
    `BilingualExplanatoryNotePair` (en_note, cy_note, concept_id,
    confidence). Patterned on the Ireland education
    `ExtractCrossLinguisticConcept` template.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractBilingualExplanatoryNote(
            en_note=en_note,
            cy_note=cy_note,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_bilingual_explanatory_note_failed",
            error=str(e),
        )
        return {"error": str(e)}


def extract_wales_bilingual_syllabus(
    en_text: str,
    cy_text: str,
) -> dict[str, Any]:
    """Pair a bilingual WJEC / CBAC / Hwb syllabus (EN ↔ CY).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 1
    per-phase function). Routes to the `ciancheiltisCyExtract` client
    (gemma-4-26B-A4B, Welsh-aware multilingual MoE).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractWalesBilingualSyllabus(
            en_text=en_text,
            cy_text=cy_text,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_wales_bilingual_syllabus_failed",
            error=str(e),
        )
        return {"error": str(e)}


def extract_welsh_si(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a UK statutory instrument (EN SI ↔ CY SI on legislation.gov.uk).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 1
    per-phase function). Routes to the `ciancheiltisCyExtract` client.
    The canonical smoke test from the umbrella spec is
    `legislation.gov.uk/uksi/2007/1484/made`, which MUST fire
    `metadata_mismatch=true` despite the HTTP `Content-Language: eng`
    metadata.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractWelshSI(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_welsh_si_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_cianocheiltis_bilingual_page",
    "extract_bilingual_explanatory_note",
    "extract_wales_bilingual_syllabus",
    "extract_welsh_si",
]
