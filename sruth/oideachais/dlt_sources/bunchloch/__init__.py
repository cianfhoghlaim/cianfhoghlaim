"""
Bunchloch DLT sources for research document ingestion.

Processes local files from bunchloch research directory:
- comp_science/  (CT###: CT874, CT545, CT511 - CS courses)
- gaeilge/       (GA###/GF###: GA101, GA201 - Irish language)
- mata/          (Applied Statistics, Networks - Mathematics)
- oideachas/     (ED###, lesson plans - Education)

Migrated from sruth.taighde.dlt_sources.filesystem_source.
"""

from .filesystem_source import (
    bunchloch_source,
    bunchloch_by_subject_source,
    create_bunchloch_pipeline,
    run_full_ingestion,
    scan_directory,
    BUNCHLOCH_PATH,
    SUBJECT_PATHS,
)

__all__ = [
    "bunchloch_source",
    "bunchloch_by_subject_source",
    "create_bunchloch_pipeline",
    "run_full_ingestion",
    "scan_directory",
    "BUNCHLOCH_PATH",
    "SUBJECT_PATHS",
]
