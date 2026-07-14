"""Per-subject DLT sources for the Ireland Junior Cycle (BIEP v2).

36 per-subject DLT sources (18 NCCA JC subjects × 2 languages EN + GA)
that read cached PDFs from `/stedding/ingest_queue/junior_cycle/<subject>/<lang>/`
and yield records tagged with the canonical jurisdiction + language metadata.

All 36 sources share the same factory pattern — they differ only by:
- `subject` slug
- `language` (en / ga)
- The destination DuckLake namespace

The 18 subjects (per `JC_SUBJECTS` in `dlt/british_isles/ireland/education/junior_cycle.py`):
    english, gaeilge, mathematics, irish_history, geography, science,
    business_studies, french, german, spanish, italian, home_economics,
    music, art, technology, engineering, graphics, wood_technology.

The per-subject DLT sources are at:
    dlt/british_isles/ireland/education/junior_cycle_subjects/<subject>_<lang>.py

The factory in `dlt/british_isles/ireland/education/junior_cycle_subjects/_factory.py`
generates the per-subject sources at import time so all 36 share the same
tested code path.

The destination is the canonical DuckLake namespace:
    oideachais.education.british_isles.ireland.junior_cycle.<subject>.<lang>

Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
"""
