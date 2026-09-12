"""PR0.10 — Phase 6 T4 (Healthcare) — EMA + ECDC DLT source.

This is the en-ga / EU level theme T4 source: every EMA (European
Medicines Agency) + ECDC (European Centre for Disease Prevention
and Control) publication paired with its Irish-language equivalent
where published.

**Partial Phase 6 T4 (caveat prominently documented)**: EU medical
content is **overwhelmingly English-only**. The EMA + ECDC publish
their clinical guidelines, product information (SmPCs) and patient
information leaflets primarily in English, with selected Irish
summaries only for high-profile public-health notices. The
``language_availability`` field is the **critical signal** here —
most rows will be tagged ``summary_only`` or English-only.

Canonical example: the EMA's European public assessment report
(EPAR) at
``https://www.ema.europa.eu/en/medicines/human/EPAR/<name>`` paired
with the Irish-language equivalent at
``https://www.ema.europa.eu/ga/medicines/human/EPAR/<name>`` where
published — typically the patient information leaflet + selected
public summaries.

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` writes ONE LanceDB row per
EMA / ECDC publication with both EN + GA embeddings where the GA
side exists; the BAML coverage gate + ``language_availability``
tag flag the partial rows but does not drop them.

Phase 6 T4 is the **smallest healthcare corpus of the 6 phases**
(CY/GA-ROI/GA-NI/GD/GV/EU). Unlike Phase 2 HSE Ireland (which ships
partial Irish content) or Phase 4 NHS Scotland (which ships a wide
bilingual surface at nhsinform.scot/gd/), Phase 6 EMA + ECDC
publishes almost no Irish content at all. The umbrella spec
acknowledges Phase 6 § T4 as a "partial" theme — the BAML coverage
gate will flag most rows as English-only or summary_only.

The underlying single-language EMA + ECDC pipelines are NOT yet
seeded in ``dlt_sources/european_union/medicine/`` (only the
shared ``EUInstitutionalSource`` base exists at
``dlt_sources/european_union/_shared/``). Phase 6 § T4 is the
first phase to populate that sub-tree.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.healthcare"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/healthcare_chunks"
THEME_CODE = "T4"
LANGUAGE_PAIR = "en-ga"

# Phase 6 T4 is partial coverage — most EU medical content is
# English-only or summary_in_irish. The ``language_availability``
# field is the critical signal here. Subagent 3 picks this up for
# the MotherDuck Dive caveat.
PARTIAL_COVERAGE = True


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    Most EU medical content is English-only or summary_in_irish.
    PR0.10 will pair every English EMA / ECDC publication with
    whatever Irish content exists and surface the
    ``language_availability`` tag (``full`` / ``partial`` /
    ``summary_only``).
    """
    del firecrawl_client
    return []


__all__ = [
    "LANCE_TABLE",
    "LANGUAGE_PAIR",
    "PARTIAL_COVERAGE",
    "SOURCE_ID",
    "THEME_CODE",
]
