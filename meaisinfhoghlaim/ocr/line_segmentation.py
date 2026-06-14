"""
Line Segmentation for Irish Historical Handwriting.

Provides line-level cropping from manuscript page images using:
- Horizontal projection profiles
- Connected component analysis
- Deep learning-based detection (optional)

Designed for Dúchas.ie Schools' Collection manuscripts
to create MNIST-style training samples.

Based on PyLaia reference: taighde/teanga/pylaia/laia/callbacks/segmentation.py

Usage:
    from ocr.line_segmentation import LineSegmenter

    segmenter = LineSegmenter()
    lines = segmenter.segment_page(image, transcription_lines)

    for line in lines:
        crop = line.image_crop
        text = line.transcription
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Bounding box for a line region."""

    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        return self.width / max(self.height, 1)

    def to_dict(self) -> dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    def expand(self, padding: int) -> BoundingBox:
        """Expand box by padding pixels."""
        return BoundingBox(
            x=max(0, self.x - padding),
            y=max(0, self.y - padding),
            width=self.width + 2 * padding,
            height=self.height + 2 * padding,
        )


@dataclass
class SegmentedLine:
    """A segmented line from a manuscript page."""

    line_number: int
    bbox: BoundingBox
    transcription: str
    confidence: float = 1.0
    image_crop: Any = None  # PIL Image or numpy array
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_number": self.line_number,
            "bbox": self.bbox.to_dict(),
            "transcription": self.transcription,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class SegmentationConfig:
    """Configuration for line segmentation."""

    # Preprocessing
    binarize: bool = True
    denoise: bool = True
    deskew: bool = True

    # Projection profile settings
    min_line_height: int = 20
    max_line_height: int = 200
    min_gap_height: int = 5
    smoothing_window: int = 5

    # Connected component settings
    min_component_area: int = 50
    max_component_area: int = 100000

    # Line filtering
    min_line_width: int = 50
    min_aspect_ratio: float = 2.0
    max_aspect_ratio: float = 100.0

    # Padding for crops
    vertical_padding: int = 5
    horizontal_padding: int = 10

    # Target size for MNIST-style output
    target_height: int = 64
    normalize_width: bool = False
    max_width: int = 2048


class LineSegmenter:
    """
    Segment manuscript pages into individual text lines.

    Uses horizontal projection profiles as primary method,
    with connected component analysis for refinement.
    """

    def __init__(self, config: SegmentationConfig | None = None):
        """Initialize segmenter with configuration."""
        self.config = config or SegmentationConfig()

    def segment_page(
        self,
        image: Any,
        transcription_lines: list[str] | None = None,
    ) -> list[SegmentedLine]:
        """
        Segment a manuscript page into text lines.

        Args:
            image: PIL Image or numpy array
            transcription_lines: Optional list of transcription lines
                                 to align with detected lines

        Returns:
            List of SegmentedLine objects with crops and transcriptions
        """
        from PIL import Image

        # Convert to numpy array
        if hasattr(image, "numpy"):
            img_array = np.array(image)
        elif isinstance(image, np.ndarray):
            img_array = image
        else:
            img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            if img_array.shape[2] == 4:  # RGBA
                img_array = img_array[:, :, :3]
            gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            gray = img_array

        # Preprocess
        processed = self._preprocess(gray)

        # Detect lines using projection profile
        line_bboxes = self._detect_lines_projection(processed)

        # Refine with connected components if few lines detected
        if len(line_bboxes) < 3:
            cc_bboxes = self._detect_lines_connected_components(processed)
            if len(cc_bboxes) > len(line_bboxes):
                line_bboxes = cc_bboxes

        # Sort by vertical position
        line_bboxes.sort(key=lambda b: b.y)

        # Align transcriptions if provided
        if transcription_lines and len(transcription_lines) == len(line_bboxes):
            texts = transcription_lines
        elif transcription_lines:
            # Try to match based on count
            texts = self._align_transcriptions(line_bboxes, transcription_lines)
        else:
            texts = [""] * len(line_bboxes)

        # Create SegmentedLine objects with crops
        segmented_lines = []
        pil_image = Image.fromarray(img_array) if not isinstance(image, Image.Image) else image

        for i, (bbox, text) in enumerate(zip(line_bboxes, texts)):
            # Expand bbox with padding
            padded_bbox = bbox.expand(self.config.vertical_padding)

            # Ensure bounds
            padded_bbox.x = max(0, padded_bbox.x)
            padded_bbox.y = max(0, padded_bbox.y)
            padded_bbox.width = min(padded_bbox.width, pil_image.width - padded_bbox.x)
            padded_bbox.height = min(padded_bbox.height, pil_image.height - padded_bbox.y)

            # Crop image
            crop = pil_image.crop((
                padded_bbox.x,
                padded_bbox.y,
                padded_bbox.x2,
                padded_bbox.y2,
            ))

            # Resize to target height if configured
            if self.config.target_height > 0:
                crop = self._resize_to_height(crop, self.config.target_height)

            segmented_lines.append(SegmentedLine(
                line_number=i + 1,
                bbox=padded_bbox,
                transcription=text.strip() if text else "",
                confidence=1.0,
                image_crop=crop,
                metadata={
                    "original_bbox": bbox.to_dict(),
                    "page_size": (pil_image.width, pil_image.height),
                },
            ))

        return segmented_lines

    def _preprocess(self, gray: np.ndarray) -> np.ndarray:
        """Preprocess image for line detection."""
        try:
            import cv2
        except ImportError:
            logger.warning("OpenCV not available, using basic preprocessing")
            # Basic thresholding without OpenCV
            threshold = np.mean(gray)
            return (gray < threshold).astype(np.uint8) * 255

        processed = gray.copy()

        # Denoise
        if self.config.denoise:
            processed = cv2.fastNlMeansDenoising(processed, h=10)

        # Binarize (Otsu's method)
        if self.config.binarize:
            _, processed = cv2.threshold(
                processed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

        # Deskew
        if self.config.deskew:
            processed = self._deskew(processed)

        return processed

    def _deskew(self, binary: np.ndarray) -> np.ndarray:
        """Deskew binary image using Hough transform."""
        try:
            import cv2
        except ImportError:
            return binary

        # Find lines using Hough transform
        lines = cv2.HoughLinesP(
            binary,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=binary.shape[1] // 4,
            maxLineGap=10,
        )

        if lines is None or len(lines) < 3:
            return binary

        # Calculate median angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                if abs(angle) < 15:  # Only consider near-horizontal lines
                    angles.append(angle)

        if not angles:
            return binary

        median_angle = np.median(angles)

        if abs(median_angle) < 0.5:  # Already nearly horizontal
            return binary

        # Rotate image
        h, w = binary.shape
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            binary,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderValue=0,
        )

        return rotated

    def _detect_lines_projection(self, binary: np.ndarray) -> list[BoundingBox]:
        """
        Detect text lines using horizontal projection profile.

        This is the primary method for line segmentation.
        """
        # Calculate horizontal projection (sum of white pixels per row)
        h_proj = np.sum(binary, axis=1)

        # Smooth projection
        if self.config.smoothing_window > 1:
            kernel = np.ones(self.config.smoothing_window) / self.config.smoothing_window
            h_proj = np.convolve(h_proj, kernel, mode="same")

        # Find line regions (where projection is above threshold)
        threshold = np.max(h_proj) * 0.1
        in_line = h_proj > threshold

        # Find line boundaries
        line_bboxes = []
        line_start = None

        for y, is_line in enumerate(in_line):
            if is_line and line_start is None:
                line_start = y
            elif not is_line and line_start is not None:
                line_end = y
                height = line_end - line_start

                # Filter by height
                if self.config.min_line_height <= height <= self.config.max_line_height:
                    # Find horizontal extent
                    line_region = binary[line_start:line_end, :]
                    v_proj = np.sum(line_region, axis=0)
                    nonzero = np.where(v_proj > 0)[0]

                    if len(nonzero) > 0:
                        x_start = nonzero[0]
                        x_end = nonzero[-1]
                        width = x_end - x_start

                        if width >= self.config.min_line_width:
                            aspect = width / height
                            if self.config.min_aspect_ratio <= aspect <= self.config.max_aspect_ratio:
                                line_bboxes.append(BoundingBox(
                                    x=x_start,
                                    y=line_start,
                                    width=width,
                                    height=height,
                                ))

                line_start = None

        # Handle last line
        if line_start is not None:
            height = binary.shape[0] - line_start
            if self.config.min_line_height <= height <= self.config.max_line_height:
                line_region = binary[line_start:, :]
                v_proj = np.sum(line_region, axis=0)
                nonzero = np.where(v_proj > 0)[0]
                if len(nonzero) > 0:
                    x_start = nonzero[0]
                    width = nonzero[-1] - x_start
                    if width >= self.config.min_line_width:
                        line_bboxes.append(BoundingBox(
                            x=x_start,
                            y=line_start,
                            width=width,
                            height=height,
                        ))

        return line_bboxes

    def _detect_lines_connected_components(self, binary: np.ndarray) -> list[BoundingBox]:
        """
        Detect text lines using connected component analysis.

        Fallback method when projection profile fails.
        """
        try:
            import cv2
        except ImportError:
            return []

        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        # Group components into lines based on vertical position
        components = []
        for i in range(1, num_labels):  # Skip background (0)
            x, y, w, h, area = stats[i]

            if self.config.min_component_area <= area <= self.config.max_component_area:
                components.append({
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "centroid_y": centroids[i][1],
                })

        if not components:
            return []

        # Sort by vertical position
        components.sort(key=lambda c: c["centroid_y"])

        # Group into lines (components with similar y centroids)
        lines = []
        current_line = [components[0]]
        line_y = components[0]["centroid_y"]

        for comp in components[1:]:
            if abs(comp["centroid_y"] - line_y) < self.config.min_line_height:
                current_line.append(comp)
            else:
                lines.append(current_line)
                current_line = [comp]
                line_y = comp["centroid_y"]

        if current_line:
            lines.append(current_line)

        # Convert to bounding boxes
        line_bboxes = []
        for line_components in lines:
            x_min = min(c["x"] for c in line_components)
            y_min = min(c["y"] for c in line_components)
            x_max = max(c["x"] + c["width"] for c in line_components)
            y_max = max(c["y"] + c["height"] for c in line_components)

            width = x_max - x_min
            height = y_max - y_min

            if width >= self.config.min_line_width:
                line_bboxes.append(BoundingBox(
                    x=x_min,
                    y=y_min,
                    width=width,
                    height=height,
                ))

        return line_bboxes

    def _align_transcriptions(
        self,
        bboxes: list[BoundingBox],
        transcriptions: list[str],
    ) -> list[str]:
        """
        Align transcriptions to detected line bboxes.

        Uses simple position-based matching when counts differ.
        """
        n_boxes = len(bboxes)
        n_trans = len(transcriptions)

        if n_boxes == n_trans:
            return transcriptions

        if n_boxes < n_trans:
            # More transcriptions than boxes - merge adjacent lines
            merged = []
            ratio = n_trans / n_boxes
            for i in range(n_boxes):
                start = int(i * ratio)
                end = int((i + 1) * ratio)
                merged.append(" ".join(transcriptions[start:end]))
            return merged
        else:
            # More boxes than transcriptions - leave some empty
            result = [""] * n_boxes
            ratio = n_boxes / n_trans
            for i, text in enumerate(transcriptions):
                idx = min(int(i * ratio), n_boxes - 1)
                result[idx] = text
            return result

    def _resize_to_height(self, image: Any, target_height: int) -> Any:
        """Resize image to target height maintaining aspect ratio."""
        from PIL import Image

        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)

        w, h = image.size
        if h == target_height:
            return image

        ratio = target_height / h
        new_width = int(w * ratio)

        # Cap width if configured
        if self.config.max_width > 0:
            new_width = min(new_width, self.config.max_width)

        return image.resize((new_width, target_height), Image.Resampling.LANCZOS)


def segment_duchas_page(
    image_path: str | Path,
    transcription_text: str | None = None,
    config: SegmentationConfig | None = None,
) -> Iterator[SegmentedLine]:
    """
    Convenience function to segment a Dúchas manuscript page.

    Args:
        image_path: Path to page image
        transcription_text: Full transcription text (lines separated by newlines)
        config: Optional segmentation configuration

    Yields:
        SegmentedLine objects with crops and aligned transcriptions
    """
    from PIL import Image

    image = Image.open(image_path)

    transcription_lines = None
    if transcription_text:
        transcription_lines = [
            line.strip() for line in transcription_text.split("\n")
            if line.strip()
        ]

    segmenter = LineSegmenter(config)
    lines = segmenter.segment_page(image, transcription_lines)

    yield from lines
