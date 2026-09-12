"""PR0.10 — Phase 6 T8 (Local government → EU institutions) — EU institutions + agencies DLT source.

This is the en-ga / EU level theme T8 source. The umbrella spec's
10-theme taxonomy uses T8 for "Local government" in the Phase 1-5
national context (Wales / ROI / NI / Scotland / IoM). At the EU
level there is **no local government** (the EU has 27 member
states but no regional/local government structure analogous to the
Welsh county councils or the Irish city & county councils).

Phase 6 therefore remaps T8 to **EU institutions + agencies** —
the EU-level governance bodies that publish in Irish. This is the
canonical Phase 6 § T8 dataset, parallel to the Phase 5 § T8
``MANX_LOCAL_GOVERNANCE`` constant (which lists the Isle of Man's
unique local government structure because the IoM also has no
"county councils" in the Phase 1 / Phase 4 sense).

The ``EU_INSTITUTIONS`` constant below enumerates the **9 main EU
institutions** (the canonical EU governance bodies under the TEU +
TFEU) + the **3 key EU agencies / bodies** that publish
significant bilingual content (Eurofound, Eurojust, EUROPOL +
FRA). Every body is the canonical ground truth for at least one
subset of the en-ga Phase 6 ground-truth pair.

Canonical example: the European Parliament, Irish-language
plenary debates, at ``https://www.europarl.europa.eu/doceo/document/PLENARY-..._GA.pdf``
— the European Parliament publishes Irish-language plenary
documents when Irish-language interpretation is requested by an MEP
(this is the most visible Irish-language presence in the EU
institutions).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
is reused (per the Phase 1 § bilingual-page-validator section) to
canonicalise the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` can write ONE LanceDB row per
institution publication (with both EN and GA embeddings where the
GA side exists; the BAML coverage gate + ``language_availability``
tag flag the partial rows but does not drop them).
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.institutions"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/institutions_chunks"
THEME_CODE = "T8"
LANGUAGE_PAIR = "en-ga"


# The 9 main EU institutions + 3 key EU agencies / bodies — the
# canonical Phase 6 § T8 governance dataset. The EU has **no
# local government** so Phase 6 T8 is remapped to EU institutions
# + agencies (parallel to the Phase 5 § T8 MANX_LOCAL_GOVERNANCE
# remap for the Isle of Man's unique local government structure).
EU_INSTITUTIONS: tuple[str, ...] = (
    # European Council — the EU's political head body (heads of
    # state or government of the 27 member states). Publishes
    # Irish-language conclusions when Ireland holds the rotating
    # Presidency of the Council of the EU.
    "consilium.europa.eu/en/european-council",
    # Council of the European Union — the EU's main legislative
    # body (ministers of the 27 member states). The principal EU
    # institution for Irish-language publications via the Council
    # Irish Language Unit.
    "consilium.europa.eu",
    # European Commission — the EU's executive body (the
    # 27 Commissioners, one per member state). The Commission
    # publishes a partial Irish-language presence via the
    # Commission's Irish-language translation service within DG
    # Translation.
    "ec.europa.eu",
    # European Parliament — the EU's directly-elected body (the
    # 720 MEPs). The Parliament has the most visible Irish-
    # language presence among the EU institutions — Irish-language
    # plenary debates + selected Irish-language committee
    # documents.
    "europarl.europa.eu",
    # European Central Bank (ECB) — the EU's central bank + the
    # monetary authority for the euro area. The ECB publishes
    # primarily in English + selected Irish-language press
    # releases when Ireland is represented in the ECB Governing
    # Council.
    "ecb.europa.eu",
    # European Investment Bank (EIB) — the EU's long-term
    # lending bank. Publishes primarily in English + French +
    # German + selected Irish-language press releases.
    "eib.org",
    # Court of Justice of the European Union (CJEU) — the EU's
    # judicial body (Court of Justice + General Court + Civil
    # Service Tribunal). Publishes primarily in English only (see
    # T7 caveat).
    "curia.europa.eu",
    # European Court of Auditors (ECA) — the EU's external
    # auditor. Publishes annual reports in all 24 official EU
    # languages, including Irish.
    "eca.europa.eu",
    # European Committee of the Regions (CoR) — the EU's
    # assembly of regional + local representatives from the 27
    # member states. The CoR publishes selected Irish-language
    # opinions + resolutions.
    "cor.europa.eu",
    # European Economic and Social Committee (EESC) — the EU's
    # assembly of employers, trade unions + civil society
    # representatives. Publishes selected Irish-language opinions
    # + resolutions.
    "eesc.europa.eu",
    # Eurofound — the European Foundation for the Improvement of
    # Living and Working Conditions (a tripartite EU agency in
    # Dublin). Publishes selected Irish-language research
    # summaries.
    "eurofound.europa.eu",
    # Eurojust — the EU Agency for Criminal Justice Cooperation
    # (an EU agency in The Hague). Publishes primarily in English.
    "eurojust.europa.eu",
    # EUROPOL — the EU Agency for Law Enforcement Cooperation
    # (an EU agency in The Hague). Publishes primarily in English.
    "europol.europa.eu",
    # FRA — the EU Agency for Fundamental Rights (an EU agency
    # in Vienna). Publishes selected Irish-language fundamental
    # rights reports.
    "fra.europa.eu",
)


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    EU-level Irish-language coverage is partial across the
    institutions + agencies — the Parliament has the most visible
    Irish-language presence; the Commission + Council + ECB + EIB
    + ECA + CoR + EESC + FRA + Eurofound each publish selectively;
    the CJEU + Eurojust + EUROPOL are English-only in practice
    (see the T7 partial-coverage caveat).

    PR0.10 will surface every bilingual institution publication
    with its ``language_availability`` tag.
    """
    del firecrawl_client
    return []


__all__ = [
    "EU_INSTITUTIONS",
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "SOURCE_ID",
    "THEME_CODE",
]
