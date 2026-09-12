"""PR0.9 — Phase 5 T8 (Local government) — Isle of Man unique governance structure DLT source.

Deferred stub. PR0.9 will seed URLs for the **unique Isle of Man
local government structure** (the ``MANX_LOCAL_GOVERNANCE``
constant below).

The Isle of Man does **NOT** have county councils (Phase 1 /
Phase 2 / Phase 4 do not apply). Instead, it has a unique local
government structure established under the Local Government Act
1985 (as amended) + the Tynwald tradition:

- **6 sheadings** (the 6 historic subdivisions — Ayre, Garff,
  Glenfaba, Michael, Middle, Rushen — the Sheading Commissioners
  are ceremonial / electoral only, not administrative).
- **4 town authorities** (Douglas, Ramsey, Peel, Castletown — the
  4 historic "parish towns" each with their own Town
  Commissioners acting as a town authority, with Douglas
  administered by the Douglas Borough Council as the principal
  urban authority).
- **1 Department of Infrastructure** (the central department of
  the Isle of Man Government that delivers the island-wide
  services that local authorities would in other UK nations).

Manx (Gaelg) is in revival status — Manx-language content in
local government publications is sparse (typically limited to the
traditional place names + the section headers of the 4 Town
Commissioners' websites, where published). The umbrella spec's
content-based language detector is the gate and is expected to
flag most rows as English-only.

PR0.9 will use
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
to pair the EN landing page (or service page) with its GV mirror
where published and write one LanceDB row per bilingual page
pair via ``ciancheiltis_en_gv_embedding``.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_gv.local_government"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_gv/local_government_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-gv"


# The unique Isle of Man local government structure (per the Local
# Government Act 1985 + the Tynwald tradition). The Isle of Man
# does NOT have county councils; it has 6 sheadings (ceremonial /
# electoral only), 4 town authorities (the 4 historic parish
# towns), and 1 Department of Infrastructure (the central
# department for island-wide services).
MANX_LOCAL_GOVERNANCE: tuple[str, ...] = (
    # Department of Infrastructure — the Isle of Man Government
    # central department for island-wide services (highways,
    # utilities, planning, building control, public transport,
    # harbours, airports). The closest Manx equivalent of a UK
    # county council, but it is a central department rather than
    # a locally-elected body.
    "gov.im",
    # Douglas Borough Council — the principal urban authority for
    # Douglas (the capital). The largest of the 4 town authorities
    # by population. Publishes service information for the
    # Douglas urban area.
    "douglas.gov.im",
    # Ramsey Town Commissioners — the town authority for Ramsey
    # (the second-largest town on the Isle of Man).
    "ramsey.gov.im",
    # Peel Town Commissioners — the town authority for Peel (the
    # western town, home to the House of Manannan museum).
    "peel.gov.im",
    # Castletown Town Commissioners — the town authority for
    # Castletown (the historic capital until 1869, home to
    # Castle Rushen).
    "castletown.gov.im",
    # Ayre Sheading Commissioners — the ceremonial / electoral
    # body for the Ayre sheading (the northern sheading
    # including the Point of Ayre).
    "ayre.gov.im",
    # Garff Sheading Commissioners — the ceremonial / electoral
    # body for the Garff sheading (the eastern sheading including
    # Laxey).
    "garff.gov.im",
    # Glenfaba Sheading Commissioners — the ceremonial /
    # electoral body for the Glenfaba sheading (the western
    # sheading including Peel + St John's).
    "glenfaba.gov.im",
    # Michael Sheading Commissioners — the ceremonial / electoral
    # body for the Michael sheading (the southern sheading
    # including Castletown + Port Erin).
    "michael.gov.im",
    # Middle Sheading Commissioners — the ceremonial / electoral
    # body for the Middle sheading (the central sheading
    # including Douglas).
    "middle.gov.im",
    # Rushen Sheading Commissioners — the ceremonial / electoral
    # body for the Rushen sheading (the south-western sheading
    # including Port Erin + Port St Mary).
    "rushen.gov.im",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.9 wires Firecrawl.

    Manx (Gaelg) is in revival status — Manx-language content in
    local government publications is sparse (typically limited to
    the traditional place names + the section headers of the 4
    Town Commissioners' websites, where published). PR0.9 will
    pair every English local government page with whatever Manx
    content exists.
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "MANX_LOCAL_GOVERNANCE",
    "SOURCE_ID",
    "THEME_CODE",
]
