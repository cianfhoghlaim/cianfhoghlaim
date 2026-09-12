"""MotherDuck Flight: ciancheiltis_en_ga_ni_flight.

Daily BAML backfill for the en-ga-ni (Northern Ireland) phase of
the ciancheiltis umbrella. Runs the L1 ingestion + L2 BAML extraction
+ L3 CocoIndex mount for the 8 Phase 3 themes, then surfaces the
bilingual-pair coverage to the Phase 3 RAGAS gate (≥ 0.70 + ≥ 500
pairs seeded).

Phase 3 is the Northern Ireland (en-ga) jurisdiction — the third
of the 6 ciancheiltis language-pair stages. Northern Ireland has a
constitutional + statutory bilingual framework distinct from the
Republic of Ireland's Official Languages Act 2003: the Identity and
Language (Northern Ireland) Act 2022 establishes Irish + Ulster
Scots as recognised languages (in addition to English), and the
Good Friday Agreement 1998 commits the NI Executive to "respect,
protect and fulfil" the linguistic diversity of the region. The
canonical bilingual reference is
`https://www.legislation.gov.uk/uksi/2022/15/contents/made` — the
Identity and Language (Northern Ireland) Act 2022 itself.

This Flight is the canonical entry-point for the
`ciancheiltis_en_ga_ni_bilingual_pairs` MotherDuck Dive and is
paired with the marimo notebook `notebooks/ciancheiltis_en_ga_ni.py`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_ga_ni_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_ga_ni",
    "northern_ireland",
    "bilingual",
    "phase_3",
    "daily_sync",
)


def build_ciancheiltis_en_ga_ni_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-ga-ni (NI) phase."""
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
    "build_ciancheiltis_en_ga_ni_flight",
]
