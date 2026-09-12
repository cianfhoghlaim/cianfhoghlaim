"""PR0.7 — Phase 3 T8 (Local government) — 11 NI unitary councils DLT source.

Deferred stub. PR0.7 will seed URLs for all 11 Northern Ireland unitary
councils (the canonical ``NI_COUNCILS`` constant below). Each council
publishes bilingual (EN + GA) content under the Local Government Act
(Northern Ireland) 2014 + the Identity and Language (Northern Ireland)
Act 2022 (s. 9 — provision of services in Irish).

The 11 councils were established by the Local Government (Boundaries)
Act (Northern Ireland) 2008 + the 2014 reform that collapsed the
legacy 26 district councils into 11 larger unitary councils. The
bilingual pages are typically hosted under the ``/ga/`` subdirectory
(e.g. ``antrimandnewtownabbey.gov.uk/ga/``) and pair with the English
site under ``/en/`` or simply ``/``.

PR0.7 will use
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
to pair the EN landing page (or service page) with its GA mirror
and write one LanceDB row per bilingual page pair via
``ciancheiltis_en_ga_ni_embedding``.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_ni.local_government"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/local_government_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-ga"


# Canonical list of all 11 unitary councils in Northern Ireland
# (per the 2014 Local Government Reform Act + the 2008 Boundaries
# Act + the 2015 operational commencement). Each council publishes
# bilingual content under the Identity and Language (Northern Ireland)
# Act 2022 + the 1998 Good Friday Agreement statutory duties.
NI_COUNCILS: tuple[str, ...] = (
    # Antrim and Newtownabbey Borough Council
    "antrimandnewtownabbey.gov.uk",
    # Ards and North Down Borough Council
    "ardsandnorthdown.gov.uk",
    # Armagh City, Banbridge and Craigavon Borough Council
    "armaghbanbridgecraigavon.gov.uk",
    # Belfast City Council (the capital district)
    "belfastcity.gov.uk",
    # Causeway Coast and Glens Borough Council
    "causewaycoastandglens.gov.uk",
    # Derry City and Strabane District Council (the cross-border city
    # straddling the Donegal border — the city's official bilingual
    # forms pair Doire / Derry, per the 1998 Good Friday Agreement)
    "derrystrabane.com",
    # Fermanagh and Omagh District Council
    "fermanaghomagh.com",
    # Lisburn and Castlereagh City Council
    "lisburncastlereagh.gov.uk",
    # Mid and East Antrim Borough Council
    "midandeastantrim.gov.uk",
    # Mid Ulster District Council
    "midulstercouncil.org",
    # Newry, Mourne and Down District Council
    "newrymournedown.org",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "NI_COUNCILS",
    "SOURCE_ID",
    "THEME_CODE",
]
