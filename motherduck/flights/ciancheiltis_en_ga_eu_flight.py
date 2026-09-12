"""MotherDuck Flight: ciancheiltis_en_ga_eu_flight.

Daily BAML backfill for the en-ga (European Union) phase of the
ciancheiltis umbrella — the **FINAL** phase of the 6-phase
ciancheiltis spine (Phase 1 en-cy / Phase 2 en-ga-roi / Phase 3
en-ga-ni / Phase 4 en-gd / Phase 5 en-gv / Phase 6 en-ga-eu).
Runs the L1 ingestion + L2 BAML extraction + L3 CocoIndex mount for
the 8 Phase 6 themes, then surfaces the bilingual-pair coverage to
the Phase 6 RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded — aspirational
on Phase 6 because EU-level coverage is PARTIAL for Irish per
Council Decision (EU) 2020/2172 + Council Regulation No 1/1958 +
Article 55 of the Treaty on European Union — see the Dive
`BILINGUAL_PAIRS_DIVE_GA_EU` description for the partial-coverage
caveat).

Phase 6 is the European Union (en-ga) jurisdiction — the **FINAL**
phase of the 6-phase ciancheiltis umbrella. Irish (Gaeilge) is a
treaty language under Article 55 of the Treaty on European Union
(TEU) + Council Regulation No 1/1958, and a full official EU language
since Council Decision (EU) 2020/2172 took effect on 2022-01-01.
The canonical bilingual reference is
`https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E` —
the Irish-language edition of the Treaty on European Union (the
Lisbon 2012 TEU, CELEX 12012E).

Phase 6 differs from Phases 1–5 in TWO structural ways:
1. **Partial coverage**. EU-level coverage is **partial** for Irish:
   many EU documents exist only in English plus a "summary in
   Irish" rather than a full Irish translation (this is the
   documented Council Decision (EU) 2020/2172 derogation for older
   acts pre-dating 2022-01-01). The Phase 6 schema captures the
   `language_availability` ∈ {"full", "partial", "summary_only"}
   axis as a first-class column on every per-phase row. The 500-pair
   gate from the ciancheiltis spec is therefore ASPIRATIONAL on
   Phase 6.
2. **The eighth theme is `institutions` (not `local_government`)**.
   The EU is sui generis — no sub-EU municipalities have a statutory
   Irish-language obligation. The 8th theme captures the EU
   institutions family (Commission + Parliament + Council + ECB +
   EIB + EIF), with the canonical example
   `https://www.ecb.europa.eu/home/html/index.ga.html` (Banc
   Ceannais Eorpach — the Irish-language ECB portal).

**Phase 6 is the FINAL Flight** of the ciancheiltis Flight registry
— after this Flight lands + the L1 ingestion completes + the L2 BAML
extraction runs + the L3 CocoIndex embedding mounts + the L4 asset
checks evaluate + the L5 anomaly sensor runs, the ciancheiltis
umbrella is complete (all 6 phases: en_cy, en_ga_roi, en_ga_ni,
en_gd, en_gv, en_ga_eu).

This Flight is the canonical entry-point for the
`ciancheiltis_en_ga_eu_bilingual_pairs` MotherDuck Dive and is paired
with the marimo notebook `notebooks/ciancheiltis_en_ga_eu.py` (which
includes a 5th umbrella-completion cell that renders a 6-row summary
table across all 6 phases — this is the final-tally dashboard).
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_ga_eu_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_ga_eu",
    "european_union",
    "bilingual",
    "phase_6",
    "daily_sync",
)


def build_ciancheiltis_en_ga_eu_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-ga (EU) phase — Phase 6 FINAL.

    Phase 6 differs from Phases 1–5 in TWO ways:
    1. Partial coverage — the `language_availability` ∈ {`full`,
       `partial`, `summary_only`} axis is the Phase 6 unique
       dimension (many EU documents exist only in English plus a
       "summary in Irish" rather than a full Irish translation).
       The 500-pair gate is therefore ASPIRATIONAL on Phase 6.
    2. The eighth theme is `institutions` (not `local_government`)
       — the EU is sui generis with no sub-EU municipal tier.

    **This Flight is the FINAL entry in the ciancheiltis Flight
    registry** — after this Flight lands, the 6-phase ciancheiltis
    spine (en_cy, en_ga_roi, en_ga_ni, en_gd, en_gv, en_ga_eu) is
    COMPLETE.
    """
    run_flight(
        name=FLIGHT_NAME,
        cron=FLIGHT_CRON,
        timezone=FLIGHT_TIMEZONE,
        schedule_kind="daily",
        started_at=datetime.now(UTC).isoformat(),
        tags=list(FLIGHT_TAGS),
    )


__all__ = [
    "FLIGHT_NAME",
    "FLIGHT_CRON",
    "FLIGHT_TIMEZONE",
    "FLIGHT_TAGS",
    "build_ciancheiltis_en_ga_eu_flight",
]
