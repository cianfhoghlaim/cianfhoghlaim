"""ciancheiltis Phase 5 (en-gv / Isle of Man) BAML extraction adapter.

Per the 2026-09-06-ciancheiltis-v1 openspec change (PR0.9). Mirrors the
shape of `baml_src/british_isles/scotland/ciancheiltis_en_gd_extraction.py`:
wraps the 3 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractManxTerm
  - baml_src/british_isles/isle_of_man/ciancheiltis_en_gv.baml
        ExtractTynwaldAct
        ExtractCultureVanninPage

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
     and returns `{"error": <str(exc)>}`. The ciancheiltis Phase 5 dlt
     sources downstream can therefore rely on `result.get("error")`
     being non-None to gate RAGAS asset checks without crashing.

Important context — Manx (Gaelg) is in **revival** status (per the
umbrella spec §6-phase language-pair staging + the dlt source
strict-gate note at `dlt_sources/ciancheiltis/en_gv/__init__.py:1`):
the last traditional native speaker died in 1974; there is no
statutory Manx-language commissioner; there is no statutory
requirement to publish in Manx. The Phase 5 mandate is "capture what
bilingual content exists and surface it faithfully". Phase 5 row
counts will be smaller than Phases 1-4 — every emitted row is
high-value.

Usage from the Phase 5 dlt source / Dagster asset layer:

    from baml_src.british_isles.isle_of_man.ciancheiltis_en_gv_extraction import (
        extract_tynwald_act,
        extract_culture_vannin_page,
        extract_manx_term,
    )

    pair = extract_tynwald_act(
        url="https://www.legislation.gov.im/cms/legislation/acts-of-tynwald/...",
        body=html_to_markdown(body),
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_tynwald_act(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual Tynwald Act / Hansard row (EN ↔ GV).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 5
    per-phase function for theme T1 Legislation). Routes to the
    `CiancheiltisGvExtract` client (`gemma-4-26B-A4B`, the
    Welsh-aware multilingual MoE used for the Phase 1 (Welsh),
    Phase 4 (Scottish Gaelic), and Phase 5 (Manx) Celtic-language
    pairings).

    The function pairs against the full Tynwald slug set:
    `https://www.legislation.gov.im/cms/legislation/acts-of-tynwald/<year>/<slug>`
    (the canonical primary-legislation stem — the older Statutes +
    recent ceremonial Acts occasionally carry Manx-language
    translations or preambular Manx clauses) and
    `https://www.tynwald.org.im/business/hansard/<session>` (the
    Tynwald Hansard stem — the verbatim parliamentary record;
    mostly English-only with rare Manx-language ceremonial /
    preambular content).

    IMPORTANT: Manx (Gaelg) is in revival status — there is NO
    `/gv/` URL prefix convention on legislation.gov.im. The
    gv-side is identified by the body content only. Most Tynwald
    Acts and Hansard rows have NO Manx-language sibling; when no
    sibling exists, the `ExtractTynwaldAct` function emits empty
    url_b + is_same_article=false. The `metadata_mismatch` flag
    fires often on Tynwald Hansard pages that ship
    `metadata["language"] = "eng"` despite a body that contains
    Manx-language ceremonial / preambular clauses.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractTynwaldAct(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_tynwald_act_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_culture_vannin_page(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual Culture Vannin / Learn Manx / Bunscoill page (EN ↔ GV).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 5
    per-phase function for themes T3/T5/T8/T9 — education, language
    bodies / culture, local government, public broadcasting & culture
    on the Manx cultural + language-body surface). Routes to the
    `CiancheiltisGvExtract` client.

    The function covers five Manx surfaces:
      - `culturevannin.im/learn-gaelg/` — Culture Vannin Manx-medium
        learning portal (the canonical Phase 5 reference page per
        the umbrella spec §Phase en-gv + the dlt source strict-gate
        note; the closest functional equivalent of the Phase 4
        Bòrd na Gàidhlig gd-side surface)
      - `learnmanx.com` — Learn Manx adult-learning portal (Culture
        Vannin + Manx Language Service)
      - `bunscoillghaelgagh.sch.im` — Bunscoill Ghaelgagh network
        (the 4 Manx-medium primary schools; the revival flagship)
      - `manxlanguage.sch.im` — per-school Manx Language Service
        offices (one per Bunscoill school site)
      - `corpus.gaelg.im` — the canonical Manx text corpus
        (Culture Vannin / Manx Language Service; the Phase 5
        equivalent of the Phase 4 Bòrd na Gàidhlig terminology
        glossary)

    IMPORTANT: Manx (Gaelg) is in revival status — there is NO
    `/gv/` URL prefix convention on any of the 5 Manx surfaces.
    The gv-side is identified by the body content only. Some
    `/learn-gaelg/` sub-pages ship Manx-only content (no en-side
    sibling); some ship side-by-side bilingual content. The
    `metadata_mismatch` flag fires often on Culture Vannin +
    Learn Manx pages where the CMS does not flip the lang
    attribute alongside the body content.

    T1 (legislation) is handled separately by `extract_tynwald_act`
    above. T6 (terminology) is handled separately by
    `extract_manx_term` (the shared `ExtractManxTerm` function in
    `baml_src/british_isles/_shared/ciancheiltis.baml`).
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractCultureVanninPage(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_culture_vannin_page_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_manx_term(
    en_term: str,
    gv_term: str,
    source: str,
) -> dict[str, Any]:
    """Pair a bilingual Manx-medium terminology row (EN ↔ GV).

    Per the 2026-09-06 spec §Requirement BAML extraction suite (Phase 5
    shared extraction function for T5 language bodies + T6 terminology
    — Culture Vannin / Learn Manx / Bunscoill Ghaelgagh / Manx
    Language Service / Gaelg Corpus). Routes to the
    `CiancheiltisGvExtract` client (the Phase 5 Manx routing). The
    function emits a `BilingualExplanatoryNotePair` with a stable
    concept_id in the CC-GLV-NNN namespace (GLV = Gaelg / Manx —
    the canonical Manx stem per the
    `ExtractBilingualExplanatoryNote` concept_id table at
    `baml_src/british_isles/_shared/ciancheiltis.baml:158-162`) and
    a translation-fidelity confidence score.

    `source` MUST be one of: 'culture_vannin', 'bunscoill',
    'learn_manx', 'manx_language_service', 'gaelg_corpus', 'other'.
    The source string is metadata only and does NOT influence the
    concept_id — the ManxTermPair companion row carries the source
    domain + is_culture_vannin_origin + is_bunscoill_origin flags
    separately (added by the Phase 5 dlt source layer).

    IMPORTANT: Manx is in revival status, so the row count from
    this function will be smaller than the Phase 4 (Scotland) and
    Phase 2 (ROI) sibling functions — every emitted row is
    high-value.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractManxTerm(
            en_term=en_term,
            gv_term=gv_term,
            source=source,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_manx_term_failed",
            source=source,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_tynwald_act",
    "extract_culture_vannin_page",
    "extract_manx_term",
]