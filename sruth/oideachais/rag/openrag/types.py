"""
Core types for multimodal document processing.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    IMAGE = "image"
    HTML = "html"
    DOCX = "docx"
    PPTX = "pptx"
    MARKDOWN = "markdown"
    TEXT = "text"

    @classmethod
    def from_extension(cls, ext: str) -> "DocumentType":
        """Detect document type from file extension."""
        ext = ext.lower().lstrip(".")
        mapping = {
            "pdf": cls.PDF,
            "png": cls.IMAGE,
            "jpg": cls.IMAGE,
            "jpeg": cls.IMAGE,
            "gif": cls.IMAGE,
            "webp": cls.IMAGE,
            "html": cls.HTML,
            "htm": cls.HTML,
            "docx": cls.DOCX,
            "pptx": cls.PPTX,
            "md": cls.MARKDOWN,
            "txt": cls.TEXT,
        }
        return mapping.get(ext, cls.TEXT)


@dataclass
class ExtractedTable:
    """Table extracted from a document."""

    id: str
    content: str  # Markdown or HTML representation
    page_number: int | None = None
    caption: str | None = None
    rows: int = 0
    cols: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedImage:
    """Image extracted from a document."""

    id: str
    caption: str | None = None
    description: str | None = None  # AI-generated description
    page_number: int | None = None
    image_path: Path | None = None
    image_data: bytes | None = None
    mime_type: str = "image/png"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """A chunk of processed document content."""

    id: str
    content: str
    doc_id: str
    chunk_index: int
    page_number: int | None = None
    section: str | None = None
    tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    # References to extracted elements
    table_refs: list[str] = field(default_factory=list)
    image_refs: list[str] = field(default_factory=list)


@dataclass
class ProcessedDocument:
    """Result of document processing."""

    doc_id: str
    source: str  # Original file path or URL
    doc_type: DocumentType
    title: str | None = None

    # Content
    chunks: list[DocumentChunk] = field(default_factory=list)
    tables: list[ExtractedTable] = field(default_factory=list)
    images: list[ExtractedImage] = field(default_factory=list)

    # Metadata
    page_count: int = 0
    total_tokens: int = 0
    language: str = "en"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_tables(self) -> bool:
        """Check if document contains tables."""
        return len(self.tables) > 0

    @property
    def has_images(self) -> bool:
        """Check if document contains images."""
        return len(self.images) > 0

    @property
    def chunk_count(self) -> int:
        """Number of content chunks."""
        return len(self.chunks)

    def get_full_text(self) -> str:
        """Get concatenated text from all chunks."""
        return "\n\n".join(c.content for c in self.chunks)


@dataclass
class ProcessingConfig:
    """Configuration for document processing."""

    # Chunking
    chunk_size: int = 1200  # Target tokens per chunk
    chunk_overlap: int = 100

    # OCR
    enable_ocr: bool = True
    ocr_languages: list[str] = field(default_factory=lambda: ["en", "ga"])

    # Tables
    extract_tables: bool = True
    table_format: str = "markdown"  # markdown or html

    # Images
    extract_images: bool = True
    generate_captions: bool = True
    max_image_size: int = 1024  # Max dimension for processing

    # Language
    primary_language: str = "en"
    detect_language: bool = True

    # Performance
    batch_size: int = 10
    max_pages: int | None = None  # None = all pages
