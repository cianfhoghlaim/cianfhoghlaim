"""England government sources — DLT scaffold for the 7 official England sources.

Per the 2026-09-01-firecrawl-england-source-discovery-v1 change
(Step 3 of the cianfhoghlaim-nua v6 era plan). The skeleton fires
the 5-step pattern in Step 4 (England expansion).

The 7 canonical England sources are documented at
`data/bi_ep/syllabi_raw/england/README.md`. This module is the
canonical DLT source entry point for the England jurisdiction.

Reference: openspec/changes/2026-09-01-firecrawl-england-source-discovery-v1/
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt

from dlt_sources.common.destinations import named_destinations

import dlt_sources

REPO_ROOT = Path(__file__).resolve().parents[5]
INGEST_QUEUE = REPO_ROOT / "stedding" / "ingest_queue" / "england"


@dlt.resource(name="england_gov_sources", write_disposition="merge", primary_key=["url"])
def england_gov_sources() -> Iterator[dict[str, Any]]:
    """Yield one row per canonical England education source PDF.

    Each row has: source_name + canonical_url + scrape_status +
    last_checked + language (en) + jurisdiction (EN) + stage +
    subject_slug.
    """
    canonical_sources = [
        # DfE national curriculum programmes of study
        ("dfe_national_curriculum_maths_primary", "https://www.gov.uk/government/publications/national-curriculum-in-england-mathematics-programmes-of-study", "primary", "mathematics"),
        ("dfe_national_curriculum_maths_secondary", "https://www.gov.uk/government/publications/national-curriculum-in-england-mathematics-programmes-of-study", "secondary", "mathematics"),
        ("dfe_national_curriculum_english_primary", "https://www.gov.uk/government/publications/national-curriculum-in-england-english-programmes-of-study", "primary", "english"),
        ("dfe_national_curriculum_english_secondary", "https://www.gov.uk/government/publications/national-curriculum-in-england-english-programmes-of-study", "secondary", "english"),
        # Ofqual grade descriptors
        ("ofqual_gcse_grade_descriptors", "https://www.gov.uk/government/publications/gcse-subject-level-conditions-and-requirements", "secondary", "all"),
        ("ofqual_alevel_grade_descriptors", "https://www.gov.uk/government/publications/gce-advanced-level-conditions-and-requirements", "secondary", "all"),
        # AQA (43 GCSE + 49 A-Level PDFs)
        ("aqa_gcse_maths_spec", "https://www.aqa.org.uk/subjects/mathematics/gcse/mathematics-8300", "secondary", "mathematics"),
        ("aqa_alevel_chemistry_spec", "https://www.aqa.org.uk/subjects/chemistry/as-and-a-level/chemistry-7404-7405", "secondary", "chemistry"),
        # OCR (43 GCSE + 49 A-Level PDFs)
        ("ocr_gcse_maths_spec", "https://www.ocr.org.uk/qualifications/gcse/mathematics-j560-from-2015", "secondary", "mathematics"),
        ("ocr_alevel_chemistry_spec", "https://www.ocr.org.uk/qualifications/as-a-level/chemistry-a-h032-h432-from-2015", "secondary", "chemistry"),
        # Pearson Edexcel (43 GCSE + 49 A-Level PDFs)
        ("pearson_gcse_maths_spec", "https://qualifications.pearson.com/en/qualifications/edexcel-gcses/mathematics-2015", "secondary", "mathematics"),
        ("pearson_alevel_chemistry_spec", "https://qualifications.pearson.com/en/qualifications/edexcel-alevels/chemistry-2015", "secondary", "chemistry"),
        # UCAS subject guides
        ("ucas_subject_guide_maths", "https://www.ucas.com/explore/subjects/mathematics", "university", "mathematics"),
        ("ucas_subject_guide_chemistry", "https://www.ucas.com/explore/subjects/chemistry", "university", "chemistry"),
    ]
    for source_name, url, stage, subject_slug in canonical_sources:
        yield {
            "source_name": source_name,
            "canonical_url": url,
            "scrape_status": "pending",
            "last_checked": datetime.now(UTC).isoformat(),
            "language": "en",
            "jurisdiction": "EN",
            "stage": stage,
            "subject_slug": subject_slug,
            "pdf_path": None,  # populated by the Firecrawl scraper
        }


@dlt.source(name="england_gov_source")
def england_gov_source() -> Any:
    return england_gov_sources


__all__ = ["england_gov_sources", "england_gov_source"]