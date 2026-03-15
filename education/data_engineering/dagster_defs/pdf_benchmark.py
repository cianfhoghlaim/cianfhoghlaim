"""
PDFStract-style PDF Extraction Benchmarking Dagster Asset.

Benchmarks multiple PDF extraction libraries for Irish curriculum documents:
- PyMuPDF4LLM: Fast, basic extraction
- Marker: ML-based, good for complex layouts
- Docling: IBM's document understanding
- Unstructured: Schema-based extraction

Based on pdfstract patterns from /taighde/teanga/pdfstract/.

Usage:
    from dagster_assets.pdf_benchmark import pdf_extraction_benchmark

    @job
    def benchmark_extractors():
        pdf_extraction_benchmark()
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats."""

    MARKDOWN = "markdown"
    JSON = "json"
    TEXT = "text"
    HTML = "html"


@dataclass
class PDFBenchmarkResult:
    """Result of benchmarking a single PDF with one extractor."""

    pdf_path: str
    extractor: str
    output_format: OutputFormat
    content: str
    extraction_time_ms: float
    page_count: int
    char_count: int
    word_count: int
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def chars_per_second(self) -> float:
        """Calculate characters extracted per second."""
        if self.extraction_time_ms <= 0:
            return 0.0
        return self.char_count / (self.extraction_time_ms / 1000)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pdf_path": self.pdf_path,
            "extractor": self.extractor,
            "output_format": self.output_format.value,
            "extraction_time_ms": self.extraction_time_ms,
            "page_count": self.page_count,
            "char_count": self.char_count,
            "word_count": self.word_count,
            "chars_per_second": self.chars_per_second,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class PDFExtractor(ABC):
    """Abstract base class for PDF extractors (pdfstract pattern)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the extractor library."""
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if the extractor is available/installed."""
        pass

    @abstractmethod
    async def extract_to_md(self, file_path: str) -> str:
        """Extract PDF to Markdown."""
        pass

    @abstractmethod
    async def extract_to_text(self, file_path: str) -> str:
        """Extract PDF to plain text."""
        pass

    def supports_format(self, format_type: OutputFormat) -> bool:
        """Check if extractor supports a specific output format."""
        return format_type in [OutputFormat.MARKDOWN, OutputFormat.TEXT]


class PyMuPDF4LLMExtractor(PDFExtractor):
    """PyMuPDF4LLM-based PDF extractor."""

    @property
    def name(self) -> str:
        return "pymupdf4llm"

    @property
    def available(self) -> bool:
        try:
            import pymupdf4llm
            return True
        except ImportError:
            return False

    async def extract_to_md(self, file_path: str) -> str:
        import pymupdf4llm
        return pymupdf4llm.to_markdown(file_path)

    async def extract_to_text(self, file_path: str) -> str:
        import fitz
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text


class MarkerExtractor(PDFExtractor):
    """Marker ML-based PDF extractor."""

    @property
    def name(self) -> str:
        return "marker"

    @property
    def available(self) -> bool:
        try:
            from marker.converters.pdf import PdfConverter
            return True
        except ImportError:
            return False

    async def extract_to_md(self, file_path: str) -> str:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        models = create_model_dict()
        converter = PdfConverter(artifact_dict=models)
        rendered = converter(file_path)
        return text_from_rendered(rendered)

    async def extract_to_text(self, file_path: str) -> str:
        md = await self.extract_to_md(file_path)
        # Strip markdown formatting for plain text
        import re
        text = re.sub(r"[#*_`\[\]]", "", md)
        return text


class DoclingExtractor(PDFExtractor):
    """IBM Docling PDF extractor."""

    @property
    def name(self) -> str:
        return "docling"

    @property
    def available(self) -> bool:
        try:
            from docling.document_converter import DocumentConverter
            return True
        except ImportError:
            return False

    async def extract_to_md(self, file_path: str) -> str:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()

    async def extract_to_text(self, file_path: str) -> str:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_text()


class UnstructuredExtractor(PDFExtractor):
    """Unstructured.io PDF extractor."""

    @property
    def name(self) -> str:
        return "unstructured"

    @property
    def available(self) -> bool:
        try:
            from unstructured.partition.pdf import partition_pdf
            return True
        except ImportError:
            return False

    async def extract_to_md(self, file_path: str) -> str:
        from unstructured.partition.pdf import partition_pdf
        elements = partition_pdf(file_path)
        # Convert elements to markdown
        md_lines = []
        for el in elements:
            if el.category == "Title":
                md_lines.append(f"# {el.text}")
            elif el.category == "Header":
                md_lines.append(f"## {el.text}")
            else:
                md_lines.append(el.text)
        return "\n\n".join(md_lines)

    async def extract_to_text(self, file_path: str) -> str:
        from unstructured.partition.pdf import partition_pdf
        elements = partition_pdf(file_path)
        return "\n".join(el.text for el in elements)


@dataclass
class PDFExtractorComparison:
    """Compare multiple PDF extractors on Irish curriculum documents."""

    extractors: list[PDFExtractor] = field(default_factory=list)

    def __post_init__(self):
        """Register default extractors if none provided."""
        if not self.extractors:
            self._register_default_extractors()

    def _register_default_extractors(self):
        """Register all available extractors."""
        potential_extractors = [
            PyMuPDF4LLMExtractor(),
            MarkerExtractor(),
            DoclingExtractor(),
            UnstructuredExtractor(),
        ]
        self.extractors = [e for e in potential_extractors if e.available]
        logger.info(f"Registered {len(self.extractors)} available extractors")

    def list_available(self) -> list[str]:
        """List available extractor names."""
        return [e.name for e in self.extractors]

    async def benchmark_single(
        self,
        pdf_path: str | Path,
        extractor_name: str | None = None,
        output_format: OutputFormat = OutputFormat.MARKDOWN,
    ) -> list[PDFBenchmarkResult]:
        """
        Benchmark extraction on a single PDF.

        Args:
            pdf_path: Path to PDF file
            extractor_name: Specific extractor to use, or None for all
            output_format: Output format to use

        Returns:
            List of benchmark results
        """
        pdf_path = str(pdf_path)
        results = []

        extractors_to_use = self.extractors
        if extractor_name:
            extractors_to_use = [e for e in self.extractors if e.name == extractor_name]

        for extractor in extractors_to_use:
            if not extractor.supports_format(output_format):
                continue

            start_time = time.perf_counter()
            try:
                if output_format == OutputFormat.MARKDOWN:
                    content = await extractor.extract_to_md(pdf_path)
                else:
                    content = await extractor.extract_to_text(pdf_path)

                extraction_time = (time.perf_counter() - start_time) * 1000

                # Count pages
                try:
                    import fitz
                    doc = fitz.open(pdf_path)
                    page_count = len(doc)
                    doc.close()
                except Exception:
                    page_count = 0

                results.append(
                    PDFBenchmarkResult(
                        pdf_path=pdf_path,
                        extractor=extractor.name,
                        output_format=output_format,
                        content=content,
                        extraction_time_ms=extraction_time,
                        page_count=page_count,
                        char_count=len(content),
                        word_count=len(content.split()),
                        success=True,
                    )
                )
                logger.info(
                    f"{extractor.name}: extracted {len(content)} chars in {extraction_time:.0f}ms"
                )

            except Exception as e:
                extraction_time = (time.perf_counter() - start_time) * 1000
                results.append(
                    PDFBenchmarkResult(
                        pdf_path=pdf_path,
                        extractor=extractor.name,
                        output_format=output_format,
                        content="",
                        extraction_time_ms=extraction_time,
                        page_count=0,
                        char_count=0,
                        word_count=0,
                        success=False,
                        error=str(e),
                    )
                )
                logger.error(f"{extractor.name}: extraction failed: {e}")

        return results

    async def benchmark_directory(
        self,
        directory: str | Path,
        pattern: str = "*.pdf",
        output_format: OutputFormat = OutputFormat.MARKDOWN,
    ) -> dict[str, list[PDFBenchmarkResult]]:
        """Benchmark all PDFs in a directory."""
        directory = Path(directory)
        results: dict[str, list[PDFBenchmarkResult]] = {}

        for pdf_path in directory.glob(pattern):
            results[str(pdf_path)] = await self.benchmark_single(pdf_path, output_format=output_format)

        return results

    def select_best_extractor(
        self,
        results: list[PDFBenchmarkResult],
        metric: str = "chars_per_second",
    ) -> str | None:
        """Select the best extractor based on benchmark results."""
        successful = [r for r in results if r.success]
        if not successful:
            return None

        if metric == "chars_per_second":
            best = max(successful, key=lambda r: r.chars_per_second)
        elif metric == "extraction_time_ms":
            best = min(successful, key=lambda r: r.extraction_time_ms)
        elif metric == "word_count":
            best = max(successful, key=lambda r: r.word_count)
        else:
            best = successful[0]

        return best.extractor


# =============================================================================
# Dagster Asset
# =============================================================================

try:
    from dagster import AssetExecutionContext, Config, asset
    from pydantic import Field as PydanticField

    class PDFBenchmarkConfig(Config):
        """Configuration for PDF benchmark asset."""

        pdf_directory: str = PydanticField(
            default="",
            description="Directory containing PDFs to benchmark",
        )
        output_format: str = PydanticField(
            default="markdown",
            description="Output format: markdown, text",
        )
        selection_metric: str = PydanticField(
            default="chars_per_second",
            description="Metric for selecting best extractor",
        )

    @asset(
        name="pdf_extraction_benchmark",
        description="Benchmark PDF extraction libraries on Irish curriculum documents",
        group_name="documents",
        compute_kind="pdfstract",
    )
    def pdf_extraction_benchmark(
        context: AssetExecutionContext,
        config: PDFBenchmarkConfig,
    ) -> dict[str, Any]:
        """
        Benchmark PDF extractors on curriculum documents.

        This asset:
        1. Identifies available PDF extractors
        2. Runs extraction benchmarks on test PDFs
        3. Recommends optimal extractor per document type

        Returns:
            Dictionary with benchmark results and recommendations
        """
        comparison = PDFExtractorComparison()

        context.log.info(f"Available extractors: {comparison.list_available()}")

        return {
            "status": "ready",
            "available_extractors": comparison.list_available(),
            "config": {
                "pdf_directory": config.pdf_directory,
                "output_format": config.output_format,
                "selection_metric": config.selection_metric,
            },
        }

except ImportError:
    def pdf_extraction_benchmark(*args, **kwargs):
        raise ImportError("Dagster is required for this asset")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Benchmark PDF extractors")
    parser.add_argument("pdf", help="PDF file to benchmark")
    parser.add_argument("--format", "-f", default="markdown", choices=["markdown", "text"])
    parser.add_argument("--extractor", "-e", help="Specific extractor to use")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    comparison = PDFExtractorComparison()
    print(f"Available extractors: {comparison.list_available()}")

    output_format = OutputFormat.MARKDOWN if args.format == "markdown" else OutputFormat.TEXT
    results = asyncio.run(
        comparison.benchmark_single(args.pdf, args.extractor, output_format)
    )

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        for r in results:
            status = "✓" if r.success else "✗"
            print(f"{status} {r.extractor}: {r.char_count} chars, {r.extraction_time_ms:.0f}ms")
            if r.error:
                print(f"  Error: {r.error}")

        best = comparison.select_best_extractor(results)
        if best:
            print(f"\nRecommended: {best}")
