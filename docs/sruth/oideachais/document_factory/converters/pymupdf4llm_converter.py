"""
PyMuPDF4LLM Converter.

Fast, reliable PDF extraction using PyMuPDF with LLM-optimized output.
Best for simple text-heavy documents like circulars.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..base import ExtractionResult
from ..pdf_factory import PDFConverter

logger = logging.getLogger(__name__)


class PyMuPDF4LLMConverter(PDFConverter):
    """
    PDF converter using PyMuPDF4LLM.

    Characteristics:
    - Very fast extraction
    - Good for text-heavy PDFs
    - Limited table/image handling
    - Native Markdown output
    """

    _pymupdf4llm = None

    def __init__(self):
        """Initialize converter (library loaded on first use)."""
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "pymupdf4llm"

    @property
    def available(self) -> bool:
        """Check if pymupdf4llm is installed."""
        if self._available is None:
            try:
                import pymupdf4llm

                self._pymupdf4llm = pymupdf4llm
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def _get_library(self):
        """Get the pymupdf4llm library."""
        if self._pymupdf4llm is None:
            import pymupdf4llm

            self._pymupdf4llm = pymupdf4llm
        return self._pymupdf4llm

    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract content from PDF using PyMuPDF4LLM."""
        import time

        start_time = time.time()

        if not self.available:
            return ExtractionResult(
                success=False,
                error_message="pymupdf4llm not installed",
            )

        try:
            pymupdf4llm = self._get_library()

            # Extract as Markdown (native output format)
            md_text = pymupdf4llm.to_markdown(str(file_path))

            # Get page count
            import fitz

            doc = fitz.open(str(file_path))
            page_count = len(doc)
            doc.close()

            duration_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                success=True,
                content_text=md_text,
                extraction_confidence=0.85,  # Good for text, lower for complex layouts
                extractor_used=self.name,
                extraction_duration_ms=duration_ms,
                pages_extracted=page_count,
                metadata={
                    "output_format": "markdown",
                    "library_version": getattr(pymupdf4llm, "__version__", "unknown"),
                },
            )

        except Exception as e:
            logger.error(f"PyMuPDF4LLM extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                extractor_used=self.name,
                extraction_duration_ms=(time.time() - start_time) * 1000,
            )

    async def convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to Markdown (native format for this converter)."""
        result = await self.extract(file_path)
        return result.content_text

    async def convert_to_text(self, file_path: Path) -> str:
        """Convert PDF to plain text."""
        result = await self.extract(file_path)
        # Strip Markdown formatting for plain text
        import re

        text = result.content_text
        # Remove headers
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r"\*+([^*]+)\*+", r"\1", text)
        # Remove links
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        return text
