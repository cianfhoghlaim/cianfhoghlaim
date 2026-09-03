"""
Marker Converter.

High-quality PDF extraction using Marker with ML-based layout understanding.
Best for complex layouts like exam papers with tables and figures.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..base import ExtractionResult
from ..pdf_factory import PDFConverter

logger = logging.getLogger(__name__)


class MarkerConverter(PDFConverter):
    """
    PDF converter using Marker.

    Characteristics:
    - ML-based layout analysis
    - Excellent table extraction
    - Good figure handling
    - Slower than PyMuPDF but higher quality
    """

    _marker = None
    _model = None

    def __init__(self, batch_multiplier: int = 2):
        """
        Initialize converter.

        Args:
            batch_multiplier: Controls memory/speed tradeoff
        """
        self._available: bool | None = None
        self.batch_multiplier = batch_multiplier

    @property
    def name(self) -> str:
        return "marker"

    @property
    def available(self) -> bool:
        """Check if marker is installed."""
        if self._available is None:
            try:
                from marker.converters.pdf import PdfConverter

                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def _get_converter(self):
        """Get or create the Marker converter."""
        if self._marker is None:
            from marker.converters.pdf import PdfConverter

            self._marker = PdfConverter()
        return self._marker

    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract content from PDF using Marker."""
        import time

        start_time = time.time()

        if not self.available:
            return ExtractionResult(
                success=False,
                error_message="marker not installed",
            )

        try:
            converter = self._get_converter()

            # Convert PDF
            rendered = converter(str(file_path))

            # Get markdown output
            md_text = rendered.markdown

            # Extract metadata
            metadata: dict[str, Any] = {
                "output_format": "markdown",
                "has_images": bool(rendered.images),
                "image_count": len(rendered.images) if rendered.images else 0,
            }

            duration_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                success=True,
                content_text=md_text,
                extraction_confidence=0.92,  # High quality extraction
                extractor_used=self.name,
                extraction_duration_ms=duration_ms,
                pages_extracted=rendered.metadata.get("pages", 0) if rendered.metadata else 0,
                metadata=metadata,
                raw_output=rendered,
            )

        except Exception as e:
            logger.error(f"Marker extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                extractor_used=self.name,
                extraction_duration_ms=(time.time() - start_time) * 1000,
            )

    async def convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to Markdown."""
        result = await self.extract(file_path)
        return result.content_text

    async def convert_to_text(self, file_path: Path) -> str:
        """Convert PDF to plain text."""
        result = await self.extract(file_path)
        # Strip Markdown formatting
        import re

        text = result.content_text
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*+([^*]+)\*+", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        return text
