"""
Multimodal document processing components.

Handles PDF conversion, image processing, table extraction,
and OCR using Docling and vision models.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

from .types import (
    DocumentType,
    ExtractedImage,
    ExtractedTable,
    ProcessingConfig,
)

logger = logging.getLogger(__name__)


class DocumentConverter:
    """
    Convert documents to structured content using Docling.

    Supports PDF, DOCX, PPTX, HTML with:
    - OCR for scanned documents
    - Table structure recognition
    - Image extraction
    """

    def __init__(self, config: ProcessingConfig | None = None):
        self.config = config or ProcessingConfig()
        self._converter = None
        self._initialized = False

    async def _ensure_initialized(self) -> bool:
        """Lazy initialization of Docling converter."""
        if self._initialized:
            return self._converter is not None

        try:
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter as DoclingConverter

            # Configure pipeline
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = self.config.enable_ocr
            pipeline_options.do_table_structure = self.config.extract_tables
            pipeline_options.generate_page_images = self.config.extract_images

            self._converter = DoclingConverter(
                allowed_formats=[
                    "pdf",
                    "docx",
                    "pptx",
                    "html",
                    "image",
                ],
                pdf_pipeline_options=pipeline_options,
            )
            self._initialized = True
            logger.info("Docling converter initialized")
            return True

        except ImportError:
            logger.warning("Docling not available, using fallback text extraction")
            self._initialized = True
            return False

    async def convert(
        self,
        source: str | Path,
        doc_type: DocumentType | None = None,
    ) -> dict[str, Any]:
        """
        Convert a document to structured content.

        Args:
            source: File path or URL
            doc_type: Document type (auto-detected if not provided)

        Returns:
            Dict with text, tables, images, and metadata
        """
        source_path = Path(source) if isinstance(source, str) else source

        # Detect document type
        if doc_type is None:
            doc_type = DocumentType.from_extension(source_path.suffix)

        # Try Docling first
        if await self._ensure_initialized() and self._converter:
            return await self._convert_with_docling(source_path, doc_type)

        # Fallback to basic extraction
        return await self._fallback_convert(source_path, doc_type)

    async def _convert_with_docling(
        self,
        source_path: Path,
        doc_type: DocumentType,
    ) -> dict[str, Any]:
        """Convert using Docling."""
        try:
            result = self._converter.convert(str(source_path))

            # Extract text content
            text_content = result.document.export_to_markdown()

            # Extract tables
            tables = []
            for idx, table in enumerate(result.document.tables):
                table_id = hashlib.md5(
                    f"{source_path.name}:table:{idx}".encode()
                ).hexdigest()[:12]

                tables.append({
                    "id": table_id,
                    "content": table.export_to_markdown(),
                    "page": getattr(table, "page_no", None),
                    "rows": len(table.data) if hasattr(table, "data") else 0,
                    "cols": len(table.data[0]) if hasattr(table, "data") and table.data else 0,
                })

            # Extract images
            images = []
            for idx, image in enumerate(result.document.pictures):
                image_id = hashlib.md5(
                    f"{source_path.name}:image:{idx}".encode()
                ).hexdigest()[:12]

                images.append({
                    "id": image_id,
                    "page": getattr(image, "page_no", None),
                    "caption": getattr(image, "caption", None),
                    "data": getattr(image, "image", None),
                })

            return {
                "text": text_content,
                "tables": tables,
                "images": images,
                "page_count": len(result.document.pages) if hasattr(result.document, "pages") else 1,
                "metadata": {
                    "converter": "docling",
                    "doc_type": doc_type.value,
                    "source": str(source_path),
                },
            }

        except Exception as e:
            logger.error(f"Docling conversion failed: {e}")
            return await self._fallback_convert(source_path, doc_type)

    async def _fallback_convert(
        self,
        source_path: Path,
        doc_type: DocumentType,
    ) -> dict[str, Any]:
        """Fallback text extraction without Docling."""
        text = ""

        if doc_type == DocumentType.TEXT:
            text = source_path.read_text(encoding="utf-8", errors="ignore")

        elif doc_type == DocumentType.MARKDOWN:
            text = source_path.read_text(encoding="utf-8", errors="ignore")

        elif doc_type == DocumentType.PDF:
            # Try PyMuPDF as fallback
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(str(source_path))
                pages = []
                for page in doc:
                    pages.append(page.get_text())
                text = "\n\n".join(pages)
                doc.close()
            except ImportError:
                logger.warning("PyMuPDF not available for PDF fallback")
                text = f"[PDF content from {source_path.name}]"

        elif doc_type == DocumentType.HTML:
            try:
                from bs4 import BeautifulSoup

                html = source_path.read_text(encoding="utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator="\n")
            except ImportError:
                text = source_path.read_text(encoding="utf-8", errors="ignore")

        return {
            "text": text,
            "tables": [],
            "images": [],
            "page_count": 1,
            "metadata": {
                "converter": "fallback",
                "doc_type": doc_type.value,
                "source": str(source_path),
            },
        }


class ImageProcessor:
    """
    Process images with vision models for captioning and description.

    Supports:
    - Image captioning using vision LLMs
    - OCR for text in images
    - Curriculum-specific image analysis
    """

    def __init__(self, config: ProcessingConfig | None = None):
        self.config = config or ProcessingConfig()
        self._llm_router = None

    async def _get_llm_router(self):
        """Get LLM router for vision processing."""
        if self._llm_router is None:
            try:
                from browser.core.llm_router import get_llm_router
                self._llm_router = await get_llm_router()
            except ImportError:
                logger.warning("LLM router not available for image processing")
                return None
        return self._llm_router

    async def generate_caption(
        self,
        image_data: bytes | str | Path,
        context: str | None = None,
    ) -> str | None:
        """
        Generate a caption for an image using vision model.

        Args:
            image_data: Image bytes, base64 string, or file path
            context: Optional context about the document

        Returns:
            Generated caption or None if unavailable
        """
        router = await self._get_llm_router()
        if router is None:
            return None

        # Prepare image for API
        image_content = await self._prepare_image(image_data)
        if image_content is None:
            return None

        # Build prompt
        system_prompt = (
            "You are an expert at describing educational images, diagrams, and figures. "
            "Provide a clear, concise description that captures the key information "
            "presented in the image. Focus on educational content and meaning."
        )

        user_prompt = "Describe this image in detail, focusing on its educational content."
        if context:
            user_prompt += f"\n\nContext: {context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_content,
                        },
                    },
                ],
            },
        ]

        try:
            response = await router.complete(
                messages,
                max_tokens=500,
                temperature=0.3,
            )

            if response.success:
                return response.content
            else:
                logger.warning(f"Image captioning failed: {response.error}")
                return None

        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return None

    async def _prepare_image(
        self,
        image_data: bytes | str | Path,
    ) -> str | None:
        """Prepare image data as base64 for API."""
        import base64

        try:
            if isinstance(image_data, bytes):
                return base64.b64encode(image_data).decode("utf-8")

            elif isinstance(image_data, Path):
                with open(image_data, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")

            elif isinstance(image_data, str):
                # Check if already base64
                if image_data.startswith("data:"):
                    # Extract base64 from data URI
                    return image_data.split(",", 1)[1]
                elif len(image_data) > 200 and "/" not in image_data[:50]:
                    # Likely base64 string
                    return image_data
                else:
                    # File path
                    with open(image_data, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")

            return None

        except Exception as e:
            logger.error(f"Image preparation failed: {e}")
            return None

    async def process_extracted_image(
        self,
        image: dict[str, Any],
        doc_context: str | None = None,
    ) -> ExtractedImage:
        """
        Process an extracted image and generate description.

        Args:
            image: Raw image data from converter
            doc_context: Context from the source document

        Returns:
            ExtractedImage with description
        """
        image_id = image.get("id", "")
        caption = image.get("caption")
        image_data = image.get("data")

        description = None
        if self.config.generate_captions and image_data:
            description = await self.generate_caption(image_data, doc_context)

        return ExtractedImage(
            id=image_id,
            caption=caption,
            description=description,
            page_number=image.get("page"),
            image_data=image_data if isinstance(image_data, bytes) else None,
        )


class TableExtractor:
    """
    Extract and process tables from documents.

    Supports:
    - Markdown and HTML table formats
    - Table structure recognition
    - Curriculum data extraction (grades, subjects, etc.)
    """

    def __init__(self, config: ProcessingConfig | None = None):
        self.config = config or ProcessingConfig()

    def process_extracted_table(
        self,
        table: dict[str, Any],
    ) -> ExtractedTable:
        """
        Process an extracted table.

        Args:
            table: Raw table data from converter

        Returns:
            ExtractedTable with metadata
        """
        return ExtractedTable(
            id=table.get("id", ""),
            content=table.get("content", ""),
            page_number=table.get("page"),
            rows=table.get("rows", 0),
            cols=table.get("cols", 0),
            metadata=table.get("metadata", {}),
        )

    def tables_to_text(
        self,
        tables: list[ExtractedTable],
        include_metadata: bool = True,
    ) -> str:
        """
        Convert tables to text representation for RAG.

        Args:
            tables: List of extracted tables
            include_metadata: Include table metadata in output

        Returns:
            Text representation of tables
        """
        parts = []

        for i, table in enumerate(tables):
            header = f"Table {i + 1}"
            if table.caption:
                header += f": {table.caption}"
            if include_metadata and table.page_number:
                header += f" (Page {table.page_number})"

            parts.append(f"### {header}\n\n{table.content}")

        return "\n\n".join(parts)


# Singleton instance
_converter: DocumentConverter | None = None


async def get_document_converter(
    config: ProcessingConfig | None = None,
) -> DocumentConverter:
    """
    Get or create document converter singleton.

    Args:
        config: Processing configuration

    Returns:
        DocumentConverter instance
    """
    global _converter

    if _converter is None:
        _converter = DocumentConverter(config)

    return _converter
