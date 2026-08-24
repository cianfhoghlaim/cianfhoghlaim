"""16 NCCA JC short-course DLT sources (BIEP v2).

Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change.

The 16 NCCA JC short courses:
    coding, chinese, japanese, russian, polish, lithuanian, portuguese,
    arabic, hebrew, philosophy, film_studies, financial_literacy,
    media_literacy, personal_professional_development, digital_media,
    athletic_studies.

Each short-course DLT source is a thin per-course re-export of the
`build_jc_short_course_source` factory at:
    dlt/british_isles/ireland/education/junior_cycle_short_courses/_factory.py

The destination DuckLake namespace is:
    cianfhoghlaim.education.british_isles.ireland.junior_cycle.short_courses.<course_slug>
"""
