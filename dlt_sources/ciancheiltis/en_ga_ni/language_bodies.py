"""PR0.7 — Phase 3 T5 (Language bodies) — CnaG + TEO + Ulster-Scots Agency DLT source.

Deferred stub. PR0.7 will crawl the bilingual (or Irish-primary / Ulster
Scots-primary) publications of the 3 canonical sister bodies that
govern the Irish language (and Ulster Scots) in Northern Ireland under
the **Identity and Language (Northern Ireland) Act 2022** + the
predecessor **St Andrews Agreement 2006** + the **Northern Ireland Act
1998** (the Belfast/Good Friday Agreement constitutional basis).

The 3 sister bodies (``NI_LANGUAGE_BODIES`` constant below) are the
canonical Phase 3 § T5 dataset: every body publishes bilingual or
Irish-only / Ulster-Scots-only content required by statute, and every
body is the canonical ground truth for at least one subset of the
en-ga ground-truth pair (note: Phase 3 covers en-ga only — Ulster Scots
falls under a separate en-gv Phase 5-style pair that is NOT in scope
for PR0.7 but is acknowledged here).
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_ni.language_bodies"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni/language_bodies_chunks"
THEME_CODE = "T5"
LANGUAGE_PAIR = "en-ga"


NI_LANGUAGE_BODIES: tuple[str, ...] = (
    # Comhairle na Gaelscolaíochta (CnaG) — the regulator of Irish-medium
    # schools (Gaelscoileanna) and the Irish-medium Aonad support
    # network across Northern Ireland. Established 2000; re-established
    # under the Identity and Language (Northern Ireland) Act 2022.
    "comhairle.org",
    # The Executive Office (TEO) — the cross-departmental NI Executive
    # department responsible for the Irish Language Act Implementation
    # Branch + the Ulster Scots language policy. Hosts the Irish
    # Language Commissioner (established under the 2022 Act) and the
    # Commissioner for Ulster Scots. Bilingual EN + GA publication
    # surface under the Executive Office's "Good Relations" portfolio.
    "executiveoffice-ni.gov.uk",
    # The Ulster-Scots Agency (Tha Boord o Ulstèr-Scotch / Ulster-Scots
    # Agency) — the cross-border language body funded by the NI
    # Executive and the Republic's Department of Tourism, Culture,
    # Arts, Gaeltacht, Sport and Media. Publishes both English and
    # Scots-language content under the North/South language-bodies
    # framework (per the 1999 Implementation Bodies Agreement).
    "ulsterscotsagency.com",
)


def collect(*, firecrawl_client=None):
    """Deferred — returns an empty list until PR0.7 wires Firecrawl."""
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "NI_LANGUAGE_BODIES",
    "SOURCE_ID",
    "THEME_CODE",
]
