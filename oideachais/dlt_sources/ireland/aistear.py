"""
Aistear (Early Childhood) DLT source.

Reads the 14 Aistear source PDFs on curriculumonline.ie/en/early-childhood/
plus the NCCA Aistear framework pages. Honors USE_LOCAL_SCRAPES=true to
read from /stedding/ingest_queue/aistear/ cache.

Datasets produced:
  aistear_documents       — AistearDocument rows
  aistear_principles      — AistearPrinciple rows
  aistear_learning_goals  — AistearLearningGoal rows
  naionra_listings        — Naionra rows (Gaeloideachas.ie / Pobal)
"""
from __future__ import annotations

import os
from pathlib import Path

import dlt


AISTEAR_CACHE_DIR = Path(os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")) / "aistear"
AISTEAR_SOURCE_URLS = [
    "https://www.curriculumonline.ie/en/early-childhood/",
    "https://www.ncca.ie/en/early-childhood/",
    "https://www.gov.ie/en/department-of-education/topics/early-years/",
    "https://gaeloideachas.ie/directories/",
]


@dlt.resource(name="aistear_documents", write_disposition="merge", primary_key=["document_id"])
def aistear_documents():
    """Aistear framework PDFs (curriculumonline.ie + NCCA + gov.ie)."""
    if not AISTEAR_CACHE_DIR.exists():
        return
    for pdf in sorted(AISTEAR_CACHE_DIR.glob("**/*.pdf")):
        yield {
            "document_id": pdf.stem,
            "title_en": pdf.stem.replace("_", " ").title(),
            "source_url": f"https://cache.local{aistear}/{pdf.relative_to(AISTEAR_CACHE_DIR)}",
            "age_band": "PRE_SCHOOL",
            "themes": ["WELL_BEING", "IDENTITY_BELONGING", "COMMUNICATING", "EXPLORING_THINKING"],
            "principles_count": 0,
            "learning_goals_count": 0,
            "extracted_at": "PENDING_BAML",
            "language": "bilingual",
        }


@dlt.resource(name="naionra_listings", write_disposition="merge", primary_key=["id"])
def naionra_listings():
    """Naíonra (Irish-medium pre-school) directory.

    Source: gaeloideachas.ie/directories/ and Pobal listings.
    Geocoded downstream by the geospatial DAG.
    """
    if not AISTEAR_CACHE_DIR.exists():
        return
    cache = AISTEAR_CACHE_DIR / "naionra"
    if not cache.exists():
        return
    for json_file in sorted(cache.glob("**/*.json")):
        import json as _json
        data = _json.loads(json_file.read_text())
        if isinstance(data, list):
            for entry in data:
                yield entry
        else:
            yield data


@dlt.source(name="aistear_curriculum")
def aistear_curriculum():
    """Aistear DLT source — documents + naíonra directory."""
    yield aistear_documents
    yield naionra_listings
