"""
DeepSeek OCR Converter.

VLM-based OCR using DeepSeek models for challenging documents.
Best for scanned documents with Irish text.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from ..base import ExtractionResult
from ..pdf_factory import PDFConverter

logger = logging.getLogger(__name__)


class DeepSeekOCRConverter(PDFConverter):
    """
    PDF converter using DeepSeek VLM for OCR.

    Characteristics:
    - VLM-based understanding
    - Excellent for scanned documents
    - Good Irish text recognition
    - Requires API key or local model
    """

    def __init__(
        self,
        model_name: str = "deepseek-vl2",
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize converter.

        Args:
            model_name: DeepSeek model to use
            api_base: API endpoint (optional, for remote inference)
            api_key: API key (optional, for remote inference)
        """
        self._available: Optional[bool] = None
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "deepseekocr"

    @property
    def available(self) -> bool:
        """Check if required libraries are installed."""
        if self._available is None:
            try:
                import fitz  # PyMuPDF for page rendering

                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def extract(self, file_path: Path) -> ExtractionResult:
        """Extract content from PDF using DeepSeek VLM."""
        import time

        start_time = time.time()

        if not self.available:
            return ExtractionResult(
                success=False,
                error_message="Required libraries not installed",
            )

        try:
            import fitz
            import base64
            from io import BytesIO

            # Open PDF and render pages
            doc = fitz.open(str(file_path))
            page_texts = []

            for page_num, page in enumerate(doc):
                # Render page to image
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                img_b64 = base64.b64encode(img_bytes).decode()

                # Call VLM for OCR
                page_text = await self._ocr_page(img_b64, page_num + 1)
                page_texts.append(page_text)

            page_count = len(doc)
            doc.close()

            # Combine all pages
            full_text = "\n\n---\n\n".join(page_texts)

            duration_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                success=True,
                content_text=full_text,
                extraction_confidence=0.88,  # VLM-based, good for scans
                extractor_used=self.name,
                extraction_duration_ms=duration_ms,
                pages_extracted=page_count,
                metadata={
                    "model": self.model_name,
                    "method": "vlm_ocr",
                },
            )

        except Exception as e:
            logger.error(f"DeepSeek OCR extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                extractor_used=self.name,
                extraction_duration_ms=(time.time() - start_time) * 1000,
            )

    async def _ocr_page(self, img_b64: str, page_num: int) -> str:
        """OCR a single page using DeepSeek VLM."""
        try:
            import litellm

            # Use LiteLLM for unified API access
            response = await litellm.acompletion(
                model=f"deepseek/{self.model_name}",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract all text from this document page. "
                                    "Preserve the structure and formatting. "
                                    "This may contain Irish language text - preserve fadas (á, é, í, ó, ú) correctly. "
                                    "Output the text in Markdown format."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_b64}",
                                },
                            },
                        ],
                    }
                ],
                api_base=self.api_base,
                api_key=self.api_key,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            logger.warning(f"VLM OCR failed for page {page_num}: {e}")
            return f"[OCR failed for page {page_num}]"

    async def convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to Markdown."""
        result = await self.extract(file_path)
        return result.content_text

    async def convert_to_text(self, file_path: Path) -> str:
        """Convert PDF to plain text."""
        result = await self.extract(file_path)
        import re

        text = result.content_text
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*+([^*]+)\*+", r"\1", text)
        return text
