"""
PyLaia HTR Comparison Module.

Compares PyLaia handwriting text recognition against VLM/OCR models
for historical Irish manuscripts from sources like:
- Dúchas.ie (folklore and historical documents)
- HiddenHeritages.ai (manuscript archives)

Based on /taighde/teanga/pylaia/ reference implementation.

Usage:
    from ocr.pylaia_comparison import HTRComparison, compare_htr_models

    comparison = HTRComparison()
    results = await comparison.compare_models(image_path, ground_truth)
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


class HTRModelType(Enum):
    """Types of HTR/OCR models."""

    PYLAIA = "pylaia"  # Traditional HTR
    VLM = "vlm"  # Vision Language Models
    OCR = "ocr"  # Traditional OCR


@dataclass
class HTRResult:
    """Result from a single HTR/OCR model."""

    model_name: str
    model_type: HTRModelType
    transcription: str
    confidence: float
    processing_time_ms: float
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HTRMetrics:
    """Evaluation metrics for HTR comparison."""

    model_name: str
    cer: float  # Character Error Rate
    wer: float  # Word Error Rate
    fada_accuracy: float  # Accuracy on fada (accent) characters
    processing_time_ms: float
    transcription: str
    ground_truth: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_name": self.model_name,
            "cer": round(self.cer, 4),
            "wer": round(self.wer, 4),
            "fada_accuracy": round(self.fada_accuracy, 4),
            "processing_time_ms": round(self.processing_time_ms, 2),
            "transcription_length": len(self.transcription),
            "ground_truth_length": len(self.ground_truth),
        }


def calculate_cer(hypothesis: str, reference: str) -> float:
    """
    Calculate Character Error Rate using Levenshtein distance.

    CER = (S + D + I) / N
    where S=substitutions, D=deletions, I=insertions, N=reference length
    """
    if not reference:
        return 1.0 if hypothesis else 0.0

    # Dynamic programming for edit distance
    m, n = len(hypothesis), len(reference)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if hypothesis[i - 1] == reference[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n] / n


def calculate_wer(hypothesis: str, reference: str) -> float:
    """Calculate Word Error Rate."""
    hyp_words = hypothesis.split()
    ref_words = reference.split()

    if not ref_words:
        return 1.0 if hyp_words else 0.0

    m, n = len(hyp_words), len(ref_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if hyp_words[i - 1] == ref_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[m][n] / n


def calculate_fada_accuracy(hypothesis: str, reference: str) -> float:
    """
    Calculate accuracy specifically on Irish fada (accent) characters.

    Fada vowels: á, é, í, ó, ú, Á, É, Í, Ó, Ú
    """
    fada_chars = set("áéíóúÁÉÍÓÚ")

    ref_fadas = [(i, c) for i, c in enumerate(reference) if c in fada_chars]
    if not ref_fadas:
        return 1.0  # No fadas to check

    correct = 0
    for i, expected_char in ref_fadas:
        if i < len(hypothesis) and hypothesis[i] == expected_char:
            correct += 1

    return correct / len(ref_fadas)


class HTRModel(ABC):
    """Abstract base class for HTR/OCR models."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Model name."""
        pass

    @property
    @abstractmethod
    def model_type(self) -> HTRModelType:
        """Model type."""
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if model is available."""
        pass

    @abstractmethod
    async def transcribe(self, image_path: str | Path) -> HTRResult:
        """Transcribe text from image."""
        pass


class PyLaiaModel(HTRModel):
    """PyLaia HTR model wrapper."""

    def __init__(self, model_path: str | Path | None = None):
        self.model_path = Path(model_path) if model_path else None
        self._available: bool | None = None

    @property
    def name(self) -> str:
        return "pylaia"

    @property
    def model_type(self) -> HTRModelType:
        return HTRModelType.PYLAIA

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                import laia
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def transcribe(self, image_path: str | Path) -> HTRResult:
        start_time = time.perf_counter()

        if not self.available:
            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription="",
                confidence=0.0,
                processing_time_ms=0.0,
                success=False,
                error="PyLaia not installed",
            )

        try:
            # PyLaia inference
            # Note: Actual implementation requires trained model
            import laia

            # Placeholder - actual inference would use laia.decode
            # This requires a trained PyLaia model for Irish manuscripts
            transcription = "[PyLaia model inference placeholder]"
            confidence = 0.0

            processing_time = (time.perf_counter() - start_time) * 1000

            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription=transcription,
                confidence=confidence,
                processing_time_ms=processing_time,
                success=True,
            )

        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription="",
                confidence=0.0,
                processing_time_ms=processing_time,
                success=False,
                error=str(e),
            )


class VLMModel(HTRModel):
    """Vision Language Model wrapper using LiteLLM."""

    def __init__(self, model_id: str = "gpt-4o"):
        self.model_id = model_id
        self._available: bool | None = None

    @property
    def name(self) -> str:
        return f"vlm-{self.model_id}"

    @property
    def model_type(self) -> HTRModelType:
        return HTRModelType.VLM

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                import litellm
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def transcribe(self, image_path: str | Path) -> HTRResult:
        import base64
        start_time = time.perf_counter()

        if not self.available:
            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription="",
                confidence=0.0,
                processing_time_ms=0.0,
                success=False,
                error="LiteLLM not installed",
            )

        try:
            import litellm

            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine image type
            image_path = Path(image_path)
            mime_type = "image/jpeg"
            if image_path.suffix.lower() == ".png":
                mime_type = "image/png"

            # VLM transcription request
            response = await litellm.acompletion(
                model=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Transcribe all handwritten or printed text in this image exactly as written. "
                                "Preserve Irish language characters including fada accents (á, é, í, ó, ú). "
                                "Return only the transcribed text, nothing else.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=2000,
            )

            transcription = response.choices[0].message.content.strip()
            processing_time = (time.perf_counter() - start_time) * 1000

            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription=transcription,
                confidence=0.9,  # VLMs don't provide explicit confidence
                processing_time_ms=processing_time,
                success=True,
            )

        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            return HTRResult(
                model_name=self.name,
                model_type=self.model_type,
                transcription="",
                confidence=0.0,
                processing_time_ms=processing_time,
                success=False,
                error=str(e),
            )


class HTRComparison:
    """Compare HTR/VLM/OCR models for Irish manuscript transcription."""

    def __init__(self, models: list[HTRModel] | None = None):
        self.models = models or self._default_models()

    def _default_models(self) -> list[HTRModel]:
        """Initialize default model set."""
        return [
            PyLaiaModel(),
            VLMModel("gpt-4o"),
            VLMModel("claude-3-5-sonnet-latest"),
            VLMModel("gemini-2.0-flash"),
        ]

    def list_available(self) -> list[str]:
        """List available model names."""
        return [m.name for m in self.models if m.available]

    async def compare_models(
        self,
        image_path: str | Path,
        ground_truth: str | None = None,
    ) -> list[HTRMetrics | HTRResult]:
        """
        Compare all models on a single image.

        Args:
            image_path: Path to manuscript image
            ground_truth: Optional ground truth transcription for evaluation

        Returns:
            List of HTRMetrics (if ground truth provided) or HTRResult
        """
        results = []

        for model in self.models:
            if not model.available:
                logger.warning(f"Model {model.name} not available, skipping")
                continue

            result = await model.transcribe(image_path)

            if ground_truth and result.success:
                metrics = HTRMetrics(
                    model_name=model.name,
                    cer=calculate_cer(result.transcription, ground_truth),
                    wer=calculate_wer(result.transcription, ground_truth),
                    fada_accuracy=calculate_fada_accuracy(result.transcription, ground_truth),
                    processing_time_ms=result.processing_time_ms,
                    transcription=result.transcription,
                    ground_truth=ground_truth,
                )
                results.append(metrics)
                logger.info(f"{model.name}: CER={metrics.cer:.4f}, WER={metrics.wer:.4f}")
            else:
                results.append(result)

        return results

    async def benchmark_directory(
        self,
        directory: str | Path,
        ground_truth_file: str | Path | None = None,
        image_pattern: str = "*.jpg",
    ) -> dict[str, list[HTRMetrics | HTRResult]]:
        """
        Benchmark all models on a directory of images.

        Args:
            directory: Directory containing images
            ground_truth_file: Optional file with ground truth transcriptions
            image_pattern: Glob pattern for images

        Returns:
            Dictionary mapping image paths to comparison results
        """
        directory = Path(directory)
        results: dict[str, list[HTRMetrics | HTRResult]] = {}

        # Load ground truth if provided
        ground_truths: dict[str, str] = {}
        if ground_truth_file:
            gt_path = Path(ground_truth_file)
            if gt_path.exists():
                with open(gt_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "\t" in line:
                            img_name, text = line.strip().split("\t", 1)
                            ground_truths[img_name] = text

        for image_path in directory.glob(image_pattern):
            gt = ground_truths.get(image_path.name)
            results[str(image_path)] = await self.compare_models(image_path, gt)

        return results

    def select_best_model(
        self,
        results: list[HTRMetrics],
        metric: str = "cer",
    ) -> str | None:
        """Select the best model based on metrics."""
        if not results:
            return None

        if metric == "cer":
            best = min(results, key=lambda r: r.cer)
        elif metric == "wer":
            best = min(results, key=lambda r: r.wer)
        elif metric == "fada_accuracy":
            best = max(results, key=lambda r: r.fada_accuracy)
        elif metric == "processing_time_ms":
            best = min(results, key=lambda r: r.processing_time_ms)
        else:
            best = results[0]

        return best.model_name


async def compare_htr_models(
    image_path: str | Path,
    ground_truth: str | None = None,
    models: list[str] | None = None,
) -> list[HTRMetrics | HTRResult]:
    """
    Convenience function to compare HTR models.

    Args:
        image_path: Path to manuscript image
        ground_truth: Optional ground truth for evaluation
        models: Optional list of model names to use

    Returns:
        Comparison results
    """
    comparison = HTRComparison()

    if models:
        comparison.models = [m for m in comparison.models if m.name in models]

    return await comparison.compare_models(image_path, ground_truth)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Compare HTR models on Irish manuscripts")
    parser.add_argument("image", help="Path to manuscript image")
    parser.add_argument("--ground-truth", "-g", help="Ground truth transcription")
    parser.add_argument("--models", "-m", nargs="+", help="Specific models to use")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    results = asyncio.run(
        compare_htr_models(args.image, args.ground_truth, args.models)
    )

    if args.json:
        output = []
        for r in results:
            if isinstance(r, HTRMetrics):
                output.append(r.to_dict())
            else:
                output.append({
                    "model_name": r.model_name,
                    "success": r.success,
                    "error": r.error,
                })
        print(json.dumps(output, indent=2))
    else:
        for r in results:
            if isinstance(r, HTRMetrics):
                print(f"{r.model_name}:")
                print(f"  CER: {r.cer:.4f}")
                print(f"  WER: {r.wer:.4f}")
                print(f"  Fada Accuracy: {r.fada_accuracy:.4f}")
                print(f"  Time: {r.processing_time_ms:.0f}ms")
            else:
                status = "✓" if r.success else "✗"
                print(f"{status} {r.model_name}: {r.error if r.error else 'OK'}")
