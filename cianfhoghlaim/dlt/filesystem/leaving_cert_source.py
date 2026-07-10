"""
Leaving Certificate 6-subject filesystem DLT source.

Ingests every PDF (and JPG for the scanned geography exam page) in
`cianfhoghlaim/leaving_certificate/{chemistry,computer_science,english,
gaeilge,geography,mathematics}/{en,ga}/` into 6 per-subject DuckLake tables:

  - lc_chemistry_papers,    lc_chemistry_syllabus,    lc_chemistry_marking
  - lc_computer_science_*,  lc_computer_science_marking
  - lc_english_*,           lc_english_marking        (english dir is
                                                       en-only at root,
                                                       similar to gaeilge)
  - lc_gaeilge_*,           lc_gaeilge_marking        (the gaeilge dir has
                                                       no en/ subdir; files
                                                       live at the root)
  - lc_geography_*,         lc_geography_marking
  - lc_mathematics_*,       lc_mathematics_marking

Each PDF is routed through the v4 `select_ocr_backend()` heuristic
(per cianfhoghlaim/meaisinfhoghlaim/models/registry.py):
  - Irish-language (gaeilge) → glm-4.6v-flash (MLX-preferred)
  - exam papers (LC###ALP/EV/IV.pdf) → qwen3-vl-8b (workhorse)
  - syllabi (SC###Syllabus or SC-Chemistry-Specification-*.pdf) →
    gemma-4-26B-A4B (M4 default)
  - marking schemes (SCSEC##_guideline_material_eng.pdf) →
    molmo2-8b (diagram-pointing specialist)
  - scanned JPG → docling-serve (DocTags layout fallback)
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

DEFAULT_LC_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_LC_ROOT",
        str(Path(__file__).resolve().parents[2] / "leaving_certificate"),
    )
)

# The 6 target subjects of the LC6-subject pipeline (added 2026-07-10:
# english, per openspec/changes/2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1)
LC6_SUBJECTS: tuple[str, ...] = (
    "chemistry",
    "computer_science",
    "english",
    "gaeilge",
    "geography",
    "mathematics",
)

# Maps each PDF kind (regex on filename) to the v4 registry model key
# that `select_ocr_backend()` would select. Used downstream by the
# Dagster layer-2 asset to pick the right model for VLM/OCR extraction.
LC_PDF_KIND_REGISTRY: dict[str, str] = {
    # LC###ALP###EV.pdf / LC###GLP###IV.pdf — exam papers
    r"^LC\d{3}[AG]LP\d{3,4}[EI]V\.pdf$": "qwen3-vl-8b",
    # LC002ALP200EV.pdf — LC English Annual Leaving Programme exam paper
    r"^LC002ALP\d{3}[EI]V\.pdf$": "qwen3-vl-8b",
    # SCSEC##_Syllabus_*.pdf / SC-Chemistry-Specification-*.pdf
    r"^SC.*[Ss]yllabus.*\.pdf$": "gemma-4-26B-A4B",
    r"^SC.*[Ss]pecification.*\.pdf$": "gemma-4-26B-A4B",
    # SC-English-Spec-ENG-INT*.pdf — LC English spec constitution
    r"^SC-English-Spec-ENG-INT.*\.pdf$": "gemma-4-26B-A4B",
    # Siollabais-Nuashonraithe-* — Irish syllabus
    r"^Siollabais.*\.pdf$": "gemma-4-26B-A4B",
    # SCSEC##_guideline_material_*.pdf — marking scheme guidelines
    r"^SCSEC\d+_guideline.*\.pdf$": "molmo2-8b",
    # LC-Computer-Science-specification-*.pdf / Geography-syllabus-*.pdf
    r"^LC-.*[Ss]pecification.*\.pdf$": "gemma-4-26B-A4B",
    # lc_irish_foundation / LC001ALP100IV — gaeilge exam papers
    r"^lc_irish_foundation.*\.pdf$": "glm-4.6v-flash",
    # Default fallback
    r".*\.pdf$": "qwen3-vl-8b",
}

# Per-language model override (used for Irish-language PDFs)
GAEILGE_MODEL_KEY = "glm-4.6v-flash"

# Supported image extensions (geography includes 1 JPG scanned exam page)
IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".tiff")


def _classify_pdf(pdf_path: Path, language: str) -> str:
    """Pick the v4 registry model key for a given PDF based on its name + language.

    Args:
        pdf_path: The PDF file.
        language: 'en' or 'ga'.

    Returns:
        A v4 registry model key (e.g. 'qwen3-vl-8b').
    """
    name = pdf_path.name
    # Irish-language PDFs always use the GLM (multilingual + fast)
    if language == "ga":
        return GAEILGE_MODEL_KEY
    # English PDFs: regex-based classification
    for pattern, model_key in LC_PDF_KIND_REGISTRY.items():
        if pattern != r".*\.pdf$" and __import__("re").match(pattern, name):
            return model_key
    # Fallback
    return "qwen3-vl-8b"


def _scan_subject(subject_dir: Path) -> Iterator[dict[str, Any]]:
    """Yield (file_path, language) tuples for one of the 6 LC subjects.

    Handles 2 asymmetries:
    - gaeilge: no en/ subdir; Irish files live at the root of `gaeilge/`.
    - english: en-only at root (no ga/ subdir) — mirrors the gaeilge pattern
      but with default language "en" since the LC English syllabus is
      taught and examined in English.
    """
    if not subject_dir.exists():
        logger.warning(f"lc_subject_dir_missing: {subject_dir}")
        return

    if subject_dir.name == "gaeilge":
        # Files at root (mostly GA; some EN-named may exist)
        for ext in (".pdf",) + IMAGE_EXTENSIONS:
            for f in subject_dir.glob(f"*{ext}"):
                yield {
                    "file_path": f,
                    "language": "ga",  # default for gaeilge root
                    "subject": "gaeilge",
                }
    elif subject_dir.name == "english":
        # Files at root (EN-only; the English LC syllabus is monolingual)
        for ext in (".pdf",) + IMAGE_EXTENSIONS:
            for f in subject_dir.glob(f"*{ext}"):
                yield {
                    "file_path": f,
                    "language": "en",  # default for english root
                    "subject": "english",
                }
    else:
        for lang in ("en", "ga"):
            lang_dir = subject_dir / lang
            if not lang_dir.exists():
                continue
            for ext in (".pdf",) + IMAGE_EXTENSIONS:
                for f in lang_dir.glob(f"*{ext}"):
                    yield {
                        "file_path": f,
                        "language": lang,
                        "subject": subject_dir.name,
                    }


def _row(record: dict[str, Any]) -> dict[str, Any]:
    """Build the DuckLake row for one PDF (or image) ingestion."""
    file_path: Path = record["file_path"]
    language: str = record["language"]
    subject: str = record["subject"]

    file_hash = ""
    try:
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    except OSError:
        # Some files may be unreadable (permissions / missing)
        pass

    is_image = file_path.suffix.lower() in IMAGE_EXTENSIONS
    return {
        "id": hashlib.sha256(
            f"{file_hash}:{file_path.name}:{language}".encode("utf-8")
        ).hexdigest()[:16],
        "file_hash": file_hash,
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        "is_image": is_image,
        "language": language,
        "subject": subject,
        # The v4 registry model key chosen for this file
        "model_key": _classify_pdf(file_path, language),
        # Classification by filename pattern
        "is_exam_paper": bool(
            __import__("re").match(r"^LC.*[AG]LP.*\.pdf$", file_path.name)
        ),
        "is_syllabus": bool(
            __import__("re").match(
                r"^(SCSEC.*Syllabus|SC-Chemistry-Specification|LC-.*[Ss]pecification|Siollabais).*\.pdf$",
                file_path.name,
            )
        ),
        "is_marking_scheme": bool(
            __import__("re").match(r"^SCSEC\d+_guideline.*\.pdf$", file_path.name)
        ),
    }


@dlt.resource(
    name="lc5_documents",
    write_disposition="replace",
    primary_key="id",
    columns={
        "id": {"data_type": "text"},
        "file_hash": {"data_type": "text"},
        "file_name": {"data_type": "text"},
        "file_path": {"data_type": "text"},
        "file_size_bytes": {"data_type": "bigint"},
        "is_image": {"data_type": "bool"},
        "language": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "model_key": {"data_type": "text"},
        "is_exam_paper": {"data_type": "bool"},
        "is_syllabus": {"data_type": "bool"},
        "is_marking_scheme": {"data_type": "bool"},
    },
)
def lc5_documents(
    root_path: str = str(DEFAULT_LC_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield one row per LC PDF (or image) across the 6 subjects × 2 languages.

    Default root: `cianfhoghlaim/leaving_certificate/`.
    Override via the `CIANFHOGHLAIM_LC_ROOT` env var.
    """
    root = Path(root_path)
    if not root.exists():
        logger.error(f"lc5_root_missing: {root}")
        return

    n = 0
    for subject in LC6_SUBJECTS:
        subject_dir = root / subject
        for record in _scan_subject(subject_dir):
            row = _row(record)
            yield row
            n += 1
    logger.info(f"lc5_ingested: {n} documents across {len(LC6_SUBJECTS)} subjects")


def main() -> int:
    """CLI entry — runs the pipeline against the local duckdb destination."""
    import duckdb
    con = duckdb.connect("lc5_ingest.duckdb")
    pipeline = dlt.pipeline(
        pipeline_name="lc5",
        destination=dlt.destinations.duckdb("lc5_ingest.duckdb"),
        dataset_name="curriculum_unified",
    )
    load_info = pipeline.run(lc5_documents())
    print(load_info)
    # Show the row count
    df = con.execute("SELECT subject, language, COUNT(*) FROM curriculum_unified.lc5_documents GROUP BY subject, language").df()
    print(df.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
