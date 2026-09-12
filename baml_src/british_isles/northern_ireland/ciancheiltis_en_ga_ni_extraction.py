"""ciancheiltis Phase 3 (en-ga / Northern Ireland) BAML extraction adapter.

Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.7). Mirrors the
shape of `baml_src/british_isles/ireland/ciancheiltis_en_ga_roi_extraction.py`:
wraps the 3 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractNIBilingualTerm
  - baml_src/british_isles/northern_ireland/ciancheiltis_en_ga_ni.baml
        ExtractNIStatute
        ExtractNIDirectBilingualPage

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
     and returns `{"error": <str(exc)>}`. The ciancheiltis Phase 3 dlt
     sources downstream can therefore rely on `result.get("error")`
     being non-None to gate RAGAS asset checks without crashing.

Usage from the Phase 3 dlt source / Dagster asset layer:

    from baml_src.british_isles.northern_ireland.ciancheiltis_en_ga_ni_extraction import (
        extract_ni_statute,
        extract_ni_direct_bilingual_page,
        extract_ni_bilingual_term,
    )

    pair = extract_ni_statute(
        url="https://www.legislation.gov.uk/uksi/2022/15/contents/made",
        body=html_to_markdown(body),
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_ni_statute(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual NI statute on `legislation.gov.uk` (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 3
    per-phase function). Routes to the `CiancheiltisGaNiExtract` client
    (`uccix-mistral-24b`, modern Irish — UCCIX Mistral fine-tune).

    The canonical smoke test from the umbrella spec is the
    *Identity and Language (Northern Ireland) Act 2022* at
    `https://www.legislation.gov.uk/uksi/2022/15/contents/made`
    (commencement pending as of 2026-09). The Act establishes the
    statutory framework for Irish-medium education in NI and creates
    the Office of the Identity and Language Commissioner.

    The function pairs against the full NI slug set:
    `/uksi/<year>/<number>`, `/nisi/<year>/<number>`,
    `/nid/<year>/<number>`, `/nia/<year>/<number>`.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractNIStatute(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_ni_statute_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_ni_direct_bilingual_page(
    url_en: str,
    url_ga: str,
    body_en: str,
    body_ga: str,
) -> dict[str, Any]:
    """Pair a bilingual nidirect.gov.uk parallel page (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 3
    per-phase function for themes T1/T2/T3/T4/T5/T7/T8/T9/T10).
    Routes to the `CiancheiltisGaNiExtract` client. The canonical
    nidirect parallel-page pattern is
    `https://www.nidirect.gov.uk/articles/<slug>` ↔
    `https://www.nidirect.gov.uk/gaeilge/airteagal/<slug>` — the
    function corroborates the pairing from the markdown body of each
    side before emitting a `BilingualPagePair` row. The same
    function also covers the CnaG (comhairle.org) + Education
    Authority NI (eani.org.uk) + Department of Education NI
    (education-ni.gov.uk) bilingual surfaces.

    T6 (terminology) is handled separately by `extract_ni_bilingual_term`
    (the shared `ExtractNIBilingualTerm` function in
    `baml_src/british_isles/_shared/ciancheiltis.baml`).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractNIDirectBilingualPage(
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
            "extract_ni_direct_bilingual_page_failed",
            url_en=url_en,
            url_ga=url_ga,
            error=str(e),
        )
        return {"error": str(e)}


def extract_ni_bilingual_term(
    en_term: str,
    ga_term: str,
    source: str,
) -> dict[str, Any]:
    """Pair a bilingual NI Irish-medium terminology row (EN ↔ GA).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 3
    shared extraction function for T5 language bodies — CnaG /
    Education Authority NI Irish-medium unit / Department of Education
    NI). Routes to the `CiancheiltisGaNiExtract` client (the Phase 3
    modern-Irish routing). The function emits a
    `BilingualExplanatoryNotePair` with a stable concept_id in the
    CC-GAE-NNN namespace and a translation-fidelity confidence score.

    `source` MUST be one of: 'cna_g', 'eani', 'dept_ed_ni', 'nidirect',
    'other'. The source string is metadata only and does NOT influence
    the concept_id — the NILanguagePair companion row carries the
    source_domain column separately (added by the Phase 3 dlt source
    layer).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractNIBilingualTerm(
            en_term=en_term,
            ga_term=ga_term,
            source=source,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_ni_bilingual_term_failed",
            source=source,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_ni_statute",
    "extract_ni_direct_bilingual_page",
    "extract_ni_bilingual_term",
]
