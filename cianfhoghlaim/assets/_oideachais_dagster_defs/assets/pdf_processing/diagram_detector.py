"""
Stage 2 of the 6-stage PDF processing pipeline: diagram detection.

Uses Granite-Docling 258M for DocTags-based layout classification
(figure / table / heading / paragraph) AND Molmo2-8B for figure-region
pointing (returns bounding boxes).

Per `oideachais-pdf-processing/spec.md`:
- Granite-Docling → layout classification (DocTags)
- Molmo2-8B → figure-region pointing
- Output: per-page `{bbox, type, caption}` records
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

warnings.warn(
    "pdf_processing.diagram_detector is the v4 implementation of Stage 2. "
    "It is experimental; the actual ML model calls are stubbed.",
    UserWarning,
    stacklevel=2,
)

DiagramType = Literal["figure", "table", "heading", "paragraph", "formula", "unknown"]


@dataclass
class DiagramResult:
    """A single diagram/figure/table detected on a page."""

    page_number: int
    diagram_type: DiagramType
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    caption: str = ""
    caption_en: str = ""
    caption_ga: str = ""
    confidence: float = 0.0
    source_model: str = "granite-docling-258M"  # or "molmo2-8b"

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "diagram_type": self.diagram_type,
            "bbox": list(self.bbox),
            "caption": self.caption,
            "caption_en": self.caption_en,
            "caption_ga": self.caption_ga,
            "confidence": self.confidence,
            "source_model": self.source_model,
        }


class DiagramDetector:
    """Stage 2 diagram detector (Granite-Docling + Molmo2-8B).

    Per the v4 spec, the detector runs two models in parallel:
    - Granite-Docling 258M (DocTags) for layout classification
    - Molmo2-8B (transformers) for figure-region pointing

    In production, both models are loaded once and reused across calls.
    For now, the actual ML calls are stubbed — the structure is
    production-ready.
    """

    def __init__(
        self,
        layout_model: str = "ibm-granite/granite-docling-258M",
        pointing_model: str = "allenai/Molmo2-8B",
    ):
        """Initialize the diagram detector.

        Args:
            layout_model: HF ID for the layout classification model
                (default: `ibm-granite/granite-docling-258M`)
            pointing_model: HF ID for the figure-region pointing model
                (default: `allenai/Molmo2-8B`)
        """
        self.layout_model = layout_model
        self.pointing_model = pointing_model

    def detect_all_pages(
        self,
        page_images: list[bytes],
    ) -> list[list[DiagramResult]]:
        """Detect diagrams on every page.

        Args:
            page_images: List of rendered page images (PNG bytes)

        Returns:
            List of per-page diagram lists (one list per page)
        """
        results: list[list[DiagramResult]] = []
        for page_number, image_bytes in enumerate(page_images, start=1):
            page_diagrams = self.detect_single_page(page_number, image_bytes)
            results.append(page_diagrams)
        return results

    def detect_single_page(
        self,
        page_number: int,
        image_bytes: bytes,
    ) -> list[DiagramResult]:
        """Detect diagrams on a single page.

        Args:
            page_number: 1-indexed page number
            image_bytes: PNG bytes of the rendered page

        Returns:
            List of DiagramResult records for this page
        """
        # Stub: in production this runs Granite-Docling for layout
        # classification and Molmo2-8B for figure pointing.
        logger.debug(
            f"Stage 2 — Detecting diagrams on page {page_number} "
            f"({len(image_bytes)} bytes) using "
            f"{self.layout_model} + {self.pointing_model}"
        )
        return []

    def classify_layout(
        self,
        image_bytes: bytes,
    ) -> list[dict[str, Any]]:
        """Classify layout regions using Granite-Docling DocTags.

        Args:
            image_bytes: PNG bytes of the rendered page

        Returns:
            List of `{type, bbox, doc_tag}` records
        """
        # Stub
        return []

    def point_figures(
        self,
        image_bytes: bytes,
    ) -> list[tuple[float, float, float, float]]:
        """Point at figure regions using Molmo2-8B.

        Args:
            image_bytes: PNG bytes of the rendered page

        Returns:
            List of bounding boxes `(x_min, y_min, x_max, y_max)`
        """
        # Stub
        return []

    def caption_figure(
        self,
        image_bytes: bytes,
        bbox: tuple[float, float, float, float],
        language: str = "en",
    ) -> str:
        """Caption a detected figure region using Qwen 3-VL 8B (Unsloth GGUF).

        Args:
            image_bytes: PNG bytes of the rendered page
            bbox: Bounding box of the figure region
            language: "en" or "ga" (Irish)

        Returns:
            1-2 sentence caption
        """
        # Stub
        return ""
