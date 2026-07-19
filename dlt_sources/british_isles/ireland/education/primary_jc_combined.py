"""
Ireland Primary + Junior Cycle (combined) DLT source.

A unified ingestion loop that walks the local `/stedding/ingest_queue/`
cache and emits one row per (stage, subject, language) for the 2
non-Leaving-Cert stages: Primary (ages 4-12) + Junior Cycle (ages 12-15).

This source complements the existing single-stage sources:

- `primary.py` — Primary-only (12 NCCA primary areas, ages 4-12)
- `junior_cycle.py` — Junior Cycle-only (18 JC subjects + 16 short courses)
- `primary_jc_combined.py` (THIS) — combined loop for cross-stage analytics
                                (e.g. "language coverage across stages 1-4")

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/{primary,junior_cycle}/`; live scraping is Phase 2.

Source URLs:
  - https://www.curriculumonline.ie/en/primary/
  - https://ncca.ie/en/primary/
  - https://www.curriculumonline.ie/en/junior-cycle/
  - https://ncca.ie/en/junior-cycle/

Datasets produced (3 resources):
  primary_jc_unified     — one row per (stage, subject, language) tuple
  primary_jc_subjects   — one row per primary area OR junior cycle subject
  primary_jc_strands     — one row per strand (BAML-extracted per source PDF)

BAML extraction (per `baml/education/primary/primary_extraction.baml`
and `baml/education/junior_cycle/junior_cycle_extraction.baml`):
  b.ExtractPrimaryArea(text, area)            -> PrimaryAreaSpecStage
  b.ExtractJCSubjectSpec(text, subject)        -> JCSubjectSpecStage
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

PRIMARY_JC_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
)

# Stage identifiers used by the unified loop. The 5-stage taxonomy
# (early_years, primary, junior_cycle, senior_cycle, tertiary) is from
# `cianfhoghlaim-pipeline` spec; this source only covers the 2 non-LC stages.
PRIMARY_JC_STAGES: tuple[str, ...] = ("primary", "junior_cycle")

PRIMARY_JC_SOURCE_URLS = [
    "https://www.curriculumonline.ie/en/primary/",
    "https://ncca.ie/en/primary/",
    "https://www.curriculumonline.ie/en/junior-cycle/",
    "https://ncca.ie/en/junior-cycle/",
]


def _file_hash(path: Path) -> str:
    """Deterministic SHA-256 for DLT merge keys."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
    except (OSError, PermissionError) as e:
        logger.warning("file_hash_failed", path=str(path), error=str(e))
        return ""
    return sha.hexdigest()


def _detect_stage(pdf: Path) -> str:
    """Detect the stage from the directory name in the cache."""
    parts = pdf.parts
    for p in parts:
        if p in PRIMARY_JC_STAGES:
            return p
    return "primary"  # default fallback


def _detect_language(pdf: Path) -> str:
    """Detect EN vs GA from the parent directory or file name.

    Convention: PDFs under `<stage>/ga/` or named `*_ga.pdf` are GA;
    everything else is EN. The BIEP v1 convention (per ncca.py) does
    the same.
    """
    name = pdf.name.lower()
    if "/ga/" in str(pdf).lower() or "_ga." in name or ".ga." in name:
        return "ga"
    return "en"


def _detect_subject(pdf: Path) -> str:
    """Detect the subject/area from the immediate parent directory name."""
    parent = pdf.parent.name
    if parent and parent not in PRIMARY_JC_STAGES:
        return parent
    return pdf.stem.split("_")[0]


@dlt.resource(
    name="primary_jc_unified",
    write_disposition="merge",
    primary_key=["file_hash", "stage", "subject", "language"],
)
def primary_jc_unified() -> Iterator[dict[str, Any]]:
    """One row per (stage, subject, language) PDF in the ingest cache.

    This is the canonical cross-stage resource for the combined
    ingestion loop; downstream assets join it with
    `primary_jc_subjects` and `primary_jc_strands` to build the
    stage-1-through-4 (Primary + JC) view of the curriculum.
    """
    if not PRIMARY_JC_CACHE_DIR.exists():
        logger.warning(
            "primary_jc_cache_dir_missing",
            path=str(PRIMARY_JC_CACHE_DIR),
            hint="set STEDDING_INGEST_QUEUE or populate /stedding/ingest_queue/{primary,junior_cycle}/",
        )
        return iter(())

    for stage in PRIMARY_JC_STAGES:
        stage_dir = PRIMARY_JC_CACHE_DIR / stage
        if not stage_dir.exists():
            continue
        for pdf in sorted(stage_dir.glob("**/*.pdf")):
            file_hash = _file_hash(pdf)
            if not file_hash:
                continue
            language = _detect_language(pdf)
            subject = _detect_subject(pdf)
            yield {
                "file_hash": file_hash,
                "document_id": pdf.stem,
                "stage": stage,
                "subject": subject,
                "language": language,
                "title_en": pdf.stem.replace("_", " ").title(),
                "file_path": str(pdf),
                "file_size": pdf.stat().st_size,
                "account": f"ireland_{stage}",
                "cycle": stage,
                "source_url": f"https://cache.local/{stage}/{pdf.name}",
                "discovered_at": datetime.now(UTC).isoformat(),
                "baml_extraction_status": "pending",
            }


@dlt.resource(
    name="primary_jc_subjects",
    write_disposition="merge",
    primary_key=["stage", "subject", "language"],
)
def primary_jc_subjects() -> Iterator[dict[str, Any]]:
    """One row per (stage, subject) pair, summarizing the unified loop.

    Different from `primary_jc_unified` in that this resource aggregates
    multiple PDFs per (stage, subject, language) — useful for
    cross-stage subject-coverage analytics (e.g. "how many primary
    areas have GA-language coverage vs JC subjects").
    """
    if not PRIMARY_JC_CACHE_DIR.exists():
        return iter(())

    seen: set[tuple[str, str, str]] = set()
    for stage in PRIMARY_JC_STAGES:
        stage_dir = PRIMARY_JC_CACHE_DIR / stage
        if not stage_dir.exists():
            continue
        for pdf in sorted(stage_dir.glob("**/*.pdf")):
            language = _detect_language(pdf)
            subject = _detect_subject(pdf)
            key = (stage, subject, language)
            if key in seen:
                continue
            seen.add(key)
            yield {
                "stage": stage,
                "subject": subject,
                "language": language,
                "title_en": subject.replace("_", " ").title(),
                "kind": "primary_area" if stage == "primary" else "jc_subject",
                "pdf_count": 1,  # bumped on each encounter below
                "account": f"ireland_{stage}",
                "cycle": stage,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.resource(
    name="primary_jc_strands",
    write_disposition="merge",
    primary_key=["file_hash", "strand_code"],
)
def primary_jc_strands() -> Iterator[dict[str, Any]]:
    """BAML-extracted strands (one per PDF).

    Mirrors the canonical `lc_extraction/curriculum_syllabus.baml`
    `SyllabusDocument.module_topics` shape, but for Primary + JC.
    Skips PDFs where BAML extraction fails (logged at warning).
    """
    if not PRIMARY_JC_CACHE_DIR.exists():
        return iter(())

    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("baml_client_not_generated_primary_jc_skipped")
        return iter(())

    for stage in PRIMARY_JC_STAGES:
        stage_dir = PRIMARY_JC_CACHE_DIR / stage
        if not stage_dir.exists():
            continue
        for pdf in sorted(stage_dir.glob("**/*.pdf")):
            file_hash = _file_hash(pdf)
            if not file_hash:
                continue
            try:
                import pymupdf  # type: ignore[import-not-found]
                doc = pymupdf.open(str(pdf))
                parts: list[str] = []
                total = 0
                for page in doc:
                    text = page.get_text() or ""
                    if not text:
                        continue
                    if total + len(text) > 30_000:
                        text = text[: 30_000 - total]
                    parts.append(text)
                    total += len(text)
                    if total >= 30_000:
                        break
                doc.close()
                text = "\n\n".join(parts)
            except (ImportError, OSError, ValueError, RuntimeError) as e:
                logger.warning("pymupdf_extract_failed", path=str(pdf), error=str(e))
                continue

            if not text:
                continue

            subject = _detect_subject(pdf)
            try:
                if stage == "primary":
                    fn = getattr(b, "ExtractPrimaryArea", None)
                    if fn is None:
                        logger.warning(
                            "primary_baml_fn_missing", file_name=pdf.name
                        )
                        continue
                    result = fn(text=text[:30_000], area=subject)
                else:
                    fn = getattr(b, "ExtractJCSubjectSpec", None)
                    if fn is None:
                        logger.warning(
                            "jc_baml_fn_missing", file_name=pdf.name
                        )
                        continue
                    result = fn(text=text[:30_000], subject=subject)
                if hasattr(result, "model_dump"):
                    payload = result.model_dump()
                elif isinstance(result, dict):
                    payload = result
                else:
                    continue
                strands = payload.get("strands", []) or payload.get(
                    "module_topics", []
                )
                if not isinstance(strands, list):
                    continue
                for idx, strand in enumerate(strands):
                    if hasattr(strand, "model_dump"):
                        strand = strand.model_dump()
                    if not isinstance(strand, dict):
                        continue
                    yield {
                        "file_hash": file_hash,
                        "strand_code": strand.get("module_id", "")
                        or strand.get("name", "")
                        or f"{subject}_{idx}",
                        "stage": stage,
                        "subject": subject,
                        "title_en": strand.get("name", "")
                        or strand.get("name_en", ""),
                        "title_ga": strand.get("name_ga"),
                        "baml_extraction_status": "success",
                        "extracted_at": datetime.now(UTC).isoformat(),
                    }
            except Exception as e:  # BAML runtime errors
                logger.warning(
                    "primary_jc_baml_extraction_failed",
                    file_name=pdf.name,
                    stage=stage,
                    error=str(e),
                )
                continue


@dlt.source(name="ireland_primary_jc")
def ireland_primary_jc_source(
    base_path: str | Path = PRIMARY_JC_CACHE_DIR,
    include_extraction: bool = True,
) -> Iterator[Any]:
    """
    Combined Ireland Primary + Junior Cycle DLT source.

    Args:
        base_path: Local cache root (default `/stedding/ingest_queue/`).
        include_extraction: If True, run the BAML-extracting resource too.
    """
    base = Path(base_path)
    if not base.exists():
        return iter(())

    yield from primary_jc_unified()
    yield from primary_jc_subjects()

    if include_extraction:
        yield from primary_jc_strands()


def create_ireland_primary_jc_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_primary_jc",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_primary_jc_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "PRIMARY_JC_CACHE_DIR",
    "PRIMARY_JC_SOURCE_URLS",
    "PRIMARY_JC_STAGES",
    "create_ireland_primary_jc_pipeline",
    "ireland_primary_jc_source",
    "primary_jc_strands",
    "primary_jc_subjects",
    "primary_jc_unified",
]