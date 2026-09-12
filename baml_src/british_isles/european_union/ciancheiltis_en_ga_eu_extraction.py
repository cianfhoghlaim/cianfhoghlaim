"""ciancheiltis Phase 6 (en-ga / European Union) BAML extraction adapter.

Per the 2026-XX-XX-ciancheiltis-v1 openspec change (PR0.10). Mirrors the
shape of `baml_src/british_isles/ireland/ciancheiltis_en_ga_roi_extraction.py`:
wraps the 4 BAML extraction functions declared across

  - baml_src/british_isles/_shared/ciancheiltis.baml
        ExtractEUBilingualTermPair
  - baml_src/british_isles/european_union/ciancheiltis_en_ga_eu.baml
        ExtractEURLexTreaty
        ExtractEuroparlPlenary
        ExtractIATETerm

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
     and returns `{"error": <str(exc)>}`. The ciancheiltis Phase 6 dlt
     sources downstream can therefore rely on `result.get("error")`
     being non-None to gate RAGAS asset checks without crashing.

IMPORTANT CONTEXT — EU-level Irish coverage is PARTIAL (Irish was added
as the 24th official EU language on 2022-01-01 per Council Decision
(EU) 2020/2172). The Phase 6 schema MUST capture `language_availability`
∈ {"full", "partial", "summary_only", "none"} as a first-class column
on every emitted row — the dlt source layer downstream relies on this
column to distinguish "real Irish-language EU rows" from "English-only
EU rows with an Irish-language summary header". The 4 adapter functions
below all route through the `CiancheiltisGaEuExtract` client
(`uccix-mistral-24b`, modern Irish — UCCIX Mistral fine-tune), same
model as the other 3 en-ga clients (Phase 2 ROI / Phase 3 NI / the
canonical `CiancheiltisGaExtract` fallback).

Usage from the Phase 6 dlt source / Dagster asset layer:

    from baml_src.british_isles.european_union.ciancheiltis_en_ga_eu_extraction import (
        extract_eur_lex_treaty,
        extract_europarl_plenary,
        extract_iate_term,
        extract_eu_bilingual_term_pair,
    )

    page = extract_eur_lex_treaty(
        url="https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E",
        body=html_to_markdown(body),
    )
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def extract_eur_lex_treaty(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual EUR-Lex Treaty / Regulation / Directive / Decision page (EN ↔ GA).

    Per the 2026-XX-XX spec §Requirement BAML extraction suite (Phase 6
    per-phase function for theme T1 Legislation at the EU level).
    Routes to the `CiancheiltisGaEuExtract` client (`uccix-mistral-24b`,
    modern Irish — UCCIX Mistral fine-tune). The canonical smoke test
    from the umbrella spec is the EUR-Lex Irish-language edition of
    the Treaty on European Union at
    `https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E`
    — the `/GA/TXT/` path segment forces EUR-Lex to serve the TEU in
    modern Irish (An Caighdeán Oifugiúil) instead of the default
    English edition.

    Covers the 8 canonical CELEX identifiers the Phase 6 dlt source
    enumerates: 12012E (TEU), 12012M (TFEU), 12012P (TEU-TFEU-CFSP),
    12012Q (Charter), 12002T (Nice), 11997D (Amsterdam), 11992E
    (Maastricht), plus 11957E (Treaty of Rome — typically
    `summary_only`).

    IMPORTANT — EU-level Irish coverage is PARTIAL: most CELEX
    documents return `summary_only` when invoked via the `/GA/TXT/`
    path (the `language_availability` column fires to flag this).
    The function emits the `EUBilingualPage` row with the
    `language_availability` first-class column populated so the
    downstream dlt source / Dagster asset / cocoindex flow can
    distinguish real Irish-language rows from summary-only rows.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractEURLexTreaty(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_eur_lex_treaty_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_europarl_plenary(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual European Parliament plenary debate transcript (EN ↔ GA).

    Per the 2026-XX-XX spec §Requirement BAML extraction suite (Phase 6
    per-phase function for theme T2 Parliamentary documents at the EU
    level). Routes to the `CiancheiltisGaEuExtract` client. The
    canonical Phase 6 europarl URL is
    `https://europarl.europa.eu/doceo/document/CRE-9-<year>-..._GA.pdf`
    — the `CRE` prefix is the *Compte Rendu in extenso* (verbatim
    plenary minutes) document series; the trailing `_GA.pdf` suffix
    forces the Irish-language edition.

    IMPORTANT — EU-level Irish coverage is PARTIAL for plenary
    transcripts. Most EP plenary debates ship only in English + French
    (the two EP procedural working languages) with no Irish-language
    edition; some Irish MEPs contribute in Irish and the EP then
    serves the transcript in Irish on a per-debate basis. The most
    common `language_availability` value for plenary transcripts is
    `none` (no Irish edition exists) followed by `summary_only` (the
    EP serves a short Irish-language summary of the debate when at
    least one Irish MEP contributed).

    The function emits the `EUBilingualPage` row with the
    `language_availability` first-class column populated. Note:
    plenary transcripts do NOT carry CELEX identifiers — the
    `ce_lex` field on the emitted row is always empty for europarl
    sources.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractEuroparlPlenary(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_europarl_plenary_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_iate_term(
    url: str,
    body: str,
) -> dict[str, Any]:
    """Pair a bilingual IATE inter-institutional terminology record (EN ↔ GA).

    Per the 2026-XX-XX spec §Requirement BAML extraction suite (Phase 6
    per-phase function for theme T6 Terminology at the EU level).
    Routes to the `CiancheiltisGaEuExtract` client. The canonical
    IATE URL pair is
    `https://iate.europa.eu/search/standard/EN/<id>` ↔
    `https://iate.europa.eu/search/standard/GA/<id>` — the IATE ID is
    the canonical term_id across all 24 official EU languages.

    IMPORTANT — IATE coverage is RELATIVELY GOOD for Irish (compared
    to the EUR-Lex / europarl plenary surfaces) because IATE was one
    of the first EU surfaces to receive Irish-language content after
    the 2022 Irish accession. The most common `language_availability`
    value for IATE is `full` (a complete Irish ↔ English term +
    definition pairing exists), with `partial` for the older IATE
    records (pre-2022) where the Irish side was added retrospectively
    by Foras na Gaeilge.

    The function emits the `EUBilingualPage` row with the
    `language_availability` first-class column populated. The Phase 6
    dlt source layer emits a separate `EUTermPair` companion row
    (with the en_term / ga_term / iate_id / domain /
    language_availability fields) from the extracted en_content /
    ga_content fields downstream via the shared
    `extract_eu_bilingual_term_pair` function below.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractIATETerm(url=url, body=body)
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_iate_term_failed",
            url=url,
            error=str(e),
        )
        return {"error": str(e)}


def extract_eu_bilingual_term_pair(
    en_term: str,
    ga_term: str,
    iate_id: str,
) -> dict[str, Any]:
    """Pair a bilingual IATE terminology row (EN ↔ GA) with stable concept_id.

    Per the 2026-XX-XX spec §Requirement BAML extraction suite (Phase 6
    shared extraction function for T5 / T6 — EU inter-institutional
    terminology from IATE). Routes to the `CiancheiltisGaEuExtract`
    client (the Phase 6 EU modern-Irish routing). The function emits
    a `BilingualExplanatoryNotePair` with a stable concept_id in the
    CC-GAE-NNN namespace (GAE = Gaeilge / Irish — the canonical Irish
    stem per the `ExtractBilingualExplanatoryNote` concept_id table
    at `baml_src/british_isles/_shared/ciancheiltis.baml:158-162`)
    and a translation-fidelity confidence score.

    `iate_id` MUST be the IATE internal numeric ID shared by the
    EN-side and GA-side standard records (e.g. '1234567'). The IATE
    ID is the canonical term_id across all 24 official EU languages.
    The ID MUST NOT influence the concept_id — it is metadata only
    and is logged to the `EUTermPair` companion row separately by
    the Phase 6 dlt source layer. When the pairing was inferred
    without an explicit IATE ID (e.g. from a cross-referenced EUR-Lex
    treaty definition), pass empty iate_id — do NOT synthesise an ID
    to force a row.

    IMPORTANT — EU-level Irish coverage is PARTIAL across the wider
    EU institutional surface (Irish was added as the 24th official
    EU language on 2022-01-01 per Council Decision (EU) 2020/2172),
    but IATE coverage is RELATIVELY GOOD because IATE was one of the
    first EU surfaces to receive Irish-language content after the
    2022 accession. The Phase 6 dlt source layer sets the
    `language_availability` field on the `EUTermPair` companion row
    separately, based on whether the IATE record has a full EN-side
    + GA-side pairing, a partial pairing, a summary-only pairing, or
    no Irish content. The `language_availability` value MUST NOT
    influence the concept_id — it is metadata only and is logged to
    the `EUTermPair` row separately by the Phase 6 dlt source layer.
    Most IATE rows post-2022 will be 'full'; most pre-2022 rows
    retro-translated by Foras na Gaeilge will be 'partial'.
    """
    try:
        from baml_client.baml_client.sync_client import b  # type: ignore[import-not-found]

        result = b.ExtractEUBilingualTermPair(
            en_term=en_term,
            ga_term=ga_term,
            iate_id=iate_id,
        )
        if hasattr(result, "model_dump_json"):
            return {"json": result.model_dump_json()}
        return {"raw": str(result)}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "extract_eu_bilingual_term_pair_failed",
            iate_id=iate_id,
            error=str(e),
        )
        return {"error": str(e)}


__all__ = [
    "extract_eur_lex_treaty",
    "extract_europarl_plenary",
    "extract_iate_term",
    "extract_eu_bilingual_term_pair",
]
