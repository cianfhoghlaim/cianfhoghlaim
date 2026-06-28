"""Brezhoneg (Breton) — full source profile (Plan 3 stub, NOT British Isles).

Breton is a Brythonic Celtic language spoken in Brittany (France). It is
included in the cianfhoghlaim language registry for completeness (the
Bretons are historically linked to the Cornish via the 5th–6th century
Brythonic migration), but it is NOT a British Isles language and has no
nation/ source files.

Coverage: NONE in cianfhoghlaim. Breton is excluded from the 6 active
nations (ie, en, ni, wls, sct, iom) and the 2 legacy nations (jey, ggy).

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

# Plan 3 preserved: NONE (Breton is outside the British Isles)
PLAN_3_SOURCES: tuple[str, ...] = ()

# ISO 639-1 + ISO 639-2 codes for Breton
ISO_CODES: tuple[str, ...] = ("br", "bre", "bre-FR")


def is_active_in_plan1() -> bool:
    """Brezhoneg is NOT in Plan 1; it's a Plan 3 stub (excluded from British Isles)."""
    return False
