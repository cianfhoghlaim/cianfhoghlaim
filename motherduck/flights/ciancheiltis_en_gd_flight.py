"""MotherDuck Flight: ciancheiltis_en_gd_flight.

Daily BAML backfill for the en-gd (Scotland) phase of the ciancheiltis
umbrella. Runs the L1 ingestion + L2 BAML extraction + L3 CocoIndex
mount for the 8 Phase 4 themes, then surfaces the bilingual-pair
coverage to the Phase 4 RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded).

Phase 4 is the Scotland (en-gd) jurisdiction — the fourth of the 6
ciancheiltis language-pair stages. Scotland has a statutory bilingual
framework distinct from Wales (Phase 1), Republic of Ireland (Phase
2), and Northern Ireland (Phase 3): the Gaelic Language (Scotland)
Act 2005 (asp/2005/7) established Bòrd na Gàidhlig as the principal
public authority for the Gaelic language in Scotland and gave
Scottish Ministers a duty to promote the use of Gaelic. The
canonical bilingual reference is
`https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/` — Bòrd na
Gàidhlig under the 2005 Act.

This Flight is the canonical entry-point for the
`ciancheiltis_en_gd_bilingual_pairs` MotherDuck Dive and is paired
with the marimo notebook `notebooks/ciancheiltis_en_gd.py`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_gd_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_gd",
    "scotland",
    "bilingual",
    "phase_4",
    "daily_sync",
)


def build_ciancheiltis_en_gd_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-gd (Scotland) phase."""
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
    "build_ciancheiltis_en_gd_flight",
]
