"""MotherDuck Flight: ciancheiltis_en_gv_flight.

Daily BAML backfill for the en-gv (Isle of Man) phase of the ciancheiltis
umbrella. Runs the L1 ingestion + L2 BAML extraction + L3 CocoIndex
mount for the 8 Phase 5 themes, then surfaces the bilingual-pair
coverage to the Phase 5 RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded —
aspirational on Phase 5 because Manx is a REVIVAL language under
Culture Vannin + Learn Manx + Bunscoill Ghaelgagh + Radio Manx with
NO statutory bilingual framework — see the Dive
`BILINGUAL_PAIRS_DIVE_GV` description for the revival-status caveat).

Phase 5 is the Isle of Man (en-gv) jurisdiction — the fifth of the 6
ciancheiltis language-pair stages. The Isle of Man is a CROWN DEPENDENCY
— Tynwald (the bicameral Isle of Man Parliament) is one of THREE
Crown Dependency legislatures in the British Isles (Jersey + Guernsey
are the other two). Phase 5 is the ONLY Crown Dependency with a
Celtic-language surface (Jersey + Guernsey have only Heritage Patois
material, which is out of scope for the revival-language strict gate).

Manx (Gaelg) is a REVIVAL language under active restoration — last
native speaker Ned Maddrell died in 1974; the modern corpus is a
constructed revival under Culture Vannin + Learn Manx + Bunscoill
Ghaelgagh + Radio Manx. There is NO statutory bilingual framework —
pages that DO have a Manx version are a bonus, NOT a baseline. The
canonical bilingual reference is
`https://www.culturevannin.im/learn-gaelg/` — Culture Vannin under
Tynwald (Tynwald Day 5 July is the oldest continuous parliament in
the world, dating to AD 979).

This Flight is the canonical entry-point for the
`ciancheiltis_en_gv_bilingual_pairs` MotherDuck Dive and is paired
with the marimo notebook `notebooks/ciancheiltis_en_gv.py`.
"""
from __future__ import annotations

from datetime import UTC, datetime

from motherduck.flights import run_flight


FLIGHT_NAME = "ciancheiltis_en_gv_flight"
FLIGHT_CRON = "0 4 * * *"
FLIGHT_TIMEZONE = "UTC"
FLIGHT_TAGS = (
    "ciancheiltis",
    "en_gv",
    "isle_of_man",
    "bilingual",
    "phase_5",
    "daily_sync",
)


def build_ciancheiltis_en_gv_flight() -> None:
    """Daily BAML backfill + RAGAS gate for the en-gv (Isle of Man) phase."""
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
    "build_ciancheiltis_en_gv_flight",
]
