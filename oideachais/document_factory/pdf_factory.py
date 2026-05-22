"""
Lazy-Loading PDF Factory.

Implements the pdfstract CLILazyFactory pattern for fast CLI startup
by deferring heavy imports until converters are actually needed.

Startup performance:
- pdfstract --help: <1s (no library loading)
- pdfstract convert file.pdf -l marker: 3-8s (loads only marker)
- First full library scan: 8-10s
"""
from __future__ import annotations

import importlib
import logging
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from .base import (
    DocumentConverter,
    DocumentFactory,
    DocumentFormat,
    DocumentSource,
    ExtractionResult,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Abstract PDF Converter
# =============================================================================

class PDFConverter(DocumentConverter):
    """
    Abstract base class for PDF converters.

    Extends DocumentConverter with PDF-specific methods.
    """

    @property
    def supported_formats(self) -> list[DocumentFormat]:
        """PDF converters support PDF format."""
        return [DocumentFormat.PDF]

    @abstractmethod
    async def convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to Markdown format."""
        pass

    @abstractmethod
    async def convert_to_text(self, file_path: Path) -> str:
        """Convert PDF to plain text."""
        pass


# =============================================================================
# Converter Registry
# =============================================================================

# Map of converter names to their module paths and class names
# This allows lazy loading - modules aren't imported until needed
CONVERTER_REGISTRY: dict[str, tuple[str, str]] = {
    "pymupdf4llm": (
        "oideachais.document_factory.converters.pymupdf4llm_converter",
        "PyMuPDF4LLMConverter",
    ),
    "marker": (
        "oideachais.document_factory.converters.marker_converter",
        "MarkerConverter",
    ),
    "docling": (
        "oideachais.document_factory.converters.docling_converter",
        "DoclingConverter",
    ),
    "deepseekocr": (
        "oideachais.document_factory.converters.deepseekocr_converter",
        "DeepSeekOCRConverter",
    ),
    "unstructured": (
        "oideachais.document_factory.converters.unstructured_converter",
        "UnstructuredConverter",
    ),
}

# Recommended converters by document source
RECOMMENDED_CONVERTERS: dict[DocumentSource, list[str]] = {
    DocumentSource.NCCA: ["docling", "marker", "pymupdf4llm"],
    DocumentSource.SEC: ["marker", "docling", "pymupdf4llm"],  # Exam papers need good layout
    DocumentSource.CIRCULAR: ["pymupdf4llm", "docling"],  # Simple text docs
    DocumentSource.TEXTBOOK: ["docling", "marker"],  # Complex layouts
    DocumentSource.RESOURCE: ["pymupdf4llm", "docling"],
    DocumentSource.UNKNOWN: ["pymupdf4llm", "marker", "docling"],
}


# =============================================================================
# Lazy PDF Factory
# =============================================================================

class LazyPDFFactory(DocumentFactory):
    """
    Lazy-loading PDF converter factory.

    Based on pdfstract CLILazyFactory pattern:
    - Converters are only loaded when first requested
    - Dynamic imports avoid loading unused heavy dependencies
    - Startup time <1s for CLI tools
    """

    def __init__(self):
        """Initialize factory without loading any converters."""
        self._converters: dict[str, PDFConverter] = {}
        self._availability_cache: dict[str, bool] = {}
        self._load_errors: dict[str, str] = {}

    def _load_converter(self, name: str) -> PDFConverter | None:
        """
        Lazy load a converter by name.

        Only imports the module when the converter is first requested.
        """
        # Return cached converter if already loaded
        if name in self._converters:
            return self._converters[name]

        # Skip if we already know it's not available
        if name in self._availability_cache and not self._availability_cache[name]:
            return None

        # Check registry
        if name not in CONVERTER_REGISTRY:
            logger.warning(f"Unknown converter: {name}")
            return None

        module_path, class_name = CONVERTER_REGISTRY[name]

        try:
            # Dynamic import - this is where the heavy loading happens
            logger.debug(f"Loading converter: {name}")
            module = importlib.import_module(module_path)
            converter_class = getattr(module, class_name)
            converter = converter_class()

            # Check availability
            if converter.available:
                self._converters[name] = converter
                self._availability_cache[name] = True
                logger.info(f"Loaded converter: {name}")
                return converter
            else:
                self._availability_cache[name] = False
                logger.debug(f"Converter not available: {name}")
                return None

        except ImportError as e:
            self._availability_cache[name] = False
            self._load_errors[name] = str(e)
            logger.debug(f"Failed to import converter {name}: {e}")
            return None

        except Exception as e:
            self._availability_cache[name] = False
            self._load_errors[name] = str(e)
            logger.error(f"Error loading converter {name}: {e}")
            return None

    def get_converter(self, name: str) -> PDFConverter | None:
        """
        Get a converter by name.

        Lazy loads the converter if not already loaded.
        """
        return self._load_converter(name)

    def list_converters(self) -> list[str]:
        """List all registered converter names."""
        return list(CONVERTER_REGISTRY.keys())

    def list_available_converters(self) -> list[str]:
        """
        List converters that are available (dependencies installed).

        Note: This triggers loading of all converters.
        """
        available = []
        for name in CONVERTER_REGISTRY:
            converter = self._load_converter(name)
            if converter is not None:
                available.append(name)
        return available

    def get_best_converter(
        self,
        file_path: Path,
        document_source: DocumentSource = DocumentSource.UNKNOWN,
    ) -> PDFConverter | None:
        """
        Get the best available converter for a document.

        Selection based on:
        1. Document source (NCCA, SEC, etc.)
        2. Availability of recommended converters
        3. Fallback to any available converter
        """
        # Get recommended converters for this source
        recommended = RECOMMENDED_CONVERTERS.get(
            document_source,
            RECOMMENDED_CONVERTERS[DocumentSource.UNKNOWN],
        )

        # Try each recommended converter in order
        for name in recommended:
            converter = self._load_converter(name)
            if converter is not None:
                logger.debug(f"Selected converter: {name} for {document_source.value}")
                return converter

        # Fallback: try any available converter
        for name in CONVERTER_REGISTRY:
            if name not in recommended:
                converter = self._load_converter(name)
                if converter is not None:
                    logger.debug(f"Fallback converter: {name}")
                    return converter

        logger.error("No PDF converters available")
        return None

    def get_load_errors(self) -> dict[str, str]:
        """Get any errors that occurred while loading converters."""
        return self._load_errors.copy()

    async def extract(
        self,
        file_path: Path,
        converter_name: str | None = None,
        document_source: DocumentSource = DocumentSource.UNKNOWN,
    ) -> ExtractionResult:
        """
        Extract content from a PDF file.

        Args:
            file_path: Path to PDF file
            converter_name: Optional specific converter to use
            document_source: Document source for converter selection

        Returns:
            ExtractionResult with extracted content
        """
        import time

        start_time = time.time()

        # Get converter
        if converter_name:
            converter = self.get_converter(converter_name)
            if converter is None:
                return ExtractionResult(
                    success=False,
                    error_message=f"Converter not available: {converter_name}",
                )
        else:
            converter = self.get_best_converter(file_path, document_source)
            if converter is None:
                return ExtractionResult(
                    success=False,
                    error_message="No PDF converters available",
                )

        # Extract
        try:
            result = await converter.extract(file_path)
            result.extractor_used = converter.name
            result.extraction_duration_ms = (time.time() - start_time) * 1000
            return result

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                extractor_used=converter.name,
                extraction_duration_ms=(time.time() - start_time) * 1000,
            )

    async def compare_extractors(
        self,
        file_path: Path,
        converters: list[str] | None = None,
    ) -> dict[str, ExtractionResult]:
        """
        Run multiple extractors on a file for comparison.

        Args:
            file_path: Path to PDF file
            converters: List of converter names (default: all available)

        Returns:
            Dict mapping converter names to their results
        """
        if converters is None:
            converters = self.list_available_converters()

        results = {}
        for name in converters:
            result = await self.extract(file_path, converter_name=name)
            results[name] = result

        return results


# =============================================================================
# Singleton Factory
# =============================================================================

_pdf_factory: LazyPDFFactory | None = None


def get_pdf_factory() -> LazyPDFFactory:
    """Get the singleton PDF factory instance."""
    global _pdf_factory
    if _pdf_factory is None:
        _pdf_factory = LazyPDFFactory()
    return _pdf_factory


# =============================================================================
# Convenience Functions
# =============================================================================

async def extract_pdf(
    file_path: Path,
    converter: str | None = None,
    document_source: DocumentSource = DocumentSource.UNKNOWN,
) -> ExtractionResult:
    """
    Convenience function to extract PDF content.

    Args:
        file_path: Path to PDF file
        converter: Optional specific converter name
        document_source: Document source for converter selection

    Returns:
        ExtractionResult with extracted content
    """
    factory = get_pdf_factory()
    return await factory.extract(file_path, converter, document_source)


def list_pdf_converters() -> list[str]:
    """List all registered PDF converter names."""
    factory = get_pdf_factory()
    return factory.list_converters()


def list_available_pdf_converters() -> list[str]:
    """List PDF converters that are available."""
    factory = get_pdf_factory()
    return factory.list_available_converters()
