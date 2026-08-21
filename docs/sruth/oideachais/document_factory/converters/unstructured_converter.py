"""
Unstructured Converter.

General-purpose document extraction using the Unstructured library.
Good fallback for various document types.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from ..base import ExtractionResult
from ..pdf_factory import PDFConverter

logger = logging.getLogger(__name__)


class UnstructuredConverter(PDFConverter):
    """
    PDF converter using Unstructured.

    Characteristics:
    - General-purpose extraction
    - Supports many document types
    - Good element detection
    - Moderate quality, reliable fallback
    """

    def __init__(self, strategy: str = "auto"):
        """
        Initialize converter.

        Args:
            strategy: Extraction strategy ('auto', 'fast', 'hi_res', 'ocr_only')
        """
        self._available: Optional[bool] = None
        self.strategy = strategy

    @property
    def name(self) -> str:
        return "unstructured"

    @property
    def available(self) -> bool:
        """Check if unstructured is installed."""
        if self._available is None:
            try:
                from unstructured.partition.pdf import partition_pdf

                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract content from PDF using Unstructured."""
        import time

        start_time = time.time()

        if not self.available:
            return ExtractionResult(
                success=False,
                error_message="unstructured not installed",
            )

        try:
            from unstructured.partition.pdf import partition_pdf

            # Partition the PDF
            elements = partition_pdf(
                filename=str(file_path),
                strategy=self.strategy,
            )

            # Build Markdown output
            md_parts = []
            element_counts: dict[str, int] = {}

            for element in elements:
                element_type = type(element).__name__
                element_counts[element_type] = element_counts.get(element_type, 0) + 1

                # Convert to Markdown based on element type
                if element_type == "Title":
                    md_parts.append(f"# {element.text}")
                elif element_type == "Header":
                    md_parts.append(f"## {element.text}")
                elif element_type == "ListItem":
                    md_parts.append(f"- {element.text}")
                elif element_type == "Table":
                    # Tables come as HTML, convert to Markdown
                    md_parts.append(self._table_to_markdown(element))
                else:
                    md_parts.append(element.text)

            md_text = "\n\n".join(md_parts)

            # Get page count from metadata
            page_count = 0
            if elements:
                page_nums = set()
                for elem in elements:
                    if hasattr(elem, "metadata") and hasattr(elem.metadata, "page_number"):
                        page_nums.add(elem.metadata.page_number)
                page_count = len(page_nums) if page_nums else 0

            duration_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                success=True,
                content_text=md_text,
                extraction_confidence=0.80,  # Moderate quality
                extractor_used=self.name,
                extraction_duration_ms=duration_ms,
                pages_extracted=page_count,
                metadata={
                    "strategy": self.strategy,
                    "element_counts": element_counts,
                    "total_elements": len(elements),
                },
                raw_output=elements,
            )

        except Exception as e:
            logger.error(f"Unstructured extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                extractor_used=self.name,
                extraction_duration_ms=(time.time() - start_time) * 1000,
            )

    def _table_to_markdown(self, table_element) -> str:
        """Convert table element to Markdown format."""
        try:
            if hasattr(table_element, "metadata") and hasattr(
                table_element.metadata, "text_as_html"
            ):
                html = table_element.metadata.text_as_html
                # Simple HTML table to Markdown conversion
                import re

                # Extract rows
                rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
                md_rows = []

                for i, row in enumerate(rows):
                    cells = re.findall(r"<t[dh]>(.*?)</t[dh]>", row, re.DOTALL)
                    cells = [c.strip() for c in cells]
                    md_rows.append("| " + " | ".join(cells) + " |")

                    # Add separator after header
                    if i == 0:
                        md_rows.append("|" + "---|" * len(cells))

                return "\n".join(md_rows)

            return table_element.text

        except Exception:
            return table_element.text if hasattr(table_element, "text") else ""

    async def convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to Markdown."""
        result = await self.extract(file_path)
        return result.content_text

    async def convert_to_text(self, file_path: Path) -> str:
        """Convert PDF to plain text."""
        if not self.available:
            return ""

        try:
            from unstructured.partition.pdf import partition_pdf

            elements = partition_pdf(
                filename=str(file_path),
                strategy=self.strategy,
            )

            return "\n\n".join(elem.text for elem in elements if hasattr(elem, "text"))

        except Exception as e:
            logger.error(f"Unstructured text extraction failed: {e}")
            return ""
