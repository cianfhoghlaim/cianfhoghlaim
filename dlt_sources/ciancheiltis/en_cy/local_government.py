"""PR0.3 — Phase 1 T8 (Local government) — 22 Welsh Local Authorities DLT source.

Deferred stub. PR0.3 will seed URLs for all 22 Welsh LAs (Anglesey,
Gwynedd, Conwy, Denbighshire, Flintshire, Wrexham, Powys,
Ceredigion, Pembrokeshire, Carmarthenshire, Swansea, Neath Port
Talbot, Bridgend, Vale of Glamorgan, Cardiff, Rhondda Cynon Taf,
Merthyr Tydfil, Caerphilly, Blaenau Gwent, Torfaen, Monmouthshire,
Newport) plus the 3 national parks.
"""
SOURCE_ID = "ciancheiltis.en_cy.local_government"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_cy/local_government_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-cy"


WELSH_LOCAL_AUTHORITIES = [
    "anglesey.gov.wales",
    "gwynedd.llyw.cymru",
    "conwy.gov.uk",
    "denbighshire.gov.uk",
    "flintshire.gov.uk",
    "wrexham.gov.uk",
    "powys.gov.uk",
    "ceredigion.gov.uk",
    "pembrokeshire.gov.uk",
    "carmarthenshire.gov.wales",
    "swansea.gov.uk",
    "neath-porttalbot.gov.uk",
    "bridgend.gov.uk",
    "valeofglamorgan.gov.uk",
    "cardiff.gov.uk",
    "rctcbc.gov.uk",
    "merthyr.gov.uk",
    "caerphilly.gov.uk",
    "blaenau-gwent.gov.uk",
    "torfaen.gov.uk",
    "monmouthshire.gov.uk",
    "newport.gov.uk",
]


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    del firecrawl_client
    return []


__all__ = [
    "SOURCE_ID",
    "LANCE_TABLE",
    "THEME_CODE",
    "LANGUAGE_PAIR",
    "WELSH_LOCAL_AUTHORITIES",
]
