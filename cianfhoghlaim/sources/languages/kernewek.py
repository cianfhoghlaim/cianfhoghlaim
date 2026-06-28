"""Kernewek (Cornish) — full source profile (Plan 3 stub).

Cornish is the revived Celtic language of Cornwall (England). Standard
scholarly spelling is "kernewek"; the native alternative spelling
"kernowek" is sometimes used by revivalists — the codebase uses the
scholarly form for consistency.

Coverage (Plan 3 future stub):
- sources/nations/en/education/{early_childhood,primary,secondary}/kernewek.py
  (Cornwall is in England; tracked via the england nation + domain=culture)

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

from __future__ import annotations

# Plan 3 preserved (Cornwall, England)
PLAN_3_SOURCES: tuple[str, ...] = (
    "sources.nations.en.education.early_childhood.kernewek",
    "sources.nations.en.education.primary.kernewek",
    "sources.nations.en.education.secondary.kernewek",
)

# ISO 639-1 + ISO 639-2 codes for Cornish
ISO_CODES: tuple[str, ...] = ("kw", "cor", "corn")


def is_active_in_plan1() -> bool:
    """Kernewek is NOT in Plan 1; it's a Plan 3 stub."""
    return False
