"""Scanned-PDF detection for the Cianfhoghlaim OCR fanout layer.

Per the 2026-08-10-ocr-vision-activation-v1 openspec change.

This module provides:
- `ScannedPDFReport` — the dataclass returned by `is_scanned_pdf()`
- `is_scanned_pdf(path)` — the canonical entry point for detecting
  image-only PDFs that need OCR vs text-layer PDFs that don't

Detection rules (per spec):
- `is_scanned = (total_text_chars < 50) OR (blank_pages / total_pages > 0.8)`
- `image_ratio = total_images / page_count`
- `recommended_backend`:
  - `is_scanned=True AND image_ratio > 0.5` → `"gemma-4-26b-a4b-vision"` (workhorse VLM)
  - `is_scanned=True AND image_ratio <= 0.5` → `"docling-serve"` (layout)
  - `is_scanned=False` → `""` (text-layer is sufficient)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ScannedPDFReport:
    """The detection result for one PDF."""

    is_scanned: bool
    image_ratio: float
    avg_text_density: float
    recommended_backend: str
    page_count: int
    blank_page_count: int
    total_text_chars: int


TEXT_DENSITY_THRESHOLD = 50
BLANK_PAGE_RATIO_THRESHOLD = 0.8
IMAGE_HEAVY_THRESHOLD = 0.5


def is_scanned_pdf(path: Path) -> ScannedPDFReport:
    """Detect whether a PDF is image-only (scanned) vs text-layer."""
    try:
        import pymupdf  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("pymupdf_not_available_for_scanned_detection", path=str(path))
        return ScannedPDFReport(False, 0.0, 0.0, "", 0, 0, 0)

    try:
        doc = pymupdf.open(str(path))
    except (OSError, ValueError, RuntimeError) as exc:  # noqa: BLE001
        logger.warning("scanned_detector_open_failed", path=str(path), error=str(exc))
        return ScannedPDFReport(False, 0.0, 0.0, "", 0, 0, 0)

    page_count = 0
    blank_page_count = 0
    total_text_chars = 0
    total_images = 0

    try:
        for page in doc:
            page_count += 1
            text = page.get_text() or ""
            if not text:
                blank_page_count += 1
            total_text_chars += len(text)
            total_images += len(page.get_images())
    finally:
        doc.close()

    if page_count > 0:
        image_ratio = total_images / page_count
        avg_text_density = total_text_chars / page_count
        blank_page_ratio = blank_page_count / page_count
    else:
        image_ratio = 0.0
        avg_text_density = 0.0
        blank_page_ratio = 0.0

    is_scanned = (total_text_chars < TEXT_DENSITY_THRESHOLD) or (
        blank_page_ratio > BLANK_PAGE_RATIO_THRESHOLD
    )

    if is_scanned and image_ratio > IMAGE_HEAVY_THRESHOLD:
        recommended_backend = "gemma-4-26b-a4b-vision"
    elif is_scanned:
        recommended_backend = "docling-serve"
    else:
        recommended_backend = ""

    if is_scanned:
        logger.info(
            "scanned_pdf_detected",
            path=str(path),
            page_count=page_count,
            blank_page_count=blank_page_count,
            total_text_chars=total_text_chars,
            image_ratio=round(image_ratio, 3),
            recommended_backend=recommended_backend,
        )

    return ScannedPDFReport(
        is_scanned=is_scanned,
        image_ratio=image_ratio,
        avg_text_density=avg_text_density,
        recommended_backend=recommended_backend,
        page_count=page_count,
        blank_page_count=blank_page_count,
        total_text_chars=total_text_chars,
    )


__all__ = ["ScannedPDFReport", "is_scanned_pdf"]
