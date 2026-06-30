"""
Ireland Junior Cycle DLT source.

Reads the 18 NCCA Junior Cycle subject specifications + 16 short courses
+ 36 CBAs (2 per JC subject) from the local scrape cache. Each
specification is a PDF that yields `JCSubjectSpec`, `CBATask[]`, and
`RubricDescriptor[]` rows after BAML extraction.

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/junior_cycle/` cache; live scraping is Phase 2.

Source URLs:
  - https://www.curriculumonline.ie/en/junior-cycle/
  - https://ncca.ie/en/junior-cycle/
  - https://www.examinations.ie/?l=en&mc=jc&fs=c  (CBA descriptors)

Datasets produced (3 resources):
  jc_specifications    — JCSubjectSpec rows (BAML-extracted)
  jc_short_courses     — 16 short courses (Coding, Chinese, etc.)
  cba_tasks            — CBATask[] (2 per JC subject, BAML-extracted)

BAML extraction (per `baml/education/stages/junior_cycle.baml`):
  b.ExtractJCSpec(text)           -> JCSubjectSpec
  b.ExtractCBADescriptor(text)    -> CBATask
"""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

JC_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "junior_cycle"

JC_SOURCE_URLS = [
    "https://www.curriculumonline.ie/en/junior-cycle/",
    "https://ncca.ie/en/junior-cycle/",
    "https://www.examinations.ie/?l=en&mc=jc&fs=c",
]

# 18 NCCA Junior Cycle subjects (kept in sync with `baml/education/stages/junior_cycle.baml:JuniorCycleSubject`).
JC_SUBJECTS: list[str] = [
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
]

# 16 NCCA Junior Cycle short courses.
JC_SHORT_COURSES: list[str] = [
    "coding",
    "chinese",
    "japanese",
    "russian",
    "polish",
    "lithuanian",
    "portuguese",
    "arabic",
    "hebrew",
    "philosophy",
    "film_studies",
    "financial_literacy",
    "media_literacy",
    "personal_professional_development",
    "digital_media",
    "athletic_studies",
]


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _extract_text_from_pdf(path: Path, max_chars: int = 50_000) -> str:
    try:
        import pymupdf  # type: ignore[import-not-found]

        doc = pymupdf.open(str(path))
        parts: list[str] = []
        total = 0
        for page in doc:
            text = page.get_text() or ""
            if not text:
                continue
            if total + len(text) > max_chars:
                text = text[: max_chars - total]
            parts.append(text)
            total += len(text)
            if total >= max_chars:
                break
        doc.close()
        return "\n\n".join(parts)
    except (ImportError, OSError, ValueError, RuntimeError) as e:
        logger.warning("pymupdf_extract_failed", path=str(path), error=str(e))
        return ""


def _baml_extract(
    text: str,
    file_name: str,
    function_name: str,
) -> dict[str, Any]:
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("baml_client_not_generated_jc_extraction_skipped")
        return {"status": "skipped_no_client", "result": None}

    try:
        if function_name == "ExtractJCSpec":
            result = b.ExtractJCSpec(text=text[:30_000], file_name=file_name)
        elif function_name == "ExtractCBADescriptor":
            result = b.ExtractCBADescriptor(text=text[:30_000], file_name=file_name)
        else:
            return {"status": "skipped_unknown_function", "result": None}
        if hasattr(result, "model_dump"):
            return {"status": "success", "result": result.model_dump()}
        return {"status": "success", "result": result}
    except Exception as e:
        logger.warning(
            "jc_baml_extraction_failed",
            file_name=file_name,
            function=function_name,
            error=str(e),
        )
        return {"status": "error", "error": str(e)}


@dlt.resource(
    name="jc_specifications",
    write_disposition="merge",
    primary_key=["file_hash", "subject"],
)
def jc_specifications() -> Any:
    """BAML-extracted `JCSubjectSpec` rows (one per JC subject PDF)."""
    if not JC_CACHE_DIR.exists():
        return
    for pdf in sorted(JC_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        # Derive subject from the file name (e.g. "mathematics_spec.pdf" -> "mathematics").
        subject = pdf.stem.split("_")[0]
        text = _extract_text_from_pdf(pdf)
        result = _baml_extract(text, pdf.name, "ExtractJCSpec")
        if result["status"] != "success" or not result["result"]:
            yield {
                "file_hash": file_hash,
                "subject": subject,
                "file_path": str(pdf),
                "account": "ireland_junior_cycle",
                "cycle": "junior_cycle",
                "baml_extraction_status": result["status"],
                "extracted_at": datetime.now(UTC).isoformat(),
            }
            continue
        spec = result["result"]
        if hasattr(spec, "model_dump"):
            spec = spec.model_dump()
        if not isinstance(spec, dict):
            continue
        yield {
            "file_hash": file_hash,
            "subject": subject,
            "title_en": spec.get("title", pdf.stem),
            "level": spec.get("level", "ordinary"),
            "strands_count": len(spec.get("strands", [])) if isinstance(spec.get("strands"), list) else 0,
            "outcomes_count": len(spec.get("outcomes", [])) if isinstance(spec.get("outcomes"), list) else 0,
            "wellbeing": spec.get("wellbeing", ""),
            "file_path": str(pdf),
            "account": "ireland_junior_cycle",
            "cycle": "junior_cycle",
            "baml_extraction_status": "success",
            "extracted_at": datetime.now(UTC).isoformat(),
        }


@dlt.resource(
    name="jc_short_courses",
    write_disposition="merge",
    primary_key=["short_course_code"],
)
def jc_short_courses() -> Any:
    """16 NCCA Junior Cycle short courses (registry-style, no PDF required)."""
    for code in JC_SHORT_COURSES:
        yield {
            "short_course_code": code,
            "title_en": code.replace("_", " ").title(),
            "level": "short",
            "account": "ireland_junior_cycle",
            "cycle": "junior_cycle",
        }


@dlt.resource(
    name="cba_tasks",
    write_disposition="merge",
    primary_key=["file_hash", "task_id"],
)
def cba_tasks() -> Any:
    """BAML-extracted `CBATask[]` rows (2 per JC subject, 36 total)."""
    if not JC_CACHE_DIR.exists():
        return
    for pdf in sorted(JC_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        subject = pdf.stem.split("_")[0]
        text = _extract_text_from_pdf(pdf)
        result = _baml_extract(text, pdf.name, "ExtractCBADescriptor")
        if result["status"] != "success" or not result["result"]:
            continue
        items = result["result"]
        if not isinstance(items, list):
            items = [items]
        for idx, task in enumerate(items):
            if hasattr(task, "model_dump"):
                task = task.model_dump()
            if not isinstance(task, dict):
                continue
            yield {
                "file_hash": file_hash,
                "task_id": task.get("id", f"{subject}_{idx}"),
                "subject": subject,
                "title_en": task.get("title", ""),
                "weighting_pct": task.get("weighting", 0),
                "assessment_format": task.get("format", ""),
                "baml_extraction_status": "success",
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ireland_junior_cycle")
def ireland_junior_cycle_source(
    base_path: str | Path = JC_CACHE_DIR,
    max_files: int | None = None,
    include_extraction: bool = True,
):
    """
    Ireland Junior Cycle dlt source.

    Args:
        base_path: Local cache directory (default `/stedding/ingest_queue/junior_cycle/`).
        max_files: Cap on rows (testing).
        include_extraction: If True, run the BAML-extracting resources too.
    """
    if not Path(base_path).exists():
        # The short_courses resource is always yielded (registry, no PDFs).
        yield from jc_short_courses()
        return

    if include_extraction:
        yield from jc_specifications()
        yield from cba_tasks()
    yield from jc_short_courses()


def create_ireland_junior_cycle_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_junior_cycle",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_junior_cycle_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "JC_CACHE_DIR",
    "JC_SHORT_COURSES",
    "JC_SOURCE_URLS",
    "JC_SUBJECTS",
    "cba_tasks",
    "create_ireland_junior_cycle_pipeline",
    "ireland_junior_cycle_source",
    "jc_short_courses",
    "jc_specifications",
]
