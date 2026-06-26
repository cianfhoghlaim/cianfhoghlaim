"""
Ireland Primary Curriculum DLT source.

Reads the 12 NCCA primary curriculum specifications (one per curriculum
area) from the local scrape cache. Each specification is a PDF that
yields `PrimaryCurriculumArea[]`, `PrimaryStrand[]`, and
`PrimaryLearningOutcome[]` rows after BAML extraction.

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/primary/` cache; live scraping is Phase 2.

Source URLs:
  - https://www.curriculumonline.ie/en/primary/
  - https://ncca.ie/en/primary/
  - https://www.gov.ie/en/department-of-education/topics/primary/

Datasets produced (4 resources):
  primary_specifications        — NCCA primary curriculum specification PDFs
  primary_curriculum_areas      — PrimaryCurriculumArea[] (BAML-extracted)
  primary_strands               — PrimaryStrand[] (BAML-extracted)
  primary_learning_outcomes     — PrimaryLearningOutcome[] (BAML-extracted)

BAML extraction (per `baml_src/primary.baml`):
  b.ExtractPrimaryFramework(text)         -> PrimaryCurriculumArea[]
  b.ExtractPrimaryLearningOutcomes(text)  -> PrimaryLearningOutcome[]
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

PRIMARY_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "primary"

PRIMARY_SOURCE_URLS = [
    "https://www.curriculumonline.ie/en/primary/",
    "https://ncca.ie/en/primary/",
    "https://www.gov.ie/en/department-of-education/topics/primary/",
]

# 12 NCCA primary curriculum areas.
PRIMARY_AREAS: list[str] = [
    "english",
    "gaeilge",
    "mathematics",
    "social_environmental_education",  # SESE
    "science",
    "geography",
    "history",
    "arts_education",
    "music",
    "drama",
    "physical_education",
    "social_personal_health_education",  # SPHE
]


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _extract_text_from_pdf(path: Path, max_chars: int = 50_000) -> str:
    """Best-effort text extraction via pymupdf."""
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
    function_name: str = "ExtractPrimaryFramework",
) -> dict[str, Any]:
    """Invoke the BAML primary extract function. Graceful degradation."""
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("baml_client_not_generated_primary_extraction_skipped")
        return {"status": "skipped_no_client", "result": None}

    try:
        if function_name == "ExtractPrimaryFramework":
            result = b.ExtractPrimaryFramework(text=text[:30_000], file_name=file_name)
        elif function_name == "ExtractPrimaryLearningOutcomes":
            result = b.ExtractPrimaryLearningOutcomes(text=text[:30_000], file_name=file_name)
        else:
            return {"status": "skipped_unknown_function", "result": None}
        if hasattr(result, "model_dump"):
            return {"status": "success", "result": result.model_dump()}
        return {"status": "success", "result": result}
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "primary_baml_extraction_failed",
            file_name=file_name,
            function=function_name,
            error=str(e),
        )
        return {"status": "error", "error": str(e)}


@dlt.resource(
    name="primary_specifications",
    write_disposition="merge",
    primary_key=["file_hash", "document_id"],
)
def primary_specifications() -> Any:
    """One row per primary curriculum specification PDF."""
    if not PRIMARY_CACHE_DIR.exists():
        return
    for pdf in sorted(PRIMARY_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        rel = pdf.relative_to(PRIMARY_CACHE_DIR)
        # Derive curriculum area from the directory name (e.g. "english/", "mathematics/").
        parts = rel.parts
        area = parts[0] if len(parts) > 1 else pdf.stem
        yield {
            "file_hash": file_hash,
            "document_id": pdf.stem,
            "title_en": pdf.stem.replace("_", " ").title(),
            "curriculum_area": area,
            "file_path": str(pdf),
            "file_size": pdf.stat().st_size,
            "account": "ireland_primary",
            "cycle": "primary",
            "source_url": f"https://cache.local/primary/{rel}",
            "discovered_at": datetime.now(UTC).isoformat(),
            "baml_extraction_status": "pending",
        }


@dlt.resource(
    name="primary_curriculum_areas",
    write_disposition="merge",
    primary_key=["file_hash", "area_code"],
)
def primary_curriculum_areas() -> Any:
    """BAML-extracted `PrimaryCurriculumArea[]` rows."""
    if not PRIMARY_CACHE_DIR.exists():
        return
    for pdf in sorted(PRIMARY_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        text = _extract_text_from_pdf(pdf)
        if not text:
            continue
        result = _baml_extract(text, pdf.name, "ExtractPrimaryFramework")
        if result["status"] != "success" or not result["result"]:
            continue
        # The BAML function returns a list of PrimaryCurriculumArea.
        items = result["result"]
        if isinstance(items, list):
            for idx, item in enumerate(items):
                if hasattr(item, "model_dump"):
                    item = item.model_dump()
                if not isinstance(item, dict):
                    continue
                yield {
                    "file_hash": file_hash,
                    "area_code": item.get("code", pdf.stem) + f"_{idx}",
                    "title_en": item.get("title", pdf.stem),
                    "stages": item.get("stages", []),
                    "strands_count": len(item.get("strands", [])) if isinstance(item.get("strands"), list) else 0,
                    "extracted_at": datetime.now(UTC).isoformat(),
                }
        elif isinstance(items, dict):
            # Single PrimaryCurriculumArea returned.
            if hasattr(items, "model_dump"):
                items = items.model_dump()
            yield {
                "file_hash": file_hash,
                "area_code": items.get("code", pdf.stem),
                "title_en": items.get("title", pdf.stem),
                "stages": items.get("stages", []),
                "strands_count": len(items.get("strands", [])) if isinstance(items.get("strands"), list) else 0,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.resource(
    name="primary_strands",
    write_disposition="merge",
    primary_key=["file_hash", "strand_code"],
)
def primary_strands() -> Any:
    """BAML-extracted `PrimaryStrand[]` rows (nested under areas)."""
    if not PRIMARY_CACHE_DIR.exists():
        return
    for pdf in sorted(PRIMARY_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        text = _extract_text_from_pdf(pdf)
        if not text:
            continue
        result = _baml_extract(text, pdf.name, "ExtractPrimaryFramework")
        if result["status"] != "success" or not result["result"]:
            continue
        items = result["result"]
        if not isinstance(items, list):
            items = [items]
        for area in items:
            if hasattr(area, "model_dump"):
                area = area.model_dump()
            if not isinstance(area, dict):
                continue
            area_code = area.get("code", pdf.stem)
            strands = area.get("strands", [])
            if not isinstance(strands, list):
                continue
            for strand in strands:
                if hasattr(strand, "model_dump"):
                    strand = strand.model_dump()
                if not isinstance(strand, dict):
                    continue
                yield {
                    "file_hash": file_hash,
                    "strand_code": strand.get("code", "unknown"),
                    "area_code": area_code,
                    "title_en": strand.get("title", ""),
                    "extracted_at": datetime.now(UTC).isoformat(),
                }


@dlt.resource(
    name="primary_learning_outcomes",
    write_disposition="merge",
    primary_key=["file_hash", "outcome_id"],
)
def primary_learning_outcomes() -> Any:
    """BAML-extracted `PrimaryLearningOutcome[]` rows."""
    if not PRIMARY_CACHE_DIR.exists():
        return
    for pdf in sorted(PRIMARY_CACHE_DIR.glob("**/*.pdf")):
        try:
            file_hash = _file_hash(pdf)
        except (OSError, PermissionError):
            continue
        text = _extract_text_from_pdf(pdf)
        if not text:
            continue
        result = _baml_extract(text, pdf.name, "ExtractPrimaryLearningOutcomes")
        if result["status"] != "success" or not result["result"]:
            continue
        items = result["result"]
        if not isinstance(items, list):
            items = [items]
        for idx, outcome in enumerate(items):
            if hasattr(outcome, "model_dump"):
                outcome = outcome.model_dump()
            if not isinstance(outcome, dict):
                continue
            yield {
                "file_hash": file_hash,
                "outcome_id": outcome.get("id", pdf.stem) + f"_{idx}",
                "text": outcome.get("text", ""),
                "stage": outcome.get("stage", ""),
                "strand": outcome.get("strand", ""),
                "element": outcome.get("element", ""),
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ireland_primary")
def ireland_primary_source(
    base_path: str | Path = PRIMARY_CACHE_DIR,
    max_files: int | None = None,
    include_extraction: bool = True,
):
    """
    Ireland primary curriculum dlt source.

    Args:
        base_path: Local cache directory (default `/stedding/ingest_queue/primary/`).
        max_files: Cap on rows (testing).
        include_extraction: If True, run the BAML-extracting resources too.
    """
    if not Path(base_path).exists():
        return iter(())

    yield from primary_specifications()

    if include_extraction:
        yield from primary_curriculum_areas()
        yield from primary_strands()
        yield from primary_learning_outcomes()


def create_ireland_primary_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_primary",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_primary_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "PRIMARY_CACHE_DIR",
    "PRIMARY_SOURCE_URLS",
    "PRIMARY_AREAS",
    "ireland_primary_source",
    "create_ireland_primary_pipeline",
    "primary_specifications",
    "primary_curriculum_areas",
    "primary_strands",
    "primary_learning_outcomes",
]
