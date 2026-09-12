"""PR0.6 — Phase 2 T7 (Courts & Tribunals) — Courts Service Ireland DLT source.

Deferred stub. PR0.6 will crawl the Courts Service of Ireland's
bilingual (EN <-> GA) public-facing content at ``courts.ie`` — the
catalogue of court forms, the Supreme Court + Court of Appeal +
High Court + Circuit Court + District Court rules, and the published
judgments of the superior courts.

The Courts Service is established under the Courts Service Act 1998
and is required by statute to publish bilingual court forms where
both Irish-language and English-language versions exist. PR0.6 will
pair the EN form (e.g. ``/forms/circuit-court/.../en/``) with its
GA mirror (e.g. ``/forms/circuit-court/.../ga/``) and write one
LanceDB row per bilingual form pair via the
``ciancheiltis_en_ga_roi_embedding`` App.

The underlying single-language pipeline already lives at
``dlt_sources/british_isles/ireland/law/courts_ie.py`` (the BIEP
substrate). This module is the **ciancheiltis bilingual-pair
wrapper** that pairs every EN row with its GA mirror.
"""
SOURCE_ID = "ciancheiltis.en_ga_roi.courts"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/courts_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
