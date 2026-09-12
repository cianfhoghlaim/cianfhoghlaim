"""PR0.10 — Phase 6 T2 (Policy / consultations) — EU Commission public consultations + EU Council press releases DLT source.

This is the en-ga / EU level theme T2 source: every EU Commission
public consultation (under the "Have your say" portal at
``ec.europa.eu/info/law/better-regulation/``) + every EU Council
press release (the Council of the European Union publishes a small
Irish-language presence — primarily the Irish-language
interpretation of high-profile press conferences + General Affairs
Council conclusions when Ireland holds the Presidency of the
Council of the EU).

Canonical example: the EUR-Lex Treaty press release for the
signing of an EU Treaty, Irish-language edition, at
``https://www.consilium.europa.eu/ga/press/press-releases/`` — the
EU Council Irish-language press release archive (the Irish-language
presence is partial — selected press releases only, primarily when
Ireland holds the rotating Presidency).

The bilingual page validator at
``dlt_sources/ciancheiltis/_shared/bilingual_page_validator.py``
canonicalises the (en, ga) URL pair to a single ``chunk_id`` so
``ciancheiltis_en_ga_eu_embedding`` writes ONE LanceDB row per
consultation / press release with both EN + GA embeddings where the
GA side exists; the ``language_availability`` tag
(``full`` / ``partial`` / ``summary_only``) is the critical signal
here because most EU consultation / press release content is
English-only.

Phase 6 T2 is **partial coverage** — the EU Council Irish-language
presence is small (selected press releases only) and most EU
Commission consultation content is English-only. The umbrella spec
acknowledges Phase 6 § T2 as a "partial" theme — the BAML coverage
gate will flag most rows as English-only.

PR0.10 will:

- ``firecrawl_map`` the EU Commission public consultations portal
  + the EU Council press release archive (the Irish switch is
  ``.../ga/press/press-releases/`` for the Council).
- ``firecrawl_scrape`` with the bilingual page validator to assert
  the (en, ga) pair refer to the same article.
- Surface the ``language_availability`` tag for every row.
"""
from __future__ import annotations

SOURCE_ID = "ciancheiltis.en_ga_eu.policy_consultations"
LANCE_TABLE = "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu/policy_consultations_chunks"
THEME_CODE = "T2"
LANGUAGE_PAIR = "en-ga"

# Phase 6 T2 is partial coverage — the EU Council Irish-language
# presence is small (selected press releases only) and most EU
# Commission consultation content is English-only. The umbrella spec
# acknowledges Phase 6 § T2 as a "partial" theme; subagent 3 picks
# this up for the MotherDuck Dive caveat.
PARTIAL_COVERAGE = True


def collect(*, firecrawl_client=None):  # noqa: ANN001 - stub param
    """Deferred — returns an empty list until PR0.10 wires Firecrawl.

    EU-level coverage is **partial** for Irish — the EU Council
    Irish-language presence is small (selected press releases only)
    and most EU Commission consultation content is English-only.
    PR0.10 will surface every bilingual consultation / press
    release pair with its ``language_availability`` tag.
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
