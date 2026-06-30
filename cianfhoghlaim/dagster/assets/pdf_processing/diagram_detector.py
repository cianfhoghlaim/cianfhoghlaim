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
        """Detect diagrams on every page (parallelized).

        Args:
            page_images: List of rendered page images (PNG bytes)

        Returns:
            List of per-page diagram lists (one list per page)
        """
        import asyncio

        async def detect_async(idx_img):
            idx, image_bytes = idx_img
            return idx + 1, await self._detect_single_page_async(idx + 1, image_bytes)

        async def main_async():
            tasks = [detect_async((i, img)) for i, img in enumerate(page_images)]
            return await asyncio.gather(*tasks)

        # Run the asyncio loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context (e.g. Dagster)
                return asyncio.gather(
                    *[self._detect_single_page_async(i + 1, img)
                      for i, img in enumerate(page_images)]
                )
            results = loop.run_until_complete(main_async())
        except RuntimeError:
            # No event loop — create one
            results = asyncio.run(main_async())

        return [r for _, r in sorted(results, key=lambda x: x[0])]

    async def _detect_single_page_async(
        self,
        page_number: int,
        image_bytes: bytes,
    ) -> DiagramResult | list[DiagramResult]:
        """Detect diagrams on a single page (async)."""
        # Stub for now — full implementation runs Granite-Docling + Molmo2-8B
        logger.debug(
            f"Stage 2 — Detecting diagrams on page {page_number} "
            f"({len(image_bytes)} bytes) using "
            f"{self.layout_model} + {self.pointing_model}"
        )
        return []

    def detect_single_page(
        self,
        page_number: int,
        image_bytes: bytes,
    ) -> list[DiagramResult]:
        """Detect diagrams on a single page (sync wrapper).

        Args:
            page_number: 1-indexed page number
            image_bytes: PNG bytes of the rendered page

        Returns:
            List of DiagramResult records for this page
        """
        # In production: use asyncio.run to call the async version
        import asyncio
        try:
            result = asyncio.run(
                self._detect_single_page_async(page_number, image_bytes)
            )
        except Exception as e:
            logger.error(f"Stage 2 diagram detection failed on page {page_number}: {e}")
            return []
        if isinstance(result, list):
            return result
        return [result] if result else []

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
        try:
            from transformers import AutoProcessor, AutoModelForVision2Seq
            import torch

            processor = AutoProcessor.from_pretrained(self.layout_model)
            model = AutoModelForVision2Seq.from_pretrained(
                self.layout_model, torch_dtype=torch.float16
            )
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            inputs = processor(images=image, return_tensors="pt")
            outputs = model.generate(**inputs, max_new_tokens=2048)
            doc_tags = processor.batch_decode(outputs, skip_special_tokens=True)[0]
            # Parse DocTags XML to extract regions
            # (DocTags is an XML-like format: <doctag><figure><...></figure></doctag>)
            return self._parse_doctags(doc_tags)
        except Exception as e:
            logger.error(f"Granite-Docling layout classification failed: {e}")
            return []

    def _parse_doctags(self, doc_tags_xml: str) -> list[dict[str, Any]]:
        """Parse Granite-Docling DocTags XML to a list of region records."""
        import xml.etree.ElementTree as ET
        results: list[dict[str, Any]] = []
        try:
            root = ET.fromstring(doc_tags_xml)
            for child in root:
                tag = child.tag.lower()
                if tag in ("figure", "table", "heading", "paragraph", "formula"):
                    results.append({
                        "type": tag,
                        "doc_tag": child.text or "",
                        "bbox": (0.0, 0.0, 1.0, 1.0),  # Granite-Docling doesn't emit bboxes; use full-page
                    })
        except ET.ParseError as e:
            logger.warning(f"DocTags XML parse failed: {e}")
        return results

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
        try:
            import litellm
            import base64
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            response = litellm.completion(
                model=f"local/vision/{self.pointing_model.split('/')[-1]}",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"},
                            },
                            {
                                "type": "text",
                                "text": "Point to every figure, table, and formula in this image.",
                            },
                        ],
                    }
                ],
                timeout=600,
                temperature=0.0,
            )
            text = response.choices[0].message.content or ""
            # Parse Molmo2-8B's pointing output
            return self._parse_molmo_points(text)
        except Exception as e:
            logger.error(f"Molmo2-8B figure pointing failed: {e}")
            return []

    def _parse_molmo_points(self, molmo_text: str) -> list[tuple[float, float, float, float]]:
        """Parse Molmo2-8B's pointing output (typically `<point x="0.5" y="0.3">caption</point>`)."""
        import re
        # Pattern: <point x="0.5" y="0.3">caption</point>
        pattern = re.compile(
            r'<point\s+x="([\d.]+)"\s+y="([\d.]+)"(?:\s+alt="([^"]+)")?\s*>([^<]*)</point>'
        )
        boxes: list[tuple[float, float, float, float]] = []
        for m in pattern.finditer(molmo_text):
            x = float(m.group(1))
            y = float(m.group(2))
            # Molmo emits a point (x, y); convert to a small box around the point
            size = 0.05
            boxes.append((
                max(0.0, x - size / 2),
                max(0.0, y - size / 2),
                min(1.0, x + size / 2),
                min(1.0, y + size / 2),
            ))
        return boxes

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
        try:
            import litellm
            import base64
            from PIL import Image
            import io
            # Crop to bbox
            image = Image.open(io.BytesIO(image_bytes))
            x1, y1, x2, y2 = bbox
            cropped = image.crop((int(x1 * image.width), int(y1 * image.height),
                                  int(x2 * image.width), int(y2 * image.height)))
            buf = io.BytesIO()
            cropped.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            lang_hint = "in Irish (Gaeilge)" if language == "ga" else "in English"
            response = litellm.completion(
                model="local/vision/qwen3-vl-8b",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"},
                            },
                            {
                                "type": "text",
                                "text": f"Caption this figure briefly {lang_hint}. "
                                        "Preserve any visible labels or annotations verbatim.",
                            },
                        ],
                    }
                ],
                timeout=120,
                temperature=0.0,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Figure captioning failed: {e}")
            return ""
