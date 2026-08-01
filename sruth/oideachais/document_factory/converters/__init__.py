"""
PDF Converter Implementations.

Each converter wraps a specific PDF extraction library with a common interface.
Lazy-loaded by the LazyPDFFactory to minimize startup time.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pymupdf4llm_converter import PyMuPDF4LLMConverter
    from .marker_converter import MarkerConverter
    from .docling_converter import DoclingConverter
    from .deepseekocr_converter import DeepSeekOCRConverter
    from .unstructured_converter import UnstructuredConverter

__all__ = [
    "PyMuPDF4LLMConverter",
    "MarkerConverter",
    "DoclingConverter",
    "DeepSeekOCRConverter",
    "UnstructuredConverter",
]
