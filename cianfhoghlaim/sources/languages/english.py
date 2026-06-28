"""English language — full source profile (cianfhoghlaim Plan 1 active).

English is the primary official language for 5 of the 6 active nations
(Ireland, England, Northern Ireland, Wales, Scotland) and is widely used in
the Isle of Man. All Plan 1 corpora include English sources.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.

Coverage (Plan 1):
- Ireland education (5 stages × EN) at sources/nations/ie/education/*/english.py
- leabharlann (mixed-language, English-first)

Coverage (Plan 2/3 stubs):
- UK 4-nation + IoM education + 7 domains — see sources/nations/{en,ni,wls,sct,iom}/
"""

from __future__ import annotations

# Plan 1 active: every English-language source that the consolidated
# Cianfhoghlaim platform needs to ingest for Ireland education + leabharlann.
PLAN_1_SOURCES: tuple[str, ...] = (
    # Ireland — 5 educational stages × English
    "sources.nations.ie.education.early_childhood.english",
    "sources.nations.ie.education.primary.english",
    "sources.nations.ie.education.junior_cycle.english",
    "sources.nations.ie.education.senior_cycle.english",
    "sources.nations.ie.education.leaving_cert.english",
    # leabharlann (English-majority: aigne, gemini_deep_research; mixed: mata,
    # ollscoil_na_gaillimhe, zotero; minority: gaeilge)
    "leabharlann.aigne",
    "leabharlann.gemini_deep_research",
    "leabharlann.mata",
    "leabharlann.ollscoil_na_gaillimhe",
    "leabharlann.zotero",
)

# Plan 2/3 preserved (UK 4-nation + IoM, all 7 domains): stub sources at
# sources/nations/{en,ni,wls,sct,iom}/{education,law,medicine,culture,
# government,intelligence,statistics,geospatial}/english.py
PLAN_2_3_STUB_NATIONS: tuple[str, ...] = ("en", "ni", "wls", "sct", "iom")

# Legacy preserved (Crown Dependencies): Jersey + Guernsey stubs at
# sources/_preserved/{jey,ggy}/english.py
LEGACY_NATIONS: tuple[str, ...] = ("jey", "ggy")

# ISO 639-1 + BCP-47 identifiers used by the BGE-M3 multilingual embedder
ISO_CODES: tuple[str, ...] = ("en", "en-GB", "en-IE", "en-US", "en-NZ", "en-AU")


def is_active_in_plan1() -> bool:
    """English is the primary secondary language for Plan 1."""
    return True
