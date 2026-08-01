"""
ColPali Weak Supervision Aligner.

Uses ColPali's vision-language model to generate line-level bounding boxes
from page-level transcriptions without manual annotation.

Algorithm:
1. Parse TEI-XML into line segments
2. Generate 32x32 patch embeddings via SigLIP encoder
3. Compute MaxSim attention for each line query
4. Upscale heatmap to original resolution
5. Apply Otsu binarization + morphological dilation
6. Extract contours and bounding boxes

Usage:
    from alignment import ColPaliAligner

    aligner = ColPaliAligner()
    aligned_lines = aligner.align_transcription(image, transcription_lines)

    for line in aligned_lines:
        print(f"Line {line.line_number}: {line.bbox} -> {line.text}")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class BoundingBox:
    """Bounding box coordinates (normalized 0-1 or pixel values)."""

    x: float
    y: float
    width: float
    height: float
    confidence: float = 1.0

    @property
    def x2(self) -> float:
        """Right edge x coordinate."""
        return self.x + self.width

    @property
    def y2(self) -> float:
        """Bottom edge y coordinate."""
        return self.y + self.height

    @property
    def center(self) -> tuple[float, float]:
        """Center point (x, y)."""
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def area(self) -> float:
        """Area of bounding box."""
        return self.width * self.height

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
        }

    def to_xyxy(self) -> tuple[float, float, float, float]:
        """Convert to (x1, y1, x2, y2) format."""
        return (self.x, self.y, self.x2, self.y2)

    def to_xywh(self) -> tuple[float, float, float, float]:
        """Convert to (x, y, width, height) format."""
        return (self.x, self.y, self.width, self.height)

    def iou(self, other: "BoundingBox") -> float:
        """Calculate Intersection over Union with another box."""
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)

        if x2 <= x1 or y2 <= y1:
            return 0.0

        intersection = (x2 - x1) * (y2 - y1)
        union = self.area + other.area - intersection

        return intersection / union if union > 0 else 0.0


@dataclass
class AlignedLine:
    """A transcription line aligned to image coordinates."""

    line_number: int
    text: str
    bbox: BoundingBox
    heatmap: np.ndarray | None = None
    gaelic_features: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "line_number": self.line_number,
            "text": self.text,
            "bbox": self.bbox.to_dict(),
            "gaelic_features": self.gaelic_features,
        }


class ColPaliAligner:
    """
    ColPali-based weak supervision for generating bounding boxes.

    Uses the ColPali vision-language model to align text transcriptions
    to manuscript images without manual annotation.
    """

    def __init__(
        self,
        model_name: str = "vidore/colpali-v1.2",
        device: str | None = None,
        patch_size: int = 32,
        min_confidence: float = 0.3,
    ):
        """
        Initialize ColPali aligner.

        Args:
            model_name: HuggingFace model identifier for ColPali
            device: Device to run on (auto-detected if None)
            patch_size: Size of image patches (32 for SigLIP)
            min_confidence: Minimum confidence threshold for boxes
        """
        self.model_name = model_name
        self.patch_size = patch_size
        self.min_confidence = min_confidence
        self._model = None
        self._processor = None

        # Determine device
        if device is None:
            try:
                import torch

                if torch.cuda.is_available():
                    self.device = "cuda"
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    self.device = "mps"
                else:
                    self.device = "cpu"
            except ImportError:
                self.device = "cpu"
        else:
            self.device = device

    def _load_model(self) -> None:
        """Lazy load the ColPali model."""
        if self._model is not None:
            return

        try:
            from colpali_engine.models import ColPali, ColPaliProcessor
            import torch

            self._model = ColPali.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16 if self.device != "cpu" else torch.float32,
            ).to(self.device)
            self._model.eval()

            self._processor = ColPaliProcessor.from_pretrained(self.model_name)

        except ImportError:
            raise ImportError(
                "colpali_engine package required. "
                "Install with: pip install colpali-engine"
            )

    def generate_heatmap(
        self,
        image: Any,
        query: str,
    ) -> np.ndarray:
        """
        Generate MaxSim attention heatmap for a text query.

        Args:
            image: PIL Image or numpy array
            query: Text query (e.g., a line of transcription)

        Returns:
            2D numpy array heatmap (same aspect ratio as patches)
        """
        self._load_model()
        import torch
        from PIL import Image

        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Process image and query
        with torch.no_grad():
            # Get image embeddings (patches)
            image_inputs = self._processor.process_images([image])
            image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
            image_embeddings = self._model(**image_inputs)

            # Get query embeddings
            query_inputs = self._processor.process_queries([query])
            query_inputs = {k: v.to(self.device) for k, v in query_inputs.items()}
            query_embeddings = self._model(**query_inputs)

            # Compute MaxSim attention
            # image_embeddings: (1, num_patches, hidden_dim)
            # query_embeddings: (1, query_len, hidden_dim)
            similarity = torch.matmul(
                image_embeddings, query_embeddings.transpose(-1, -2)
            )
            # Max over query tokens
            max_sim = similarity.max(dim=-1).values  # (1, num_patches)

            # Reshape to 2D grid
            num_patches = max_sim.shape[-1]
            grid_size = int(np.sqrt(num_patches))
            heatmap = max_sim[0].reshape(grid_size, grid_size).cpu().numpy()

        return heatmap

    def heatmap_to_bbox(
        self,
        heatmap: np.ndarray,
        original_size: tuple[int, int],
        threshold_method: str = "otsu",
    ) -> BoundingBox:
        """
        Convert attention heatmap to bounding box.

        Args:
            heatmap: 2D numpy array from generate_heatmap
            original_size: (width, height) of original image
            threshold_method: "otsu" or "adaptive"

        Returns:
            BoundingBox in pixel coordinates
        """
        import cv2

        original_width, original_height = original_size

        # Upscale heatmap to original resolution
        heatmap_upscaled = cv2.resize(
            heatmap.astype(np.float32),
            (original_width, original_height),
            interpolation=cv2.INTER_LINEAR,
        )

        # Normalize to 0-255
        heatmap_normalized = (
            (heatmap_upscaled - heatmap_upscaled.min())
            / (heatmap_upscaled.max() - heatmap_upscaled.min() + 1e-8)
            * 255
        ).astype(np.uint8)

        # Apply thresholding
        if threshold_method == "otsu":
            _, binary = cv2.threshold(
                heatmap_normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        else:
            binary = cv2.adaptiveThreshold(
                heatmap_normalized,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.dilate(binary, kernel, iterations=2)
        binary = cv2.erode(binary, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            # Return full image if no contours found
            return BoundingBox(
                x=0,
                y=0,
                width=float(original_width),
                height=float(original_height),
                confidence=0.0,
            )

        # Find largest contour (assumed to be the text region)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate confidence from heatmap values in region
        region_values = heatmap_upscaled[y : y + h, x : x + w]
        confidence = float(region_values.mean() / heatmap_upscaled.max())

        return BoundingBox(
            x=float(x),
            y=float(y),
            width=float(w),
            height=float(h),
            confidence=confidence,
        )

    def detect_gaelic_features(self, text: str) -> dict[str, bool]:
        """
        Detect Gaelic script features in text.

        Args:
            text: Line of text to analyze

        Returns:
            Dictionary of detected features
        """
        return {
            "has_tironian_et": "\u204a" in text or "7" in text,  # Tironian et
            "has_punctum_delens": any(
                c in text for c in ["\u1e03", "\u1e0b", "\u1e1f", "\u1e21", "\u1e41", "\u1e57", "\u1e61", "\u1e6b"]
            ),
            "has_fada": any(c in text for c in ["\u00e1", "\u00e9", "\u00ed", "\u00f3", "\u00fa", "\u00c1", "\u00c9", "\u00cd", "\u00d3", "\u00da"]),
            "has_seanchlo": any(
                ord(c) in range(0xA000, 0xA4CF) for c in text  # Ogham block
            ),
            "is_bilingual": bool(
                # English-ish patterns mixed with Irish
                any(word in text.lower() for word in ["the", "and", "of", "is"])
                and any(word in text.lower() for word in ["agus", "an", "na", "le"])
            ),
        }

    def align_transcription(
        self,
        image: Any,
        transcription_lines: list[str],
        progress_callback: Any | None = None,
    ) -> list[AlignedLine]:
        """
        Align transcription lines to image coordinates.

        Args:
            image: PIL Image or numpy array
            transcription_lines: List of text lines from transcription
            progress_callback: Optional callback(current, total)

        Returns:
            List of AlignedLine objects with bounding boxes
        """
        from PIL import Image

        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        original_size = image.size  # (width, height)
        aligned_lines = []

        total_lines = len(transcription_lines)

        for i, line_text in enumerate(transcription_lines):
            if not line_text.strip():
                continue

            # Generate heatmap for this line
            heatmap = self.generate_heatmap(image, line_text)

            # Convert to bounding box
            bbox = self.heatmap_to_bbox(heatmap, original_size)

            # Skip low-confidence boxes
            if bbox.confidence < self.min_confidence:
                continue

            # Detect Gaelic features
            gaelic_features = self.detect_gaelic_features(line_text)

            aligned_lines.append(
                AlignedLine(
                    line_number=i + 1,
                    text=line_text,
                    bbox=bbox,
                    heatmap=heatmap,
                    gaelic_features=gaelic_features,
                )
            )

            if progress_callback:
                progress_callback(i + 1, total_lines)

        # Sort by y-coordinate (top to bottom)
        aligned_lines.sort(key=lambda line: line.bbox.y)

        # Renumber after sorting
        for i, line in enumerate(aligned_lines):
            line.line_number = i + 1

        return aligned_lines

    def visualize_alignment(
        self,
        image: Any,
        aligned_lines: list[AlignedLine],
        output_path: str | Path | None = None,
        show: bool = False,
    ) -> Any:
        """
        Visualize aligned bounding boxes on image.

        Args:
            image: PIL Image or numpy array
            aligned_lines: List of AlignedLine objects
            output_path: Optional path to save visualization
            show: Whether to display the image

        Returns:
            PIL Image with overlaid boxes
        """
        from PIL import Image, ImageDraw, ImageFont

        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Create copy for drawing
        vis_image = image.copy()
        draw = ImageDraw.Draw(vis_image)

        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except Exception:
            font = ImageFont.load_default()

        # Draw boxes and labels
        for line in aligned_lines:
            bbox = line.bbox

            # Draw rectangle
            draw.rectangle(
                [bbox.x, bbox.y, bbox.x2, bbox.y2],
                outline="red",
                width=2,
            )

            # Draw label
            label = f"{line.line_number}: {line.text[:30]}..."
            draw.text((bbox.x, bbox.y - 15), label, fill="red", font=font)

        if output_path:
            vis_image.save(output_path)

        if show:
            vis_image.show()

        return vis_image
