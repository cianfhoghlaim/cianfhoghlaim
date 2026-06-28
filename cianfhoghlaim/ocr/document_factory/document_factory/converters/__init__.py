"""
PDF Converter Implementations.

Each converter wraps a specific PDF extraction library with a common interface.
Lazy-loaded by the LazyPDFFactory to minimize startup time.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .deepseekocr_converter import DeepSeekOCRConverter
    from .docling_converter import DoclingConverter
    from .marker_converter import MarkerConverter
    from .pymupdf4llm_converter import PyMuPDF4LLMConverter
    from .unstructured_converter import UnstructuredConverter

__all__ = [
    "DeepSeekOCRConverter",
    "DoclingConverter",
    "MarkerConverter",
    "PyMuPDF4LLMConverter",
    "UnstructuredConverter",
]
