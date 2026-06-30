"""By-domain re-exports for backward compat with the legacy top-level paths.

Preserves the old `from cianfhoghlaim.dagster.assets.pdf_assets import ...`
paths for one release. Update your imports to the by_domain/ path.
"""
from .pdf_processing import (
    pdf_cognify,
    pdf_convert,
    pdf_discover,
    pdf_embed_cocoindex,
    pdf_evaluate,
    pdf_extract_baml,
    pdf_ocr_compare,
    pdf_quality_check,
)

__all__ = [
    "pdf_cognify",
    "pdf_convert",
    "pdf_discover",
    "pdf_embed_cocoindex",
    "pdf_evaluate",
    "pdf_extract_baml",
    "pdf_ocr_compare",
    "pdf_quality_check",
]