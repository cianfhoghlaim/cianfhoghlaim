"""PR0.9 — Phase 5 T4 (Healthcare) — Manx Health & Social Care DLT source.

Deferred stub. PR0.9 will crawl the very limited Manx-language
content published by Manx Care (the Isle of Man Health & Social
Care body, established 2021 under the Manx Care Act 2021) and the
Department of Health & Social Care (DHSC) at ``gov.im``.

Canonical example: ``https://www.gov.im/about-the-government/departments/health-and-social-care/``
— the Department of Health & Social Care portal.

Manx (Gaelg) is in revival status — **very limited Manx content
exists here**. Manx Care's published patient-information library
is English-only with isolated Manx-language glossaries (typically
the section headers + the Manx-language equivalents of common
medical terms where published by the Manx Language Project).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, gv) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gv_embedding`` writes ONE LanceDB row per
patient-information page (with both EN + GV embeddings where the
GV side exists; the BAML coverage gate flags the partial rows).

Phase 5 T4 is the **smallest healthcare corpus of the 5 sister
phases** (CY/GA-ROI/GA-NI/GD/GV). Unlike Phase 4 NHS Scotland
(which ships a wide bilingual surface at nhsinform.scot/gd/...)
or Phase 2 HSE Ireland (which ships partial Irish content), Phase
5 Manx Care publishes very little Manx content at all. The
umbrella spec's content-based language detector is the gate and
is expected to flag most rows as English-only.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-gv"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    Manx (Gaelg) is in revival status — Manx Care's patient-information
    library is English-only with isolated Manx-language glossaries.
    The Phase 5 strict gate is "capture what bilingual content exists
    and surface it faithfully"; PR0.9 will pair every English Manx Care
    page with whatever Manx content exists and the umbrella spec's
    content-based language detector will flag the partial rows.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
