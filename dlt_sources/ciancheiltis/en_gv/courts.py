"""PR0.9 — Phase 5 T7 (Courts & Tribunals) — Isle of Man Courts DLT source.

Deferred stub. PR0.9 will crawl the Isle of Man Courts of Justice
public-facing content at ``courts.im`` — the catalogue of court
forms, the Deemster's Court + the High Court + the Magistrate's
Court + the Court of Appeal rules, and the published judgments of
the superior courts.

**Partial Phase 5**: The Isle of Man Courts publishes an
English-only corpus with extremely limited Manx-language material
(court forms ship with optional Manx-language notices + the
Deemster's oaths of office ship in Manx + English as a bilingual
document under the long-standing Tynwald convention). The Isle of
Man Courts bilingual surface is the smallest of the Phase 1-5
sister-court corpora and the umbrella spec acknowledges Phase 5 §
T7 as a "partial" theme — the BAML coverage gate is expected to
flag most rows as English-only.

The Isle of Man courts are established under the High Court Act
1991 + the Magistrates' Courts Act 1962 + the Court of Appeal
Act 1991. The Deemsters are the hereditary lay judges appointed
by the Crown (the First Deemster + the Second Deemster + the
full-time + part-time Deemsters). The appellate structure runs
from the High Court to the Judicial Committee of the Privy
Council (UK) as the final court of appeal — Manx law remains a
distinct body of customary law derived from Norse-Gaelic
tradition, separate from English common law.

PR0.9 will pair the EN form (e.g.
``courts.im/forms/<court>/.../en/``) with its GV mirror (where
published) and write one LanceDB row per bilingual form pair
via the ``ciancheiltis_en_gv_embedding`` App.

The underlying single-language pipeline is NOT yet seeded in
``dlt_sources/british_isles/isle_of_man/law/`` (only
``legislation.py`` exists). Phase 5 § T7 is the first Phase to
populate the rest of that sub-tree.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.courts"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/courts_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-gv"


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    Manx (Gaelg) is in revival status — the Isle of Man Courts
    bilingual surface is the smallest of the Phase 1-5 sister-court
    corpora (the BAML coverage gate will flag most rows as
    English-only).
    """
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
