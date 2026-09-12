"""ciancheiltis Phase 4 (en-gd / Scotland) BAML extraction adapter.

Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.8). Mirrors the
shape of `baml_src/british_isles/northern_ireland/ciancheiltis_en_ga_ni_extraction.py`:
wraps the 3 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractGaelicTerm
  - baml_src/british_isles/scotland/ciancheiltis_en_gd.baml
        ExtractScottishStatute
        ExtractScottishGovPage

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
     and returns `{"error": <str(exc)>}`. The ciancheiltis Phase 4 dlt
     sources downstream can therefore rely on `result.get("error")`
     being non-None to gate RAGAS asset checks without crashing.

Usage from the Phase 4 dlt source / Dagster asset layer:

    from baml_src.british_isles.scotland.ciancheiltis_en_gd_extraction import (
        extract_scottish_statute,
        extract_scottish_gov_page,
        extract_gaelic_term,
    )

    pair = extract_scottish_statute(
        url="https://www.legislation.gov.uk/asp/2005/7/contents",
        body=html_to_markdown(body),
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_scottish_statute(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual Scottish statute on `legislation.gov.uk` (EN ↔ GD).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 4
    per-phase function for theme T1 Legislation). Routes to the
    `CiancheiltisGdExtract` client (`gemma-4-26B-A4B`, Welsh-aware
    multilingual MoE used for both Phase 1 Welsh and Phase 4 Scottish
    Gaelic routing).

    The canonical smoke test from the umbrella spec is the
    *Gaelic Language (Scotland) Act 2005* at
    `https://www.legislation.gov.uk/asp/2005/7/contents` which
    established Bòrd na Gàidhlig and gave Scottish Ministers a duty
    to promote the use of Gaelic.

    The function pairs against the full Scottish slug set:
    `/asp/<year>/<number>`, `/ssi/<year>/<number>`,
    `/sdsi/<year>/<number>`.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractScottishStatute(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_scottish_statute_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_scottish_gov_page(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual Scottish Government page (EN ↔ GD).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 4
    per-phase function for themes T2/T3/T5 — policy, education, and
    language bodies on the Scottish Government surface). Routes to the
    `CiancheiltisGdExtract` client.

    The function covers three Scottish surfaces:
      - `gov.scot` — the Scottish Government's main surface, which
        publishes a small but real Gaelic content section under
        gd-side `<slug>` URLs (the CMS does NOT enforce a `/gd/`
        prefix; pairing is corroborated from body content + the
        `<html lang="gd">` attribute)
      - `education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/`
        — the Education Scotland / Foghlam Alba gd-side education
        surface
      - `gaidhlig.scot/bord-na-gaidhlig/naidheachdan/` — the Bòrd na
        Gàidhlig Gaelic-medium news index (the canonical Phase 4
        T5 reference page)

    T1 (legislation) is handled separately by `extract_scottish_statute`
    above. T6 (terminology) is handled separately by
    `extract_gaelic_term` (the shared `ExtractGaelicTerm` function in
    `baml_src/british_isles/_shared/ciancheiltis.baml`).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractScottishGovPage(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_scottish_gov_page_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_gaelic_term(
    en_term: str,
    gd_term: str,
    source: str,
) -> dict[str, Any]:
    """Pair a bilingual Scottish Gaelic-medium terminology row (EN ↔ GD).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 4
    shared extraction function for T5 language bodies — Bòrd na
    Gàidhlig / Stòrlann Nàiseanta / DASG). Routes to the
    `CiancheiltisGdExtract` client (the Phase 4 Scottish Gaelic
    routing). The function emits a `BilingualExplanatoryNotePair`
    with a stable concept_id in the CC-GDH-NNN namespace and a
    translation-fidelity confidence score.

    `source` MUST be one of: 'bord_na_gaidhlig', 'storlann', 'dasg',
    'foghlam_alba', 'gov_scot', 'other'. The source string is
    metadata only and does NOT influence the concept_id — the
    GaelicTermPair companion row carries the source domain +
    is_bord_na_gaidhlig_origin flag separately (added by the Phase 4
    dlt source layer).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractGaelicTerm(
            en_term=en_term,
            gd_term=gd_term,
            source=source,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_gaelic_term_failed",
            source=source,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_scottish_statute",
    "extract_scottish_gov_page",
    "extract_gaelic_term",
]