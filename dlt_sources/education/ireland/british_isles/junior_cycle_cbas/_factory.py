"""Factory for the 36 JC CBA (Classroom-Based Assessment) DLT sources (BIEP v2).

The 18 NCCA JC subjects each have 2 CBAs (one for Year 2, one for Year 3)
= 36 CBAs total. Each CBA has its own DLT source keyed by `cba_id`.

The destination DuckLake namespace is:
    cianfhoghlaim.education.british_isles.ireland.junior_cycle.cbas.<subject>.<cba_id>

Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
"""
from __future__ import annotations
import dlt


import hashlib
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import dlt_sources
import structlog

from dlt_sources.education.ireland.british_isles.education._pdf_text import (
    extract_pdf_text,
)

logger = structlog.get_logger(__name__)

JC_SUBJECTS: tuple[str, ...] = (
    "english",
    "gaeilge",
    "mathematics",
    "irish_history",
    "geography",
    "science",
    "business_studies",
    "french",
    "german",
    "spanish",
    "italian",
    "home_economics",
    "music",
    "art",
    "technology",
    "engineering",
    "graphics",
    "wood_technology",
)

# Each subject has 2 CBAs - one for Year 2 and one for Year 3
JC_CBAS_PER_SUBJECT: int = 2

JC_CBA_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "junior_cycle" / "cbas"


def list_jc_cba_ids() -> list[str]:
    """Return the canonical list of 36 JC CBA IDs (subject_1, subject_2, ...)."""
    return [
        f"{subject}_{cba_idx + 1}"
        for subject in JC_SUBJECTS
        for cba_idx in range(JC_CBAS_PER_SUBJECT)
    ]


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


# The shared `extract_pdf_text` helper handles both the real pymupdf extraction
# and the legacy stub fallback. See
# dlt_sources.education.ireland.british_isles.education._pdf_text


def build_jc_cba_source(cba_id: str, cache_dir: Path | None = None):
    """Build a DLT source for one NCCA JC CBA descriptor.

    Parameters
    ----------
    cba_id : str
        One of the 36 CBA IDs (e.g. "english_1", "english_2", "gaeilge_1", ...).
    cache_dir : Path | None
        Override the default cache dir.

    Returns
    -------
    dlt.Source
        A DLT source with 1 resource:
        - `jc_cba_<cba_id>_descriptors` — per-PDF CBA descriptor rows
    """
    subject, cba_idx_str = cba_id.rsplit("_", 1)
    if subject not in JC_SUBJECTS:
        raise ValueError(
            f"Unknown CBA subject '{subject}'. Must be one of {JC_SUBJECTS}."
        )
    cba_idx = int(cba_idx_str)
    if cba_idx < 1 or cba_idx > JC_CBAS_PER_SUBJECT:
        raise ValueError(
            f"CBA index must be 1 or {JC_CBAS_PER_SUBJECT} (got {cba_idx})."
        )

    effective_cache_dir = (
        cache_dir
        if cache_dir is not None
        else JC_CBA_CACHE_ROOT / subject
    )
    source_id = f"british_isles.ireland.education.jc_cba_{cba_id}"

    @dlt.resource(
        name=f"jc_cba_{cba_id}_descriptors",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def jc_cba_descriptors():
        if not effective_cache_dir.exists():
            logger.warning(
                "jc_cba_cache_dir_missing",
                subject=subject,
                cba_id=cba_id,
                path=str(effective_cache_dir),
            )
            return

        # Each subject has 2 CBA PDFs (one per year) - filter by index in filename.
        cba_pdf_pattern = f"cba_{cba_idx}_*.pdf"
        for pdf_path in sorted(effective_cache_dir.glob(cba_pdf_pattern)):
            content_hash = _file_hash(pdf_path)
            m = re.search(r"(20\d{2}|19\d{2})", pdf_path.name)
            spec_year = int(m.group(1)) if m else None
            yield {
                "source_id": source_id,
                "subject": subject,
                "cba_id": cba_id,
                "cba_idx": cba_idx,
                "language": "en",
                "filename": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_bytes": pdf_path.stat().st_size,
                "content_hash": content_hash,
                "pdf_text": extract_pdf_text(pdf_path),
                "specification_year": spec_year,
                "ingested_at": datetime.now(UTC).isoformat(),
                "country_code": "ireland",
                "jurisdiction": "ireland",
                "education_stage": "junior_cycle_cba",
                "year_band": "YEAR_2" if cba_idx == 1 else "YEAR_3",
                "namespace": (
                    "cianfhoghlaim.education.british_isles.ireland.junior_cycle."
                    f"cbas.{subject}.{cba_id}"
                ),
            }

    return jc_cba_descriptors


# Generate the 36 per-CBA DLT source factories at import time.
__all__: list[str] = []
for _cba_id in list_jc_cba_ids():
    _name = f"{_cba_id.replace(' ', '_')}_source"

    def _make(cid: str = _cba_id):
        return build_jc_cba_source(cid)

    globals()[_name] = _make
    __all__.append(_name)


# Also expose the canonical list of 36 CBA IDs.
JC_CBA_IDS = list_jc_cba_ids()
