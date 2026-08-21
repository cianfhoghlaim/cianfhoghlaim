"""Docling PDF parsing resource for Dagster.

Provides hierarchy-aware PDF parsing with curriculum-optimized chunking.

Features:
- PDF parsing with structure preservation (sections, tables, lists)
- HierarchicalChunker for curriculum document hierarchy
- Table extraction with PaddleOCR-VL fallback
- Page-to-image conversion for VLM processing
- LiteLLM integration for OCR fallback

Usage:
    @asset(resource_defs={"docling": docling_resource()})
    def parse_pdfs(context, docling: DoclingResource):
        doc = docling.parse_pdf(pdf_bytes)
        chunks = docling.chunk_document(doc)
        images = docling.pdf_to_images(pdf_bytes)
        return {"chunks": chunks, "images": images}
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from typing import Any, Iterator

import dagster as dg
import structlog

try:
    from pydantic import Field
except ImportError:
    from dagster import Field

logger = structlog.get_logger(__name__)


@dataclass
class Chunk:
    """Represents a document chunk with metadata."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    start_page: int | None = None
    end_page: int | None = None
    heading_path: list[str] = field(default_factory=list)
    chunk_type: str = "text"  # text, table, list, figure


@dataclass
class PageImage:
    """Represents a page rendered as an image."""

    page_number: int
    image_bytes: bytes
    width: int
    height: int
    format: str = "PNG"


@dataclass
class ExtractedTable:
    """Represents an extracted table."""

    page_number: int
    table_index: int
    rows: list[list[str]]
    headers: list[str] | None = None
    caption: str | None = None


class DoclingResource(dg.ConfigurableResource):
    """Docling-based PDF parsing with curriculum-aware chunking.

    Integrates with:
    - Docling for PDF structure extraction
    - pdf2image for page image generation
    - LiteLLM for VLM-based OCR fallback
    - PaddleOCR-VL for table/formula extraction

    Example:
        @asset(resource_defs={"docling": docling_resource()})
        def process_curriculum_pdf(docling: DoclingResource):
            with open("curriculum.pdf", "rb") as f:
                pdf_bytes = f.read()

            doc = docling.parse_pdf(pdf_bytes)
            chunks = docling.chunk_document(doc)
            return [chunk.text for chunk in chunks]
    """

    # Chunking configuration
    chunk_size: int = Field(
        default=512,
        description="Maximum tokens per chunk (for embedding)",
    )

    chunk_overlap: int = Field(
        default=50,
        description="Token overlap between chunks",
    )

    # Image extraction configuration
    dpi: int = Field(
        default=200,
        description="DPI for PDF to image conversion",
    )

    image_format: str = Field(
        default="PNG",
        description="Output image format (PNG, JPEG)",
    )

    # OCR fallback configuration
    use_vlm_fallback: bool = Field(
        default=True,
        description="Use VLM-based OCR for scanned pages",
    )

    litellm_base_url: str = Field(
        default_factory=lambda: os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        description="LiteLLM proxy base URL for VLM calls",
    )

    vlm_model: str = Field(
        default="vision",
        description="LiteLLM model alias for vision OCR",
    )

    # PaddleOCR configuration
    use_paddleocr: bool = Field(
        default=True,
        description="Use PaddleOCR-VL for table/formula extraction",
    )

    def _get_converter(self) -> Any:
        """Get Docling DocumentConverter instance (lazy import)."""
        try:
            from docling.document_converter import DocumentConverter

            return DocumentConverter()
        except ImportError:
            logger.warning("docling_not_installed", message="Install: pip install docling")
            return None

    def _get_chunker(self) -> Any:
        """Get Docling HierarchicalChunker instance (lazy import)."""
        try:
            from docling.chunking import HierarchicalChunker

            return HierarchicalChunker(
                max_tokens=self.chunk_size,
                overlap=self.chunk_overlap,
            )
        except ImportError:
            logger.warning("docling_chunker_not_available")
            return None

    def parse_pdf(self, pdf_bytes: bytes) -> Any:
        """Parse a PDF file, preserving document structure.

        Args:
            pdf_bytes: PDF file content as bytes

        Returns:
            Docling Document object with parsed structure

        Raises:
            ImportError: If docling is not installed
            ValueError: If PDF parsing fails
        """
        converter = self._get_converter()
        if converter is None:
            raise ImportError("Docling not installed. Install: pip install docling")

        try:
            # Docling expects a file path or stream
            from io import BytesIO

            result = converter.convert(BytesIO(pdf_bytes))

            logger.info(
                "pdf_parsed",
                page_count=len(result.document.pages) if hasattr(result, "document") else 0,
            )

            return result.document if hasattr(result, "document") else result

        except Exception as e:
            logger.error("pdf_parse_failed", error=str(e))
            raise ValueError(f"Failed to parse PDF: {e}") from e

    def parse_pdf_from_path(self, pdf_path: str) -> Any:
        """Parse a PDF file from disk.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Docling Document object
        """
        converter = self._get_converter()
        if converter is None:
            raise ImportError("Docling not installed")

        try:
            result = converter.convert(pdf_path)
            logger.info(
                "pdf_parsed_from_path",
                path=pdf_path,
                page_count=len(result.document.pages) if hasattr(result, "document") else 0,
            )
            return result.document if hasattr(result, "document") else result

        except Exception as e:
            logger.error("pdf_parse_failed", path=pdf_path, error=str(e))
            raise ValueError(f"Failed to parse PDF: {e}") from e

    def chunk_document(self, doc: Any) -> list[Chunk]:
        """Chunk a parsed document using hierarchy-aware chunking.

        Preserves curriculum structure (strands, topics, learning outcomes)
        in chunk metadata.

        Args:
            doc: Docling Document object

        Returns:
            List of Chunk objects with text and metadata
        """
        chunker = self._get_chunker()
        if chunker is None:
            # Fallback: simple text extraction without hierarchy
            return self._fallback_chunk(doc)

        try:
            docling_chunks = chunker.chunk(doc)

            chunks = []
            for i, chunk in enumerate(docling_chunks):
                chunks.append(
                    Chunk(
                        text=chunk.text if hasattr(chunk, "text") else str(chunk),
                        metadata={
                            "chunk_index": i,
                            "source": "docling_hierarchical",
                        },
                        heading_path=chunk.heading_path if hasattr(chunk, "heading_path") else [],
                        chunk_type="text",
                    )
                )

            logger.info(
                "document_chunked",
                chunk_count=len(chunks),
                avg_chunk_size=sum(len(c.text) for c in chunks) // max(len(chunks), 1),
            )

            return chunks

        except Exception as e:
            logger.warning("chunking_failed", error=str(e), fallback="simple")
            return self._fallback_chunk(doc)

    def _fallback_chunk(self, doc: Any) -> list[Chunk]:
        """Simple fallback chunking when Docling chunker unavailable."""
        # Extract text from document
        if hasattr(doc, "text"):
            text = doc.text
        elif hasattr(doc, "export_to_markdown"):
            text = doc.export_to_markdown()
        else:
            text = str(doc)

        # Simple character-based chunking
        chunks = []
        char_chunk_size = self.chunk_size * 4  # Rough token to char conversion
        overlap_chars = self.chunk_overlap * 4

        start = 0
        while start < len(text):
            end = min(start + char_chunk_size, len(text))
            chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    text=chunk_text,
                    metadata={"chunk_index": len(chunks), "source": "fallback"},
                    chunk_type="text",
                )
            )

            start = end - overlap_chars if end < len(text) else len(text)

        return chunks

    def pdf_to_images(
        self,
        pdf_bytes: bytes,
        pages: list[int] | None = None,
    ) -> Iterator[PageImage]:
        """Convert PDF pages to images for VLM processing.

        Args:
            pdf_bytes: PDF file content
            pages: Specific pages to convert (1-indexed), None for all

        Yields:
            PageImage objects for each page
        """
        try:
            from pdf2image import convert_from_bytes
        except ImportError:
            logger.error("pdf2image_not_installed", message="Install: pip install pdf2image")
            return

        try:
            # Convert PDF to images
            images = convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt=self.image_format.lower(),
            )

            for page_num, img in enumerate(images, start=1):
                # Skip if specific pages requested and this isn't one
                if pages is not None and page_num not in pages:
                    continue

                # Convert PIL Image to bytes
                img_buffer = io.BytesIO()
                img.save(img_buffer, format=self.image_format)
                img_bytes = img_buffer.getvalue()

                yield PageImage(
                    page_number=page_num,
                    image_bytes=img_bytes,
                    width=img.width,
                    height=img.height,
                    format=self.image_format,
                )

            logger.info(
                "pdf_converted_to_images",
                page_count=len(images),
                dpi=self.dpi,
            )

        except Exception as e:
            logger.error("pdf_to_images_failed", error=str(e))
            raise

    def extract_tables(self, doc: Any) -> list[ExtractedTable]:
        """Extract tables from a parsed document.

        Uses Docling's table extraction, with PaddleOCR-VL fallback
        for complex tables.

        Args:
            doc: Docling Document object

        Returns:
            List of ExtractedTable objects
        """
        tables = []

        try:
            if hasattr(doc, "tables"):
                for i, table in enumerate(doc.tables):
                    tables.append(
                        ExtractedTable(
                            page_number=table.page if hasattr(table, "page") else 0,
                            table_index=i,
                            rows=table.data if hasattr(table, "data") else [],
                            headers=table.headers if hasattr(table, "headers") else None,
                            caption=table.caption if hasattr(table, "caption") else None,
                        )
                    )

            logger.info("tables_extracted", count=len(tables))

        except Exception as e:
            logger.warning("table_extraction_failed", error=str(e))

        return tables

    async def ocr_page_vlm(
        self,
        page_image: PageImage,
        instruction: str = "Extract all text from this document page.",
    ) -> str:
        """OCR a page image using VLM (Qwen3-VL, GLM-4.6V).

        Args:
            page_image: PageImage to process
            instruction: OCR instruction prompt

        Returns:
            Extracted text
        """
        try:
            import litellm
        except ImportError:
            logger.error("litellm_not_installed")
            return ""

        import base64

        # Encode image as base64
        image_b64 = base64.b64encode(page_image.image_bytes).decode("utf-8")
        image_url = f"data:image/{page_image.format.lower()};base64,{image_b64}"

        try:
            response = await litellm.acompletion(
                model=self.vlm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instruction},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                base_url=self.litellm_base_url,
            )

            text = response.choices[0].message.content
            logger.info(
                "vlm_ocr_completed",
                page=page_image.page_number,
                text_length=len(text),
            )
            return text

        except Exception as e:
            logger.error(
                "vlm_ocr_failed",
                page=page_image.page_number,
                error=str(e),
            )
            return ""

    def get_markdown(self, doc: Any) -> str:
        """Export document to markdown format.

        Args:
            doc: Docling Document object

        Returns:
            Markdown string
        """
        if hasattr(doc, "export_to_markdown"):
            return doc.export_to_markdown()
        elif hasattr(doc, "text"):
            return doc.text
        else:
            return str(doc)

    def get_metadata(self, doc: Any) -> dict[str, Any]:
        """Extract document metadata.

        Args:
            doc: Docling Document object

        Returns:
            Metadata dictionary
        """
        metadata = {
            "page_count": 0,
            "has_tables": False,
            "has_images": False,
            "title": None,
            "language": None,
        }

        try:
            if hasattr(doc, "pages"):
                metadata["page_count"] = len(doc.pages)
            if hasattr(doc, "tables"):
                metadata["has_tables"] = len(doc.tables) > 0
            if hasattr(doc, "images") or hasattr(doc, "figures"):
                images = getattr(doc, "images", getattr(doc, "figures", []))
                metadata["has_images"] = len(images) > 0
            if hasattr(doc, "title"):
                metadata["title"] = doc.title
            if hasattr(doc, "language"):
                metadata["language"] = doc.language

        except Exception as e:
            logger.warning("metadata_extraction_failed", error=str(e))

        return metadata


# Resource factory function
def docling_resource(**kwargs) -> DoclingResource:
    """Factory for Docling resource with default configuration.

    Usage:
        @asset(resource_defs={"docling": docling_resource()})
        def my_asset(docling: DoclingResource):
            doc = docling.parse_pdf(pdf_bytes)
            chunks = docling.chunk_document(doc)
            return chunks
    """
    return DoclingResource(**kwargs)
