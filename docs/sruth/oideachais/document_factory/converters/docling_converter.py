"""
Docling Converter.

IBM's document understanding library with excellent structure preservation.
Best for NCCA curriculum documents with complex hierarchies.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from ..base import ExtractionResult
from ..pdf_factory import PDFConverter

logger = logging.getLogger(__name__)


class DoclingConverter(PDFConverter):
    """
    PDF converter using IBM Docling.

    Characteristics:
    - Deep document structure understanding
    - Excellent for hierarchical content
    - Strong table detection
    - Good for curriculum specifications
    """

    _converter = None

    def __init__(self):
        """Initialize converter."""
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "docling"

    @property
    def available(self) -> bool:
        """Check if docling is installed."""
        if self._available is None:
            try:
                from docling.document_converter import DocumentConverter

                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def _get_converter(self):
        """Get or create the Docling converter."""
        if self._converter is None:
            from docling.document_converter import DocumentConverter

            self._converter = DocumentConverter()
        return self._converter

    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract content from PDF using Docling."""
        import time

        start_time = time.time()

        if not self.available:
            return ExtractionResult(
                success=False,
                error_message="docling not installed",
            )

        try:
            converter = self._get_converter()

            # Convert document
            result = converter.convert(str(file_path))
            doc = result.document

            # Export to Markdown
            md_text = doc.export_to_markdown()

            # Extract metadata
            metadata: dict[str, Any] = {
                "output_format": "markdown",
                "structure": {
                    "sections": len(doc.sections) if hasattr(doc, "sections") else 0,
                    "tables": len(doc.tables) if hasattr(doc, "tables") else 0,
                    "figures": len(doc.figures) if hasattr(doc, "figures") else 0,
                },
            }

            # Count pages
            page_count = len(doc.pages) if hasattr(doc, "pages") else 0

            duration_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                success=True,
                content_text=md_text,
                extraction_confidence=0.90,
                extractor_used=self.name,
                extraction_duration_ms=duration_ms,
                pages_extracted=page_count,
                metadata=metadata,
                raw_output=doc,
            )

        except Exception as e:
            logger.error(f"Docling extraction failed: {e}")
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
        if not self.available:
            return ""

        try:
            converter = self._get_converter()
            result = converter.convert(str(file_path))
            return result.document.export_to_text()
        except Exception as e:
            logger.error(f"Docling text extraction failed: {e}")
            return ""

    async def extract_tables(self, file_path: Path) -> list[dict[str, Any]]:
        """Extract tables from PDF as structured data."""
        if not self.available:
            return []

        try:
            converter = self._get_converter()
            result = converter.convert(str(file_path))
            doc = result.document

            tables = []
            if hasattr(doc, "tables"):
                for i, table in enumerate(doc.tables):
                    tables.append({
                        "index": i,
                        "data": table.export_to_dataframe().to_dict()
                        if hasattr(table, "export_to_dataframe")
                        else {},
                    })
            return tables

        except Exception as e:
            logger.error(f"Docling table extraction failed: {e}")
            return []
