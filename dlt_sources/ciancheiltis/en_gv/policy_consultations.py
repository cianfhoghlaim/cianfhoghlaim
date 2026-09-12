"""PR0.9 — Phase 5 T2 (Policy / consultations) — gov.im DLT source.

Deferred stub. PR0.9 will crawl the partial bilingual paired pages
of the Isle of Man Government at ``gov.im`` — the public-facing
portal of the Isle of Man Government (the Cabinet Office + the
branches of the Isle of Man Government).

Canonical example: ``https://www.gov.im/`` — the Isle of Man
Government public portal. ``gov.im`` publishes most policy /
consultation content in English only with **very limited** Manx
content (typically the page footer notice + the Cabinet Office
website's section headers, where published by the Office of the
Chief Minister).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, gv) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_gv_embedding`` writes ONE LanceDB row per
consultation / policy page pair — even when most rows are
English-only and the Manx side is empty (the BAML coverage gate
flags the partial row but does not drop it).

Phase 5 differs from Phase 2 (gov.ie) and Phase 3 (nidirect) in
that gov.im's bilingual surface is the smallest of the 5 sister
phases (CY/GA-ROI/GA-NI/GD/GV). Manx is in revival status —
there is no statutory bilingual publication duty (unlike the
Gaelic Language (Scotland) Act 2005 for Phase 4). The umbrella
spec's content-based language detector is the gate.

Phase 5 differs from Phase 4 in an additional way: gov.im does
not ship a parallel ``/gv/`` subdirectory surface — Manx-language
pages (where they exist) are published as standalone pages under
``/news/`` + the Cabinet Office's section headers, rather than as
mirrors of the English pages.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-gv"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    Manx (Gaelg) is in revival status — gov.im ships partial Manx
    content (typically page footers + Cabinet Office section headers)
    rather than full bilingual mirrors. PR0.9 will pair every English
    gov.im page with whatever Manx content exists, and the umbrella
    spec's content-based language detector will flag the partial rows.
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
