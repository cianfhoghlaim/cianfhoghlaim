"""
Base classes for document factory.

Provides abstract interfaces for document conversion and extraction,
following historical-document-analysis patterns.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class DocumentSource(StrEnum):
    """Curriculum document source types."""

    NCCA = "ncca"  # curriculumonline.ie
    SEC = "sec"  # examinations.ie
    CIRCULAR = "circular"  # Department of Education
    TEXTBOOK = "textbook"  # Publisher content
    RESOURCE = "resource"  # Teacher resources
    UNKNOWN = "unknown"


class DocumentFormat(StrEnum):
    """Document file formats."""

    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    PPTX = "pptx"
    XML = "xml"
    JSON = "json"
    MARKDOWN = "md"
    TEXT = "txt"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """Result of document extraction."""

    success: bool
    content_text: str = ""
    content_html: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Quality metrics
    extraction_confidence: float = 0.0
    extractor_used: str = ""
    extraction_duration_ms: float = 0.0

    # Error information
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)

    # Raw extraction data
    raw_output: Any | None = None
    pages_extracted: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "content_length": len(self.content_text),
            "has_html": self.content_html is not None,
            "extraction_confidence": self.extraction_confidence,
            "extractor_used": self.extractor_used,
            "extraction_duration_ms": self.extraction_duration_ms,
            "pages_extracted": self.pages_extracted,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class DocumentConverter(ABC):
    """
    Abstract base class for document converters.

    Implements the Strategy pattern for pluggable extraction backends.
    Each converter handles a specific extraction library (Marker, Docling, etc.)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this converter."""
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if the converter's dependencies are available."""
        pass

    @property
    def supported_formats(self) -> list[DocumentFormat]:
        """Return list of supported input formats."""
        return [DocumentFormat.PDF]

    @abstractmethod
    async def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extract content from a document.

        Args:
            file_path: Path to the document file

        Returns:
            ExtractionResult with content and metadata
        """
        pass

    async def extract_to_markdown(self, file_path: Path) -> str:
        """
        Extract content as Markdown.

        Default implementation extracts and returns content_text.
        Override for converters with native Markdown output.
        """
        result = await self.extract(file_path)
        return result.content_text

    async def extract_to_json(self, file_path: Path) -> dict[str, Any]:
        """
        Extract content as structured JSON.

        Default implementation returns extraction result as dict.
        Override for converters with native structured output.
        """
        result = await self.extract(file_path)
        return result.to_dict()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, available={self.available})"


class DocumentFactory(ABC):
    """
    Abstract factory for creating document converters.

    Implements the Abstract Factory pattern for managing
    multiple extraction backends.
    """

    @abstractmethod
    def get_converter(self, name: str) -> DocumentConverter | None:
        """Get a converter by name."""
        pass

    @abstractmethod
    def list_converters(self) -> list[str]:
        """List available converter names."""
        pass

    @abstractmethod
    def get_best_converter(
        self,
        file_path: Path,
        document_source: DocumentSource = DocumentSource.UNKNOWN,
    ) -> DocumentConverter | None:
        """
        Get the best converter for a document.

        Selection based on:
        - Document format
        - Document source (NCCA, SEC, etc.)
        - Historical extraction quality metrics
        """
        pass


@dataclass
class ConversionTask:
    """A document conversion task for tracking."""

    task_id: str
    file_path: Path
    file_size_bytes: int
    document_source: DocumentSource
    document_format: DocumentFormat

    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    status: str = "pending"  # pending, running, completed, failed
    selected_converter: str | None = None

    # Results
    extraction_result: ExtractionResult | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Calculate task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "task_id": self.task_id,
            "file_path": str(self.file_path),
            "file_size_bytes": self.file_size_bytes,
            "document_source": self.document_source.value,
            "document_format": self.document_format.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "selected_converter": self.selected_converter,
            "duration_seconds": self.duration_seconds,
        }


# =============================================================================
# Utility Functions
# =============================================================================

def detect_format(file_path: Path) -> DocumentFormat:
    """Detect document format from file extension."""
    suffix = file_path.suffix.lower()

    format_map = {
        ".pdf": DocumentFormat.PDF,
        ".html": DocumentFormat.HTML,
        ".htm": DocumentFormat.HTML,
        ".docx": DocumentFormat.DOCX,
        ".doc": DocumentFormat.DOCX,
        ".pptx": DocumentFormat.PPTX,
        ".ppt": DocumentFormat.PPTX,
        ".xml": DocumentFormat.XML,
        ".json": DocumentFormat.JSON,
        ".md": DocumentFormat.MARKDOWN,
        ".markdown": DocumentFormat.MARKDOWN,
        ".txt": DocumentFormat.TEXT,
    }

    return format_map.get(suffix, DocumentFormat.UNKNOWN)


def generate_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"task_{timestamp}_{short_uuid}"
