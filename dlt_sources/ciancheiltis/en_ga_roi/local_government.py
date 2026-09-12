"""PR0.6 — Phase 2 T8 (Local government) — 31 Irish local authorities DLT source.

Deferred stub. PR0.6 will seed URLs for all 31 Irish local
authorities (26 county councils + 3 city councils + 2 city and
county councils — the canonical ``IRISH_COUNTY_COUNCILS`` constant
below).

Each local authority publishes bilingual (EN + GA) content under
the Local Government Act 2001 + the Official Languages Act 2003
(s. 9 — provision of services in Irish). The bilingual pages are
typically hosted under the ``/ga/`` subdirectory
(e.g. ``fingal.ie/ga/``) and pair with the English site under
``/en/`` or simply ``/``.

PR0.6 will use
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
to pair the EN landing page (or service page) with its GA mirror
and write one LanceDB row per bilingual page pair via
``ciancheiltis_en_ga_roi_embedding``.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_roi.local_government"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi/local_government_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-ga"


# Canonical list of all 31 local authorities in the Republic of
# Ireland (per the 2014 Local Government Reform Act + the 2019
# Cork City + Galway City boundary extensions). The list mixes the
# 26 county councils + 3 city councils + 2 city-and-county councils
# because each ships bilingual content under the same Official
# Languages Act 2003 s. 9 statutory duty.
IRISH_COUNTY_COUNCILS: tuple[str, ...] = (
    # Carlow County Council
    "carlowcoco.ie",
    # Cavan County Council
    "cavancoco.ie",
    # Clare County Council
    "clarecoco.ie",
    # Cork City Council (the 2019 boundary-extended successor to
    # the older Cork City Council — publishes EN + GA under
    # the same ``corkcity.ie`` domain)
    "corkcity.ie",
    # Cork County Council
    "corkcoco.ie",
    # Donegal County Council (the only Republic of Ireland county
    # where Irish is still a community language in the Gaeltacht)
    "donegalcoco.ie",
    # Dublin City Council
    "dublincity.ie",
    # Dún Laoghaire-Rathdown County Council
    "dlr.ie",
    # Fingal County Council
    "fingal.ie",
    # Galway City Council
    "galwaycity.ie",
    # Galway County Council
    "galwaycoco.ie",
    # Kerry County Council
    "kerrycoco.ie",
    # Kildare County Council
    "kildarecoco.ie",
    # Kilkenny County Council
    "kilkennycoco.ie",
    # Laois County Council
    "laoiscoco.ie",
    # Leitrim County Council
    "leitrimcoco.ie",
    # Limerick City and County Council (the merged authority since 2014)
    "limerick.ie",
    # Longford County Council
    "longfordcoco.ie",
    # Louth County Council
    "louthcoco.ie",
    # Mayo County Council
    "mayococo.ie",
    # Meath County Council
    "meath.ie",
    # Monaghan County Council
    "monaghancoco.ie",
    # Offaly County Council
    "offalycoco.ie",
    # Roscommon County Council
    "roscommoncoco.ie",
    # Sligo County Council
    "sligococo.ie",
    # South Dublin County Council
    "sdublincoco.ie",
    # Tipperary County Council
    "tipperarycoco.ie",
    # Waterford City and County Council (the merged authority since 2014)
    "waterfordcouncil.ie",
    # Westmeath County Council
    "westmeathcoco.ie",
    # Wexford County Council
    "wexfordcoco.ie",
    # Wicklow County Council
    "wicklowcoco.ie",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.6 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "IRISH_COUNTY_COUNCILS",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
