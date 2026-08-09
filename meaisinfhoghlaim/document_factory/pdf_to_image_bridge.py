"""PDF page -> BAML image adapter.

Renders a single PDF page to bytes and wraps it as a `baml_py.Image`,
closing the gap documented in `tuatha/asset_generation/fibo/assets.py::
fibo_configs_from_syllabus_diagrams` and fixed in
`baml_src/british_isles/ireland/education/lc_extraction/
syllabus_diagram.baml`: `ExtractSyllabusDiagram` is declared
`client BIEPV3Vision` (a real vision client routing through litellm ->
llama-swap -> qwen3-vl-8b) but previously had no `image` parameter at
all, so "vision" extraction was actually text-only.

Deliberately self-contained rather than importing
`sruth.shared.extraction.docling_resource.DoclingResource` (which has
the same base64/data-URI encoding pattern this module reuses
conceptually): `sruth/shared/` is a separate `pyproject.toml` workspace
member whose `__init__.py` eagerly imports an unrelated `agent_os`
middleware chain (FastAPI, PyJWT, ...) with no relation to PDF
rendering. That's the same reasoning
`tuatha/asset_generation/fibo/assets.py::_find_english_syllabus_pdf()`
already documents for avoiding a cross-layer import elsewhere in this
codebase. This module uses `pymupdf` directly instead -- the same
library `dlt_sources/british_isles/ireland/education/_pdf_text.py::
extract_pdf_text()` already uses for text extraction in this exact
pipeline, so no new PDF-rendering dependency (e.g. `pdf2image` + a
system `poppler` binary) is introduced.
"""

from __future__ import annotations

import base64
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

DEFAULT_DPI = 200
DEFAULT_IMAGE_FORMAT = "png"
_MEDIA_TYPE_BY_FORMAT = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
}


def render_pdf_page_to_bytes(
    pdf_path: Path,
    page_number: int,
    dpi: int = DEFAULT_DPI,
    image_format: str = DEFAULT_IMAGE_FORMAT,
) -> bytes | None:
    """Render one PDF page (1-indexed) to raw image bytes.

    Returns `None` (rather than raising) if `pymupdf` is unavailable or
    the page can't be rendered -- callers should treat that as "fall
    back to text-only extraction", matching `extract_pdf_text()`'s own
    graceful-degradation convention rather than crashing a whole
    extraction run over one bad page.
    """
    try:
        import pymupdf  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("pymupdf_not_installed", page=page_number)
        return None

    try:
        doc = pymupdf.open(str(pdf_path))
        try:
            if not (1 <= page_number <= doc.page_count):
                logger.warning(
                    "page_number_out_of_range",
                    path=str(pdf_path),
                    page=page_number,
                    page_count=doc.page_count,
                )
                return None
            page = doc[page_number - 1]  # pymupdf is 0-indexed internally
            zoom = dpi / 72.0  # PDF base resolution is 72 DPI
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
            return pixmap.tobytes(image_format)
        finally:
            doc.close()
    except Exception as exc:
        logger.warning(
            "pdf_page_render_failed",
            path=str(pdf_path),
            page=page_number,
            error=str(exc),
        )
        return None


def render_pdf_page_to_data_uri(
    pdf_path: Path,
    page_number: int,
    dpi: int = DEFAULT_DPI,
    image_format: str = DEFAULT_IMAGE_FORMAT,
) -> str | None:
    """Render one PDF page and return a `data:<media-type>;base64,...` URI.

    Shared by any caller building a raw `image_url` content block for an
    OpenAI-compatible chat completions endpoint (litellm, most vision
    gateways) -- the same base64/data-URI construction
    `sruth/shared/extraction/docling_resource.py::ocr_page_vlm()` already
    does inline; factored out here so
    `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`'s `_call_qwen3_vl`
    doesn't need a 3rd copy of the same encoding logic (see the
    2026-08-08-lakehouse-extensive-hydration-v1 change).
    """
    image_bytes = render_pdf_page_to_bytes(
        pdf_path, page_number, dpi=dpi, image_format=image_format
    )
    if image_bytes is None:
        return None
    media_type = _MEDIA_TYPE_BY_FORMAT.get(image_format.lower(), "image/png")
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{media_type};base64,{b64}"


def pdf_page_to_baml_image(
    pdf_path: Path,
    page_number: int,
    dpi: int = DEFAULT_DPI,
    image_format: str = DEFAULT_IMAGE_FORMAT,
):
    """Render one PDF page and wrap it as a `baml_py.Image`.

    Returns `None` (not a raised exception) on any failure -- the
    caller is expected to fall back to the `image=None` / text-only
    path in `ExtractSyllabusDiagram`, which is designed to degrade
    gracefully rather than require an image.
    """
    try:
        import baml_py
    except ImportError:
        logger.warning("baml_py_not_installed", page=page_number)
        return None

    image_bytes = render_pdf_page_to_bytes(
        pdf_path, page_number, dpi=dpi, image_format=image_format
    )
    if image_bytes is None:
        return None

    media_type = _MEDIA_TYPE_BY_FORMAT.get(image_format.lower(), "image/png")
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return baml_py.Image.from_base64(media_type, b64)


__all__ = [
    "DEFAULT_DPI",
    "pdf_page_to_baml_image",
    "render_pdf_page_to_bytes",
    "render_pdf_page_to_data_uri",
]
