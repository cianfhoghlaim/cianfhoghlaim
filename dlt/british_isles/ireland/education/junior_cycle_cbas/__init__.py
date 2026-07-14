"""36 NCCA JC CBA DLT sources (BIEP v2).

Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change.

The 18 NCCA JC subjects each have 2 CBAs (Year 2 + Year 3) = 36 total.
The CBA IDs are: ``<subject>_1`` + ``<subject>_2`` for each of the 18 subjects.

Each CBA DLT source is a thin re-export of the `build_jc_cba_source(cba_id=...)`
factory at:
    dlt/british_isles/ireland/education/junior_cycle_cbas/_factory.py
"""
