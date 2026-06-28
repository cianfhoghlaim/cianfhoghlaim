"""Northern Ireland — geospatial domain stub (Plan 3 PRESERVED).

This is one of the 7 cross-domain sources for Northern Ireland.
Authority: Northern Ireland Executive (gov.uk/government/organisations/department-of-education)

Coverage: STUB ONLY. The actual DLT source for this domain will be
created when Plan 3 implementation lands.

Source schema layout is PROVISIONAL — refactor after Plan 1 informs best
CocoIndex + DLT + DuckDB + DuckLake + Lance patterns.
"""

NATION = "ni"
DOMAIN = "geospatial"
SAMPLING_RATE = 0.1
CHUNK_SIZE_TOKENS = 1024
OVERLAP_TOKENS = 128


def is_plan1_active() -> bool:
    return False


def is_plan3_stub() -> bool:
    return True
