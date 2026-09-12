"""PR0.7 — Phase 3 T7 (Courts & Tribunals) — NI Courts Service DLT source.

Deferred stub. PR0.7 will crawl the Northern Ireland Courts and
Tribunals Service (NICTS) public-facing content at
``courtsni.uk`` — the catalogue of court forms, the Court of Appeal +
High Court + Crown Court + County Court + Magistrates' Court rules,
and the published judgments of the superior courts.

The NICTS is established under the Judicature (Northern Ireland) Act
1978 + the Northern Ireland Act 1998 + the Courts Act (Northern
Ireland) 1978 (the primary statute) and is required by statute to
publish bilingual court forms where both Irish-language and
English-language versions exist (per the 1998 Good Friday Agreement
commitments + the Identity and Language (Northern Ireland) Act 2022
which extends the Irish-language publication duties to NICTS).

PR0.7 will pair the EN form (e.g. ``courtsni.uk/forms/<court>/.../en/``)
with its GA mirror (e.g. ``courtsni.uk/forms/<court>/.../ga/``) and
write one LanceDB row per bilingual form pair via the
``ciancheiltis_en_ga_ni_embedding`` App.

The underlying single-language pipeline already lives at
``dlt_sources/british_isles/northern_ireland/law/courtsni.py`` (the
BIEP substrate, mirroring the BIEP v3 jurisdiction pipeline pattern).
This module is the **ciancheiltis bilingual-pair wrapper** that pairs
every EN row with its GA mirror.
"""
SOURCE_ID = "ciancheiltis.en_ga_ni.courts"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/courts_chunks"
THEME_CODE = "T7"
LANGUAGE_PAIR = "en-ga"


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = ["LANCE_TABLE", "LANGUAGE_PAIR", "SOURCE_ID", "THEME_CODE"]
