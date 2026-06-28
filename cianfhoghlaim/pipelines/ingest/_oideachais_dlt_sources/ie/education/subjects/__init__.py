"""
Per-Subject DLT Sources for Irish Curriculum.

This module provides DLT resources for each subject, yielding:
- Subject pages (crawled content from NCCA/curriculumonline)
- Subject PDFs (PDF URLs discovered from pages)

Usage:
    from oideachais.dlt_sources.ie.education.subjects import (
        senior_cycle_source,
        junior_cycle_source,
        create_subject_source,
    )

    # Full Senior Cycle (40+ subjects)
    pipeline.run(senior_cycle_source(language="en"))

    # Single subject
    pages, pdfs = create_subject_source("mathematics", "senior_cycle", "en")
"""

from .base import (
    CrawledPage,
    PDFResource,
    crawl_subject,
    create_all_subject_resources,
    create_subject_source,
    extract_pdfs_from_subject,
)
from .junior_cycle import junior_cycle_source
from .senior_cycle import senior_cycle_source

__all__ = [
    # Data classes
    "CrawledPage",
    "PDFResource",
    "crawl_subject",
    "create_all_subject_resources",
    # Base functions
    "create_subject_source",
    "extract_pdfs_from_subject",
    "junior_cycle_source",
    # Cycle sources
    "senior_cycle_source",
]
