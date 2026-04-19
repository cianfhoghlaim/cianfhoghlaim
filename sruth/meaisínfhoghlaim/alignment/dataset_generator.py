"""
Training Dataset Generator for OCR Fine-tuning.

Generates JSONL datasets for Unsloth training from aligned images
and transcriptions.

Output Formats:
- Dense OCR (crop-based): Individual line crops with transcriptions
- Visual Grounding (full page): Full page with bounding box annotations
- Conversation format: Multi-turn QA for instruction tuning

Includes:
- Data augmentation (blur, noise, perspective warp)
- Tironian note handling (⁊ → "agus" substitution)
- Quality filtering
- Train/val/test splits

Usage:
    from alignment import DatasetGenerator

    generator = DatasetGenerator(output_dir="./training_data")
    generator.add_sample(image, transcription_lines, aligned_lines)
    generator.finalize(train_split=0.8, val_split=0.1)
"""

import base64
import io
import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class TrainingSample:
    """A single training sample."""

    sample_id: str
    image_path: str | None = None
    image_base64: str | None = None
    transcription: str = ""
    lines: list[dict[str, Any]] = field(default_factory=list)
    bbox: dict[str, float] | None = None
    gaelic_features: dict[str, bool] = field(default_factory=dict)
    format_type: str = "dense_ocr"  # dense_ocr, visual_grounding, conversation
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sample_id": self.sample_id,
            "image_path": self.image_path,
            "image_base64": self.image_base64,
            "transcription": self.transcription,
            "lines": self.lines,
            "bbox": self.bbox,
            "gaelic_features": self.gaelic_features,
            "format_type": self.format_type,
            "metadata": self.metadata,
        }

    def to_dense_ocr_format(self) -> dict[str, Any]:
        """Convert to dense OCR training format."""
        return {
            "id": self.sample_id,
            "image": self.image_base64 or self.image_path,
            "conversations": [
                {
                    "role": "user",
                    "content": "Transcribe the handwritten text in this image.",
                },
                {
                    "role": "assistant",
                    "content": self.transcription,
                },
            ],
        }

    def to_visual_grounding_format(self) -> dict[str, Any]:
        """Convert to visual grounding training format."""
        # Format bounding boxes as text
        bbox_text = ""
        for line in self.lines:
            if "bbox" in line:
                b = line["bbox"]
                bbox_text += f"[{b['x']:.0f},{b['y']:.0f},{b['x']+b['width']:.0f},{b['y']+b['height']:.0f}] {line['text']}\n"

        return {
            "id": self.sample_id,
            "image": self.image_base64 or self.image_path,
            "conversations": [
                {
                    "role": "user",
                    "content": "Transcribe the handwritten text and provide bounding boxes for each line.",
                },
                {
                    "role": "assistant",
                    "content": bbox_text.strip(),
                },
            ],
        }

    def to_conversation_format(self) -> dict[str, Any]:
        """Convert to multi-turn conversation format."""
        conversations = [
            {
                "role": "user",
                "content": "What type of document is this?",
            },
            {
                "role": "assistant",
                "content": f"This is a handwritten manuscript page from the Irish folklore collection, written in {self._detect_script_type()}.",
            },
            {
                "role": "user",
                "content": "Please transcribe the text.",
            },
            {
                "role": "assistant",
                "content": self.transcription,
            },
        ]

        # Add Gaelic feature questions if relevant
        if self.gaelic_features.get("has_tironian_et"):
            conversations.extend(
                [
                    {
                        "role": "user",
                        "content": "Are there any special Irish abbreviations?",
                    },
                    {
                        "role": "assistant",
                        "content": "Yes, this text contains the Tironian et (⁊), an ancient Irish abbreviation for 'agus' (and).",
                    },
                ]
            )

        return {
            "id": self.sample_id,
            "image": self.image_base64 or self.image_path,
            "conversations": conversations,
        }

    def _detect_script_type(self) -> str:
        """Detect script type from features."""
        if self.gaelic_features.get("has_seanchlo"):
            return "Cló Gaelach (Gaelic script)"
        elif self.gaelic_features.get("has_punctum_delens"):
            return "modified Roman script with lenition marks"
        else:
            return "Irish cursive handwriting"


class DatasetGenerator:
    """
    Generate training datasets from aligned images and transcriptions.
    """

    def __init__(
        self,
        output_dir: str | Path,
        include_augmentations: bool = True,
        augmentation_factor: int = 3,
        tironian_substitution: bool = True,
        min_line_length: int = 3,
        max_samples: int | None = None,
    ):
        """
        Initialize dataset generator.

        Args:
            output_dir: Directory to save datasets
            include_augmentations: Whether to generate augmented samples
            augmentation_factor: Number of augmented versions per sample
            tironian_substitution: Replace ⁊ with "agus" in some samples
            min_line_length: Minimum characters per line
            max_samples: Maximum samples to generate
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.include_augmentations = include_augmentations
        self.augmentation_factor = augmentation_factor
        self.tironian_substitution = tironian_substitution
        self.min_line_length = min_line_length
        self.max_samples = max_samples

        self.samples: list[TrainingSample] = []
        self._sample_count = 0

    def add_sample(
        self,
        image: Any,
        transcription_lines: list[str],
        aligned_lines: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        format_types: list[str] | None = None,
    ) -> list[TrainingSample]:
        """
        Add a training sample.

        Args:
            image: PIL Image or numpy array
            transcription_lines: List of text lines
            aligned_lines: Optional aligned lines with bounding boxes
            metadata: Additional metadata
            format_types: Output formats (default: all)

        Returns:
            List of generated TrainingSample objects
        """
        from PIL import Image

        if self.max_samples and self._sample_count >= self.max_samples:
            return []

        format_types = format_types or ["dense_ocr", "visual_grounding", "conversation"]
        generated_samples = []

        # Convert image to PIL
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Generate base64 encoding
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Full transcription
        full_transcription = "\n".join(transcription_lines)

        # Detect Gaelic features
        gaelic_features = self._detect_gaelic_features(full_transcription)

        # Generate sample for each format
        for format_type in format_types:
            sample_id = f"sample_{self._sample_count:06d}_{format_type}"

            sample = TrainingSample(
                sample_id=sample_id,
                image_base64=f"data:image/png;base64,{image_base64}",
                transcription=full_transcription,
                lines=[line.to_dict() if hasattr(line, "to_dict") else line for line in (aligned_lines or [])],
                gaelic_features=gaelic_features,
                format_type=format_type,
                metadata=metadata or {},
            )

            self.samples.append(sample)
            generated_samples.append(sample)

            # Generate augmented versions
            if self.include_augmentations:
                augmented = self._generate_augmentations(
                    image, transcription_lines, aligned_lines, format_type
                )
                self.samples.extend(augmented)
                generated_samples.extend(augmented)

        self._sample_count += 1
        return generated_samples

    def add_line_crop(
        self,
        image: Any,
        line_text: str,
        bbox: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TrainingSample:
        """
        Add a single line crop as a training sample.

        Args:
            image: Cropped line image
            line_text: Line transcription
            bbox: Optional bounding box
            metadata: Additional metadata

        Returns:
            Generated TrainingSample
        """
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        sample_id = f"line_{self._sample_count:06d}"

        sample = TrainingSample(
            sample_id=sample_id,
            image_base64=f"data:image/png;base64,{image_base64}",
            transcription=line_text,
            bbox=bbox,
            gaelic_features=self._detect_gaelic_features(line_text),
            format_type="dense_ocr",
            metadata=metadata or {},
        )

        self.samples.append(sample)
        self._sample_count += 1

        return sample

    def _detect_gaelic_features(self, text: str) -> dict[str, bool]:
        """Detect Gaelic script features."""
        return {
            "has_tironian_et": "⁊" in text,
            "has_punctum_delens": any(
                c in text for c in ["ḃ", "ċ", "ḋ", "ḟ", "ġ", "ṁ", "ṗ", "ṡ", "ṫ"]
            ),
            "has_fada": any(c in text for c in ["á", "é", "í", "ó", "ú"]),
            "has_seanchlo": False,  # Would need more sophisticated detection
        }

    def _generate_augmentations(
        self,
        image: Any,
        transcription_lines: list[str],
        aligned_lines: list[dict[str, Any]] | None,
        format_type: str,
    ) -> list[TrainingSample]:
        """Generate augmented versions of a sample."""
        augmented_samples = []

        try:
            from PIL import Image, ImageFilter
        except ImportError:
            return augmented_samples

        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image

        augmentations = [
            ("blur", lambda img: img.filter(ImageFilter.GaussianBlur(radius=1))),
            ("sharpen", lambda img: img.filter(ImageFilter.SHARPEN)),
            ("noise", self._add_salt_pepper_noise),
            ("contrast", self._adjust_contrast),
        ]

        for i in range(min(self.augmentation_factor, len(augmentations))):
            aug_name, aug_func = augmentations[i % len(augmentations)]

            try:
                aug_image = aug_func(pil_image.copy())

                buffered = io.BytesIO()
                aug_image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                # Optionally apply Tironian substitution
                aug_transcription = "\n".join(transcription_lines)
                if self.tironian_substitution and random.random() < 0.3:
                    aug_transcription = aug_transcription.replace("⁊", "agus")

                sample = TrainingSample(
                    sample_id=f"aug_{self._sample_count:06d}_{aug_name}_{format_type}",
                    image_base64=f"data:image/png;base64,{image_base64}",
                    transcription=aug_transcription,
                    lines=[line.to_dict() if hasattr(line, "to_dict") else line for line in (aligned_lines or [])],
                    gaelic_features=self._detect_gaelic_features(aug_transcription),
                    format_type=format_type,
                    metadata={"augmentation": aug_name},
                )

                augmented_samples.append(sample)

            except Exception:
                continue

        return augmented_samples

    def _add_salt_pepper_noise(self, image: Any) -> Any:
        """Add salt and pepper noise to image."""
        from PIL import Image

        img_array = np.array(image)
        noise_mask = np.random.random(img_array.shape[:2])

        img_array[noise_mask < 0.02] = 0  # Salt
        img_array[noise_mask > 0.98] = 255  # Pepper

        return Image.fromarray(img_array)

    def _adjust_contrast(self, image: Any) -> Any:
        """Adjust image contrast."""
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Contrast(image)
        factor = random.uniform(0.8, 1.2)
        return enhancer.enhance(factor)

    def finalize(
        self,
        train_split: float = 0.8,
        val_split: float = 0.1,
        test_split: float = 0.1,
        shuffle: bool = True,
        seed: int = 42,
    ) -> dict[str, Path]:
        """
        Finalize dataset and write to files.

        Args:
            train_split: Fraction for training
            val_split: Fraction for validation
            test_split: Fraction for testing
            shuffle: Whether to shuffle samples
            seed: Random seed for reproducibility

        Returns:
            Dictionary of output file paths
        """
        if shuffle:
            random.seed(seed)
            random.shuffle(self.samples)

        total = len(self.samples)
        train_end = int(total * train_split)
        val_end = train_end + int(total * val_split)

        splits = {
            "train": self.samples[:train_end],
            "val": self.samples[train_end:val_end],
            "test": self.samples[val_end:],
        }

        output_files = {}

        for split_name, split_samples in splits.items():
            if not split_samples:
                continue

            # Write JSONL for each format type
            for format_type in ["dense_ocr", "visual_grounding", "conversation"]:
                format_samples = [s for s in split_samples if s.format_type == format_type]

                if not format_samples:
                    continue

                output_path = self.output_dir / f"{split_name}_{format_type}.jsonl"

                with open(output_path, "w", encoding="utf-8") as f:
                    for sample in format_samples:
                        if format_type == "dense_ocr":
                            record = sample.to_dense_ocr_format()
                        elif format_type == "visual_grounding":
                            record = sample.to_visual_grounding_format()
                        else:
                            record = sample.to_conversation_format()

                        f.write(json.dumps(record, ensure_ascii=False) + "\n")

                output_files[f"{split_name}_{format_type}"] = output_path

        # Write metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_samples": total,
            "splits": {name: len(samples) for name, samples in splits.items()},
            "augmentations_enabled": self.include_augmentations,
            "augmentation_factor": self.augmentation_factor,
            "tironian_substitution": self.tironian_substitution,
        }

        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        output_files["metadata"] = metadata_path

        return output_files

    def get_statistics(self) -> dict[str, Any]:
        """Get dataset statistics."""
        if not self.samples:
            return {"total_samples": 0}

        gaelic_counts = {
            "has_tironian_et": 0,
            "has_punctum_delens": 0,
            "has_fada": 0,
        }

        format_counts = {}
        total_chars = 0
        total_lines = 0

        for sample in self.samples:
            format_counts[sample.format_type] = format_counts.get(sample.format_type, 0) + 1
            total_chars += len(sample.transcription)
            total_lines += len(sample.lines)

            for feature, has_feature in sample.gaelic_features.items():
                if has_feature and feature in gaelic_counts:
                    gaelic_counts[feature] += 1

        return {
            "total_samples": len(self.samples),
            "format_distribution": format_counts,
            "gaelic_feature_counts": gaelic_counts,
            "avg_transcription_length": total_chars / len(self.samples),
            "avg_lines_per_sample": total_lines / len(self.samples) if total_lines > 0 else 0,
        }
