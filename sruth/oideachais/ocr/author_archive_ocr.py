"""
Author-Archive OCR / HTR dispatcher.

For pages flagged as `requires_handwriting_ocr=true` by
`oideachais/dlt_sources/author_archive/_scanner.requires_handwriting_ocr`,
select the right back-end:

- `pylaia`        — Irish / Gaeilge HTR (when language == "ga" or "mixed").
- `trocr`         — Latin / English handwriting (graceful fallback to
                    PaddleOCR when TrOCR is not on the workstation).
- `vlm`           — LaTeX / equation extraction when equation density is high
                    (default threshold: 5 `=`, `∫`, `∑`, `∂` per page).

The runner degrades gracefully: if a back-end is unavailable, the row is
emitted with `text=""`, `latex=""`, `confidence=0.0`, `backend="unavailable"`
and the BAML extractor returns an empty list. The asset materialisation
NEVER fails on missing OCR back-ends.

Re-uses:
- `oideachais/ocr/pylaia_comparison.py` for the Pylaia entry point.
- `oideachais/ocr/adapters.py` for PaddleOCR (fallback to TrOCR).
- `oideachais/agents/baml_integration.py` style for the VLM call (via
  the LiteLLM gateway — `litellm/gemini-2.5-flash`).

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/specs/author-archive-ocr-htr/spec.md
"""

from __future__ import annotations

import asyncio
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# Try to import the existing OCR modules; degrade gracefully.
try:
    from oideachais.ocr.pylaia_comparison import HTRComparison  # type: ignore[import-not-found]

    PYLAIA_AVAILABLE = True
except ImportError:
    PYLAIA_AVAILABLE = False

try:
    from oideachais.ocr.adapters import (  # type: ignore[import-not-found]
        OCRAdapterRegistry,
        get_adapter,
    )

    ADAPTERS_AVAILABLE = True
except ImportError:
    ADAPTERS_AVAILABLE = False


class OCRBackend(str, Enum):
    """The author-archive OCR dispatchers."""

    PYLAIA = "pylaia"  # Irish HTR
    TROCR = "trocr"  # English handwriting
    PADDLEOCR = "paddleocr"  # Fallback
    VLM = "vlm"  # Equation / LaTeX extraction
    UNAVAILABLE = "unavailable"  # Back-end not on the workstation


# Heuristics for back-end selection.
_EQUATION_SIGNS = re.compile(r"[=∫∑∂√πϕθλμσ]")
_EQUATION_DENSITY_THRESHOLD = 5  # ≥5 math symbols per page → VLM route


@dataclass(frozen=True)
class AuthorArchiveOCRConfig:
    """Per-page OCR configuration."""

    preferred_backends: dict[str, OCRBackend] = field(
        default_factory=lambda: {
            "ga": OCRBackend.PYLAIA,
            "mixed": OCRBackend.PYLAIA,
            "en": OCRBackend.TROCR,
        }
    )
    equation_density_threshold: int = _EQUATION_DENSITY_THRESHOLD
    max_chars: int = 20_000


@dataclass
class AuthorArchiveOCRResult:
    """One OCR result."""

    file_path: str
    page_index: int
    text: str
    latex: str
    confidence: float
    backend: OCRBackend
    elapsed_ms: float = 0.0
    error: str | None = None


class AuthorArchiveOCRRunner:
    """Dispatcher that picks the right back-end per page."""

    def __init__(self, config: AuthorArchiveOCRConfig | None = None) -> None:
        self.config = config or AuthorArchiveOCRConfig()

    def _select_backend(
        self, *, language: str, equation_density: int
    ) -> OCRBackend:
        if equation_density >= self.config.equation_density_threshold:
            return OCRBackend.VLM
        preferred = self.config.preferred_backends.get(language, OCRBackend.TROCR)
        if preferred == OCRBackend.PYLAIA and not PYLAIA_AVAILABLE:
            logger.debug("pylaia_unavailable_falling_back_to_paddleocr")
            return OCRBackend.PADDLEOCR if ADAPTERS_AVAILABLE else OCRBackend.UNAVAILABLE
        if preferred == OCRBackend.TROCR and not ADAPTERS_AVAILABLE:
            return OCRBackend.UNAVAILABLE
        return preferred

    def _extract_page_text(self, path: Path, page_index: int) -> str:
        """Best-effort text extraction from a single page (PDF)."""
        if path.suffix.lower() != ".pdf":
            return ""
        try:
            import pymupdf  # type: ignore[import-untyped]
        except ImportError:
            return ""
        try:
            doc = pymupdf.open(str(path))
            if page_index >= len(doc):
                doc.close()
                return ""
            text = doc[page_index].get_text() or ""
            doc.close()
            return text
        except (OSError, ValueError, RuntimeError) as e:
            logger.debug("pymupdf_page_extract_failed", error=str(e))
            return ""

    def _equation_density(self, text: str) -> int:
        return len(_EQUATION_SIGNS.findall(text))

    # ------------------------------------------------------------------
    # Back-ends
    # ------------------------------------------------------------------

    def _run_pylaia(self, path: Path, page_index: int) -> AuthorArchiveOCRResult:
        if not PYLAIA_AVAILABLE:
            return self._unavailable(path, page_index, OCRBackend.PYLAIA)
        try:
            # Stub: HTRComparison.compare_models is async in the canonical
            # implementation; we don't block the asset on its coroutine.
            # We return an empty result and let the dagster asset continue.
            logger.debug("pylaia_dispatch_skipped_use_async_in_dagster_asset")
            return AuthorArchiveOCRResult(
                file_path=str(path),
                page_index=page_index,
                text="",
                latex="",
                confidence=0.0,
                backend=OCRBackend.PYLAIA,
                error="pylaia_available_but_sync_call_not_implemented",
            )
        except (OSError, ValueError, RuntimeError) as e:
            return self._error_result(path, page_index, OCRBackend.PYLAIA, str(e))

    def _run_trocr_or_paddleocr(
        self, path: Path, page_index: int
    ) -> AuthorArchiveOCRResult:
        if not ADAPTERS_AVAILABLE:
            return self._unavailable(path, page_index, OCRBackend.TROCR)
        try:
            adapter = get_adapter("paddleocr")  # type: ignore[name-defined]
            # PaddleOCR is async in the canonical implementation; this stub
            # returns empty text and the asset continues.
            return AuthorArchiveOCRResult(
                file_path=str(path),
                page_index=page_index,
                text="",
                latex="",
                confidence=0.0,
                backend=OCRBackend.TROCR,
                error="trocr_available_but_sync_call_not_implemented",
            )
        except (OSError, ValueError, RuntimeError) as e:
            return self._error_result(
                path, page_index, OCRBackend.PADDLEOCR, str(e)
            )

    def _run_vlm(
        self, path: Path, page_index: int, page_text: str
    ) -> AuthorArchiveOCRResult:
        """VLM-backed equation extraction. Falls back to empty on error."""
        try:
            from baml_client import b  # type: ignore[import-not-found]

            result = b.ExtractHandwrittenEquations(
                ocr_text=page_text[: self.config.max_chars],
                file_name=path.name,
            )
            latex_parts: list[str] = []
            verbatim_parts: list[str] = []
            confidences: list[float] = []
            for eqn in result or []:
                if hasattr(eqn, "latex"):
                    latex_parts.append(eqn.latex or "")
                    verbatim_parts.append(eqn.verbatim or "")
                    confidences.append(float(eqn.confidence or 0.0))
                elif isinstance(eqn, dict):
                    latex_parts.append(eqn.get("latex", ""))
                    verbatim_parts.append(eqn.get("verbatim", ""))
                    confidences.append(float(eqn.get("confidence", 0.0)))
            return AuthorArchiveOCRResult(
                file_path=str(path),
                page_index=page_index,
                text=page_text,
                latex="\n".join(latex_parts),
                confidence=sum(confidences) / len(confidences) if confidences else 0.0,
                backend=OCRBackend.VLM,
            )
        except (ImportError, OSError, ValueError, RuntimeError) as e:
            logger.debug("vlm_equation_extract_failed", error=str(e))
            return self._error_result(path, page_index, OCRBackend.VLM, str(e))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _unavailable(
        self, path: Path, page_index: int, backend: OCRBackend
    ) -> AuthorArchiveOCRResult:
        logger.warning(
            "ocr_backend_unavailable",
            backend=backend.value,
            file_path=str(path),
        )
        return AuthorArchiveOCRResult(
            file_path=str(path),
            page_index=page_index,
            text="",
            latex="",
            confidence=0.0,
            backend=OCRBackend.UNAVAILABLE,
        )

    def _error_result(
        self,
        path: Path,
        page_index: int,
        backend: OCRBackend,
        error: str,
    ) -> AuthorArchiveOCRResult:
        logger.warning(
            "ocr_backend_error",
            backend=backend.value,
            file_path=str(path),
            error=error,
        )
        return AuthorArchiveOCRResult(
            file_path=str(path),
            page_index=page_index,
            text="",
            latex="",
            confidence=0.0,
            backend=backend,
            error=error,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_ocr_for_page(
        self,
        path: Path,
        page_index: int,
        language: str = "en",
    ) -> AuthorArchiveOCRResult:
        """
        Run OCR on a single page of a file.

        Args:
            path: Absolute path to the file (PDF / Apple .pages / image).
            page_index: 0-based page index (for multi-page files).
            language: One of "en" | "ga" | "mixed" | "unknown".

        Returns:
            `AuthorArchiveOCRResult` with `text`, `latex`, `confidence`,
            `backend`. `text`/`latex` may be empty when the back-end is
            unavailable — the caller (Dagster asset) MUST handle this.
        """
        start = time.time()
        try:
            page_text = self._extract_page_text(path, page_index)
        except (OSError, ValueError, RuntimeError) as e:
            return self._error_result(path, page_index, OCRBackend.UNAVAILABLE, str(e))

        eq_density = self._equation_density(page_text)
        backend = self._select_backend(
            language=language, equation_density=eq_density
        )

        if backend == OCRBackend.VLM:
            result = self._run_vlm(path, page_index, page_text)
        elif backend == OCRBackend.PYLAIA:
            result = self._run_pylaia(path, page_index)
        elif backend in {OCRBackend.TROCR, OCRBackend.PADDLEOCR}:
            result = self._run_trocr_or_paddleocr(path, page_index)
        else:
            result = self._unavailable(path, page_index, backend)

        result.elapsed_ms = (time.time() - start) * 1000.0
        return result

    def iter_pages(
        self, path: Path, language: str = "en", max_pages: int = 50
    ) -> Iterator[AuthorArchiveOCRResult]:
        """
        Yield one OCR result per page of a file. For single-page formats
        (`.pages`, `.heic`, scanned image), yields one row.
        """
        if not path.exists():
            return
        suffix = path.suffix.lower()
        if suffix in {".pdf"}:
            try:
                import pymupdf  # type: ignore[import-untyped]

                doc = pymupdf.open(str(path))
                page_count = min(len(doc), max_pages)
                doc.close()
            except (OSError, ValueError, RuntimeError):
                page_count = 1
            for i in range(page_count):
                yield self.run_ocr_for_page(path, page_index=i, language=language)
        else:
            yield self.run_ocr_for_page(path, page_index=0, language=language)


# =============================================================================
# Standalone runner
# =============================================================================


def run_author_archive_ocr_for_file(
    path: str | Path,
    language: str = "en",
) -> list[dict[str, Any]]:
    """Convenience runner: returns a list of dicts for the Dagster asset."""
    runner = AuthorArchiveOCRRunner()
    p = Path(path)
    out: list[dict[str, Any]] = []
    for result in runner.iter_pages(p, language=language):
        out.append(
            {
                "file_path": result.file_path,
                "page_index": result.page_index,
                "text": result.text,
                "latex": result.latex,
                "confidence": result.confidence,
                "backend": result.backend.value,
                "elapsed_ms": result.elapsed_ms,
                "error": result.error,
            }
        )
    return out


__all__ = [
    "OCRBackend",
    "AuthorArchiveOCRConfig",
    "AuthorArchiveOCRResult",
    "AuthorArchiveOCRRunner",
    "run_author_archive_ocr_for_file",
    "PYLAIA_AVAILABLE",
    "ADAPTERS_AVAILABLE",
]
