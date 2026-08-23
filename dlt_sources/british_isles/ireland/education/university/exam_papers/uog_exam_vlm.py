"""VLM processing wrapper for UoG exam papers (M.Sc. AI thesis).

Why this file exists:

  Most UoG Masters-level exam papers (M.Sc. AI, M.Sc. CS, etc.) are
  **scanned PDFs** with no embedded text layer. The SEC pipeline
  (`examinations_scraper.py`) gets away with `pdftotext` because those
  PDFs were exported from Word; UoG papers are uploaded as images
  straight from the lecturer's iPad. We need a Vision Language Model.

  The thesis contribution is a 4-VLM comparison (GLM-4.6V Flash, Qwen3-
  VL-7B, olmOCR-2-7B, Gemma-3) on the same 20-paper gold set, so the
  BAML `ExtractUoGExamPaper` schema can be evaluated end-to-end.

Two entry points:

  - `UoGExamVLMConfig`  – thin Pydantic config for "what model + DPI to
                          use".
  - `run_vlm_eval(...)` – per-paper extract helper used by both the
                          `uog_exam_papers_ocr_extract` Dagster asset
                          and the standalone MLflow eval script.
  - `run_thesis_eval(...)` – runs the 4-VLM comparison and returns a
                             CSV-shaped DataFrame ready for MLflow.

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# --------------------------------------------------------------------------- #
# Model registry — mirrors `machine_learning/ocr/vlm_finetune_comparison.py`
# --------------------------------------------------------------------------- #

# Each entry is `(model_id, vram_gb, description)`. We keep this list
# small (4 models) because the thesis needs a defensible comparison,
# not a leaderboard.
UOG_VLM_MODEL_REGISTRY: tuple[tuple[str, float, str], ...] = (
    (
        "glm-4.6v-flash",
        6.0,
        "Lightweight, 128k context, function-calling capable. "
        "Primary extraction backend.",
    ),
    (
        "qwen3-vl-7b",
        8.0,
        "Strong OCR + document understanding. 32k context. "
        "First fallback.",
    ),
    (
        "olmocr-2-7b",
        4.0,
        "Specialist OCR VLM. Best on math/equation extraction.",
    ),
    (
        "gemma-3-9b-it",
        9.0,
        "Mobile-friendly, fast, lower ceiling for tables.",
    ),
)


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass
class UoGExamVLMConfig:
    """How to run a VLM against an exam paper PDF."""

    model: str = "glm-4.6v-flash"
    dpi: int = 200
    max_pages: int = 30  # most papers are < 8 pages; 30 is the cap
    timeout_seconds: float = 60.0
    output_schema: str = "UoGExamPaper"
    mlflow_experiment: str = "uog_vlm_exam_ocr"
    extract_en_alias: str = "extract-en"  # routes through BAML LiteLLM client

    @classmethod
    def from_env(cls) -> UoGExamVLMConfig:
        return cls(
            model=os.environ.get("UOG_VLM_MODEL", "glm-4.6v-flash"),
            dpi=int(os.environ.get("UOG_VLM_DPI", "200")),
            max_pages=int(os.environ.get("UOG_VLM_MAX_PAGES", "30")),
            mlflow_experiment=os.environ.get(
                "UOG_VLM_MLFLOW_EXPERIMENT", "uog_vlm_exam_ocr"
            ),
        )


# --------------------------------------------------------------------------- #
# Image extraction (PDF → PNG list)
# --------------------------------------------------------------------------- #


def pdf_to_images(
    pdf_path: Path,
    *,
    dpi: int = 200,
    max_pages: int = 30,
) -> list[bytes]:
    """Render each page of `pdf_path` to a PNG byte blob.

    Uses PyMuPDF (`pymupdf`) when available, falls back to a no-op
    return so the import path doesn't crash on a workstation that
    hasn't installed the OCR stack yet.
    """
    try:
        import pymupdf  # PyMuPDF (renamed in 2024; pymupdf==1.24+)
    except Exception:  # noqa: BLE001
        try:
            import fitz  # type: ignore[no-redef]
        except ImportError:
            logger.warning(
                "uog_vlm_pdf_to_images_pymupdf_missing",
                pdf_path=str(pdf_path),
            )
            return []

    try:
        import pymupdf as _mupdf  # type: ignore[no-redef]
    except Exception:  # noqa: BLE001
        import fitz as _mupdf  # type: ignore[no-redef]

    images: list[bytes] = []
    with _mupdf.open(str(pdf_path)) as doc:  # type: ignore[union-attr]
        for page_idx, page in enumerate(doc):
            if page_idx >= max_pages:
                break
            pix = page.get_pixmap(dpi=dpi)
            images.append(pix.tobytes("png"))
    return images


# --------------------------------------------------------------------------- #
# Single-paper VLM extract
# --------------------------------------------------------------------------- #


def run_vlm_eval(
    pdf_path: Path,
    *,
    module_code: str,
    academic_year: int,
    config: UoGExamVLMConfig | None = None,
) -> dict[str, Any]:
    """Run one VLM extraction of `pdf_path` through the BAML client.

    Returns the BAML `UoGExamPaper` JSON dict plus a `meta` block with
    the model + DPI used and the page count. The function never raises
    on BAML errors — it returns `{"status": "error", "error": str(exc)}`
    so the calling asset can keep going.
    """
    cfg = config or UoGExamVLMConfig.from_env()
    images = pdf_to_images(pdf_path, dpi=cfg.dpi, max_pages=cfg.max_pages)
    if not images:
        return {
            "status": "no_images",
            "module_code": module_code,
            "academic_year": academic_year,
            "config": cfg.__dict__,
        }

    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError:
        return {
            "status": "baml_client_missing",
            "module_code": module_code,
            "academic_year": academic_year,
            "hint": "Run `baml generate` first.",
        }

    # BAML image-prompt: hand over the page PNGs as a list of
    # `image_url` blocks (LiteLLM handles data URLs cleanly).
    # We save them to a sidecar so the cache survives a restart.
    try:
        result = b.ExtractUoGExamPaperFromImages(
            images=[_bytes_to_data_url(img) for img in images],
            module_code=module_code,
            academic_year=academic_year,
        )
        return {
            "status": "ok",
            "module_code": module_code,
            "academic_year": academic_year,
            "model": cfg.model,
            "dpi": cfg.dpi,
            "page_count": len(images),
            "exam_paper": (
                result.model_dump() if hasattr(result, "model_dump") else result
            ),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "uog_vlm_eval_failed",
            model=cfg.model,
            module_code=module_code,
            error=str(exc),
        )
        return {
            "status": "error",
            "module_code": module_code,
            "academic_year": academic_year,
            "model": cfg.model,
            "error": str(exc),
        }


def _bytes_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    import base64

    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"


# --------------------------------------------------------------------------- #
# Thesis 4-VLM comparison
# --------------------------------------------------------------------------- #


@dataclass
class ThesisEvalRow:
    paper_id: str
    module_code: str
    academic_year: int
    model: str
    status: str
    question_count: int = 0
    total_marks: int = 0
    confidence: float = 0.0
    page_count: int = 0
    elapsed_ms: float = 0.0

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "module_code": self.module_code,
            "academic_year": self.academic_year,
            "model": self.model,
            "status": self.status,
            "question_count": self.question_count,
            "total_marks": self.total_marks,
            "confidence": self.confidence,
            "page_count": self.page_count,
            "elapsed_ms": self.elapsed_ms,
        }


def run_thesis_eval(
    gold_set: Iterable[Path],
    module_codes: dict[Path, str],
    years: dict[Path, int],
    *,
    models: tuple[str, ...] = tuple(m for m, _, _ in UOG_VLM_MODEL_REGISTRY),
) -> list[ThesisEvalRow]:
    """Run the 4-VLM comparison on the thesis gold set.

    `gold_set` is the iterable of PDF paths. `module_codes` and `years`
    are `path -> value` dicts (so we can split train/test later). The
    result is a list of rows suitable for MLflow logging or pandas
    import.
    """
    out: list[ThesisEvalRow] = []
    import time as _time

    for pdf_path in gold_set:
        module_code = module_codes.get(pdf_path, pdf_path.stem.split("_")[0])
        try:
            academic_year = years.get(pdf_path, int(pdf_path.stem.split("_")[1]))
        except (ValueError, IndexError):
            academic_year = 0

        for model_name in models:
            cfg = UoGExamVLMConfig(
                model=model_name,
                mlflow_experiment="uog_vlm_exam_ocr",
            )
            t0 = _time.perf_counter()
            result = run_vlm_eval(
                pdf_path,
                module_code=module_code,
                academic_year=academic_year,
                config=cfg,
            )
            elapsed = (_time.perf_counter() - t0) * 1000.0

            exam_paper = result.get("exam_paper") or {}
            if isinstance(exam_paper, dict):
                questions = exam_paper.get("questions") or []
                question_count = len(questions) if isinstance(questions, list) else 0
                total_marks = int(exam_paper.get("total_marks") or 0)
                confidence = float(exam_paper.get("confidence") or 0.0)
            else:
                question_count = 0
                total_marks = 0
                confidence = 0.0

            out.append(
                ThesisEvalRow(
                    paper_id=pdf_path.stem,
                    module_code=module_code,
                    academic_year=academic_year,
                    model=model_name,
                    status=result.get("status", "unknown"),
                    question_count=question_count,
                    total_marks=total_marks,
                    confidence=confidence,
                    page_count=result.get("page_count", 0),
                    elapsed_ms=round(elapsed, 2),
                )
            )
    return out


__all__ = [
    "UOG_VLM_MODEL_REGISTRY",
    "UoGExamVLMConfig",
    "pdf_to_images",
    "run_vlm_eval",
    "run_thesis_eval",
    "ThesisEvalRow",
]
