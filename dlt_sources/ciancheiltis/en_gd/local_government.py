"""PR0.8 — Phase 4 T8 (Local government) — 32 Scottish unitary councils DLT source.

Deferred stub. PR0.8 will seed URLs for all 32 Scottish unitary
councils (the canonical ``SCOTTISH_COUNCILS`` constant below). Each
council publishes bilingual (EN + GD) content under the Local
Government (Scotland) Act 1973 + the Gaelic Language (Scotland) Act
2005 (which extends the bilingual publication duties to councils
that have adopted a Gaelic Language Plan under section 3 — notably
Comhairle nan Eilean Siar, Highland Council, Argyll and Bute, and
the City of Glasgow).

The 32 councils were established by the Local Government etc.
(Scotland) Act 1994 + the 1996 operational commencement which
replaced the legacy 53 district councils + 9 regional councils with
32 unitary councils. The bilingual pages are typically hosted under
the ``/gd/`` subdirectory (e.g. ``cne-siar.gov.uk/gd/`` for
Comhairle nan Eilean Siar) and pair with the English site under
``/en/`` or simply ``/``.

PR0.8 will use
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
to pair the EN landing page (or service page) with its GD mirror
and write one LanceDB row per bilingual page pair via
``ciancheiltis_en_gd_embedding``.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gd.local_government"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gd/local_government_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-gd"


# Canonical list of all 32 unitary councils in Scotland
# (per the 1994 Local Government etc. (Scotland) Act + the 1996
# operational commencement). Each council publishes bilingual content
# where adopted under the Gaelic Language (Scotland) Act 2005 § 3
# (Gaelic Language Plans).
SCOTTISH_COUNCILS: tuple[str, ...] = (
    # Aberdeen City Council
    "aberdeencity.gov.uk",
    # Aberdeenshire Council
    "aberdeenshire.gov.uk",
    # Angus Council
    "angus.gov.uk",
    # Argyll and Bute Council (one of the four Gaelic Language Plan
    # councils under the 2005 Act)
    "argyll-bute.gov.uk",
    # City of Edinburgh Council
    "edinburgh.gov.uk",
    # Clackmannanshire Council
    "clacks.gov.uk",
    # Comhairle nan Eilean Siar (Western Isles Council — the only
    # council with Gaelic as its primary working language, under the
    # 2005 Act + the Gaelic-first statutory footing of the Western
    # Isles)
    "cne-siar.gov.uk",
    # Dumfries and Galloway Council
    "dumgal.gov.uk",
    # Dundee City Council
    "dundeecity.gov.uk",
    # East Ayrshire Council
    "east-ayrshire.gov.uk",
    # East Dunbartonshire Council
    "eastdunbarton.gov.uk",
    # East Lothian Council
    "eastlothian.gov.uk",
    # East Renfrewshire Council
    "eastrenfrewshire.gov.uk",
    # Falkirk Council
    "falkirk.gov.uk",
    # Fife Council
    "fife.gov.uk",
    # Glasgow City Council (one of the four Gaelic Language Plan
    # councils under the 2005 Act — Glaschu)
    "glasgow.gov.uk",
    # Highland Council (one of the four Gaelic Language Plan councils
    # under the 2005 Act — the largest by area, with the densest
    # Gaelic-speaking population outside the Western Isles)
    "highland.gov.uk",
    # Inverclyde Council
    "inverclyde.gov.uk",
    # Midlothian Council
    "midlothian.gov.uk",
    # Moray Council
    "moray.gov.uk",
    # North Ayrshire Council
    "north-ayrshire.gov.uk",
    # North Lanarkshire Council
    "northlanarkshire.gov.uk",
    # Orkney Islands Council
    "orkney.gov.uk",
    # Perth and Kinross Council
    "pkc.gov.uk",
    # Renfrewshire Council
    "renfrewshire.gov.uk",
    # Scottish Borders Council
    "scotborders.gov.uk",
    # Shetland Islands Council
    "shetland.gov.uk",
    # South Ayrshire Council
    "south-ayrshire.gov.uk",
    # South Lanarkshire Council
    "southlanarkshire.gov.uk",
    # Stirling Council
    "stirling.gov.uk",
    # West Dunbartonshire Council
    "west-dunbarton.gov.uk",
    # West Lothian Council
    "westlothian.gov.uk",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.8 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SCOTTISH_COUNCILS",
    "SOURCE_ID",
    "THEME_CODE",
]