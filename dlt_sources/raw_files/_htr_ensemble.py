"""HTR ensemble router for the UoG personal-archive pipeline.

For every file the DLT source emits, ``route_htr()`` decides which
HTR (Handwritten Text Recognition) backend to use, and
``htr_extract_pages()`` runs the chosen backend and returns the
extracted markdown text + the HTR confidence.

The 5 backends:

- ``NOUGAT`` — Meta's nougat-ocr (Scientific Paper OCR)
- ``OLMOCR_2_7B`` — the Allen AI olmocr-2-7b model
- ``COGVLM`` — THUDM's CogVLM (general-purpose VLM)
- ``GEMMA_3`` — Google's gemma-3 VLM
- ``MULTI_VLM_CONSENSUS`` — the 4-VLM ensemble + majority-vote
  consensus (the production path for handwritten / scanned PDFs)
- ``PYMUPDF_TYPED`` — typed-text path (the default for born-digital
  PDFs that pymupdf can extract directly)

The routing heuristic is intentionally simple:

- ``.pages`` / ``.heic`` → MULTI_VLM_CONSENSUS (confidence 0.5)
- filename contains ``handwritten`` / ``goodnotes`` / ``apple_pencil`` →
  MULTI_VLM_CONSENSUS (confidence 0.5)
- ``pymupdf_chars_per_page < 100`` (i.e. scanned) →
  MULTI_VLM_CONSENSUS (confidence 0.4)
- else → PYMUPDF_TYPED (confidence 0.95)

For the MULTI_VLM_CONSENSUS path, the ensemble defers-imports
``meaisinfhoghlaim.ocr.ensemble.ensembled_extractor.EnsembledExtractor``
(the BIEP v2 4-path OCR/VLM extractor per
`openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/`)
and runs the 4-VLM ensemble (nougat + olmocr-2-7b + CogVLM + gemma-3)
with majority-vote consensus on extracted equations. If all 4
disagree on >30%, the ensemble falls back to nougat (the
single-VLM best-of-breed for scientific papers).

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

from __future__ import annotations

import hashlib
import os
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class HTRBackend(str, Enum):
    """The 6 HTR backends the personal-archive pipeline can route to."""

    NOUGAT = "NOUGAT"
    OLMOCR_2_7B = "OLMOCR_2_7B"
    COGVLM = "COGVLM"
    GEMMA_3 = "GEMMA_3"
    MULTI_VLM_CONSENSUS = "MULTI_VLM_CONSENSUS"
    PYMUPDF_TYPED = "PYMUPDF_TYPED"
    NONE = "NONE"


# ---------------------------------------------------------------------------- #
# Routing heuristic
# ---------------------------------------------------------------------------- #


_HANDWRITTEN_FILENAME_TOKENS: tuple[str, ...] = (
    "handwritten",
    "goodnotes",
    "apple_pencil",
)

_HANDWRITTEN_EXTENSIONS: tuple[str, ...] = (
    ".pages",
    ".heic",
)

_SCANNED_CHARS_PER_PAGE_THRESHOLD: float = 100.0


def route_htr(
    file_path: Path,
    pymupdf_chars_per_page: float,
) -> tuple[HTRBackend, float]:
    """Pick the HTR backend + confidence for one file.

    Args:
        file_path: The absolute path to the file.
        pymupdf_chars_per_page: The number of characters per page
            pymupdf could extract (0 if pymupdf couldn't open the
            file). Used to detect scanned PDFs.

    Returns:
        (backend, confidence)
    """
    suffix = file_path.suffix.lower()
    name_lower = file_path.name.lower()

    if suffix in _HANDWRITTEN_EXTENSIONS:
        return HTRBackend.MULTI_VLM_CONSENSUS, 0.5

    if any(token in name_lower for token in _HANDWRITTEN_FILENAME_TOKENS):
        return HTRBackend.MULTI_VLM_CONSENSUS, 0.5

    if pymupdf_chars_per_page < _SCANNED_CHARS_PER_PAGE_THRESHOLD:
        return HTRBackend.MULTI_VLM_CONSENSUS, 0.4

    return HTRBackend.PYMUPDF_TYPED, 0.95


# ---------------------------------------------------------------------------- #
# Extraction helpers
# ---------------------------------------------------------------------------- #


def _pymupdf_chars_per_page(file_path: Path) -> float:
    """Return the pymupdf chars/page for a PDF; 0.0 if pymupdf fails."""
    try:
        from dlt_sources.education.ireland.british_isles.education._pdf_text import (
            extract_pdf_text,
        )

        text = extract_pdf_text(file_path, max_chars=50_000)
        if not text:
            return 0.0
        # Rough approximation: assume 1 page per 2000 chars.
        return len(text) / max(1, text.count("\n\n") + 1)
    except (ImportError, OSError, RuntimeError) as exc:
        logger.warning(
            "htr_pymupdf_chars_per_page_failed",
            path=str(file_path),
            error=str(exc),
        )
        return 0.0


def _extract_pymupdf_typed(file_path: Path) -> tuple[str, float]:
    """Typed-text path via pymupdf (the BIEP v1 helper)."""
    try:
        from dlt_sources.education.ireland.british_isles.education._pdf_text import (
            extract_pdf_text,
        )

        text = extract_pdf_text(file_path, max_chars=50_000)
        return text, 0.95
    except ImportError as exc:
        logger.warning(
            "htr_pymupdf_import_missing",
            path=str(file_path),
            error=str(exc),
        )
        return "", 0.0


def _extract_multi_vlm_consensus(
    file_path: Path,
    confidence: float,
) -> tuple[str, float]:
    """Multi-VLM consensus path.

    Defer-imports ``EnsembledExtractor`` from
    ``meaisinfhoghlaim.ocr.ensemble.ensembled_extractor`` (the BIEP v2
    4-path OCR/VLM extractor). Runs all 4 VLMs in parallel and
    majority-votes the consensus on extracted equations.

    Fallback chain:
    1. Try the canonical ensemble (nougat + olmocr-2-7b + CogVLM + gemma-3)
    2. If the ensemble raises, fall back to nougat alone
    3. If nougat is missing, return an empty string + 0.0 confidence

    Args:
        file_path: The absolute path to the file.
        confidence: The router's confidence (0.4 or 0.5).

    Returns:
        (extracted_text, htr_confidence)
    """
    # Try the canonical ensemble first.
    try:
        from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import (
            EnsembledExtractor,
        )

        extractor = EnsembledExtractor()
        result = extractor.extract(
            pdf_path=str(file_path),
            baml_function="ExtractUoGPersonalArchiveArtefact",
        )
        markdown = getattr(result, "consensus_markdown", None) or getattr(
            result, "raw_response", ""
        )
        return markdown, confidence

    except ImportError as exc:
        logger.warning(
            "htr_ensemble_import_missing_falling_back_to_nougat",
            path=str(file_path),
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 — fallback chain
        logger.warning(
            "htr_ensemble_failed_falling_back_to_nougat",
            path=str(file_path),
            error=str(exc),
        )

    # Fallback: try nougat via the legacy stub.
    try:
        from meaisinfhoghlaim.ocr.models import nougat_extract  # type: ignore[import-not-found]

        text = nougat_extract(str(file_path))
        return text, confidence
    except (ImportError, Exception) as exc:  # noqa: BLE001
        logger.warning(
            "htr_nougat_fallback_failed",
            path=str(file_path),
            error=str(exc),
        )

    return "", 0.0


def htr_extract_pages(
    file_path: Path,
    backend: HTRBackend,
) -> tuple[str, float]:
    """Run the chosen HTR backend and return (markdown_text, confidence).

    Args:
        file_path: The absolute path to the file.
        backend: The HTR backend chosen by ``route_htr()``.

    Returns:
        (extracted_text, htr_confidence)
    """
    if backend == HTRBackend.PYMUPDF_TYPED:
        return _extract_pymupdf_typed(file_path)
    if backend == HTRBackend.MULTI_VLM_CONSENSUS:
        confidence = 0.5 if file_path.suffix.lower() in _HANDWRITTEN_EXTENSIONS else 0.4
        return _extract_multi_vlm_consensus(file_path, confidence)
    if backend == HTRBackend.NONE:
        return "", 0.0
    # Single-VLM fallbacks (NOUGAT / OLMOCR_2_7B / COGVLM / GEMMA_3) are
    # exercised by the MULTI_VLM_CONSENSUS path's ensemble — direct
    # single-VLM invocation is reserved for future per-backend A/B testing.
    logger.warning(
        "htr_backend_not_implemented",
        backend=backend.value,
        path=str(file_path),
    )
    return _extract_pymupdf_typed(file_path)


def auto_extract(file_path: Path) -> tuple[str, float, HTRBackend]:
    """Convenience: route + extract in one call.

    Returns:
        (extracted_text, htr_confidence, backend_used)
    """
    chars_per_page = _pymupdf_chars_per_page(file_path)
    backend, confidence = route_htr(file_path, chars_per_page)
    text, htr_conf = htr_extract_pages(file_path, backend)
    return text, htr_conf, backend


__all__ = [
    "HTRBackend",
    "route_htr",
    "htr_extract_pages",
    "auto_extract",
]
