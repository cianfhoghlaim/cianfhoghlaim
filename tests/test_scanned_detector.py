"""Tests for the ScannedPDFDetector.

Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.13): the
`is_scanned_pdf()` function in
`meaisinfhoghlaim/backends/scanned_detector.py` is the canonical
scanned-PDF detector for the BIEP v3 OCR fanout layer (per the
`2026-08-10-ocr-vision-activation-v1` change).

This test file covers the 4 canonical scenarios from the spec:
1. Pure text-layer PDF (e.g. NCCA HTML-converted syllabus)
2. Pure image-only scanned PDF (e.g. legacy SEC exam paper scan)
3. Image-heavy mixed PDF (e.g. syllabus with diagrams)
4. Empty PDF (0 pages — defensive)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Make meaisinfhoghlaim importable when running from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from meaisinfhoghlaim.backends.scanned_detector import (  # noqa: E402
    BLANK_PAGE_RATIO_THRESHOLD,
    IMAGE_HEAVY_THRESHOLD,
    TEXT_DENSITY_THRESHOLD,
    ScannedPDFReport,
    is_scanned_pdf,
)


# ─── Mocked-pymupdf tests (no real PDF needed) ───────────────────────────────


def _make_mock_pdf(page_texts: list[str], images_per_page: list[int]) -> MagicMock:
    """Build a mock pymupdf document where each page has the given text and image counts."""
    doc = MagicMock()
    pages = []
    for text, n_images in zip(page_texts, images_per_page):
        page = MagicMock()
        page.get_text.return_value = text
        page.get_images.return_value = list(range(n_images))
        pages.append(page)
    doc.__iter__ = lambda self: iter(pages)
    return doc


def test_pure_text_layer_pdf_is_not_scanned(monkeypatch) -> None:
    """Scenario 1: A text-layer PDF (e.g. NCCA HTML-converted syllabus) is NOT scanned."""
    # 5 pages, each with 1000+ chars of text, 0 images
    mock_doc = _make_mock_pdf(
        page_texts=["Lorem ipsum " * 100] * 5,
        images_per_page=[0] * 5,
    )
    monkeypatch.setattr("pymupdf.open", lambda *a, **kw: mock_doc)

    report = is_scanned_pdf(Path("/tmp/fake.pdf"))

    assert report.is_scanned is False
    assert report.image_ratio == 0.0
    assert report.recommended_backend == ""
    assert report.page_count == 5
    assert report.blank_page_count == 0
    assert report.total_text_chars == 5 * 100 * 12  # "Lorem ipsum " × 100


def test_pure_scanned_pdf_is_scanned_with_qwen3vl(monkeypatch) -> None:
    """Scenario 2: A scanned PDF (no text, 1 image per page) routes to qwen3-vl-8b."""
    # 4 pages, each with empty text but 1 image — pure scan
    mock_doc = _make_mock_pdf(
        page_texts=[""] * 4,
        images_per_page=[1] * 4,
    )
    monkeypatch.setattr("pymupdf.open", lambda *a, **kw: mock_doc)

    report = is_scanned_pdf(Path("/tmp/scanned.pdf"))

    assert report.is_scanned is True
    assert report.image_ratio == 1.0
    # image_ratio > 0.5 means image-heavy → qwen3-vl-8b
    assert report.recommended_backend == "qwen3-vl-8b"
    assert report.page_count == 4
    assert report.blank_page_count == 4
    assert report.total_text_chars == 0


def test_mixed_pdf_with_few_images_routes_to_docling(monkeypatch) -> None:
    """Scenario 3: A scanned PDF with few images routes to docling-serve (layout)."""
    # 6 pages, each empty text, 0.2 images/page (low image ratio)
    mock_doc = _make_mock_pdf(
        page_texts=[""] * 6,
        images_per_page=[0, 0, 1, 0, 0, 0],  # avg 0.17
    )
    monkeypatch.setattr("pymupdf.open", lambda *a, **kw: mock_doc)

    report = is_scanned_pdf(Path("/tmp/mixed.pdf"))

    assert report.is_scanned is True
    assert report.image_ratio < IMAGE_HEAVY_THRESHOLD  # not image-heavy
    assert report.recommended_backend == "docling-serve"


def test_empty_pdf_returns_zero_report(monkeypatch) -> None:
    """Scenario 4: An empty PDF (0 pages) reports zero metrics (defensive).

    Per the implementation: when page_count=0, total_text_chars=0 which
    is < TEXT_DENSITY_THRESHOLD (50), so is_scanned=True. With
    image_ratio=0.0 (no images), the recommended backend is
    docling-serve (the layout-specialist, which can extract structure
    from any input, even an empty PDF).
    """
    mock_doc = _make_mock_pdf(page_texts=[], images_per_page=[])
    monkeypatch.setattr("pymupdf.open", lambda *a, **kw: mock_doc)

    report = is_scanned_pdf(Path("/tmp/empty.pdf"))

    # The empty PDF has total_text_chars=0 < TEXT_DENSITY_THRESHOLD so
    # is_scanned=True. image_ratio=0.0 means docling-serve is chosen
    # (per the per-image-ratio routing logic).
    assert report.is_scanned is True
    assert report.image_ratio == 0.0
    assert report.avg_text_density == 0.0
    assert report.recommended_backend == "docling-serve"
    assert report.page_count == 0


def test_pymupdf_not_available_returns_safe_default(monkeypatch) -> None:
    """When pymupdf is not installed, return the safe-default report (not scanned)."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pymupdf":
            raise ImportError("pymupdf not installed")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    report = is_scanned_pdf(Path("/tmp/fake.pdf"))

    # Defensive: not scanned + no recommended backend (avoids sending to
    # qwen3-vl when we can't actually detect the image ratio)
    assert report.is_scanned is False
    assert report.recommended_backend == ""
    assert report.page_count == 0


def test_constants_match_spec() -> None:
    """The detector constants match the values documented in the spec."""
    assert TEXT_DENSITY_THRESHOLD == 50
    assert BLANK_PAGE_RATIO_THRESHOLD == 0.8
    assert IMAGE_HEAVY_THRESHOLD == 0.5


def test_scanned_pdf_report_is_frozen() -> None:
    """ScannedPDFReport is a frozen dataclass (immutable after construction)."""
    report = ScannedPDFReport(
        is_scanned=True,
        image_ratio=0.9,
        avg_text_density=0.0,
        recommended_backend="qwen3-vl-8b",
        page_count=4,
        blank_page_count=4,
        total_text_chars=0,
    )
    import dataclasses

    try:
        report.is_scanned = False  # type: ignore[misc]
        raise AssertionError("ScannedPDFReport should be frozen")
    except dataclasses.FrozenInstanceError:
        pass  # expected