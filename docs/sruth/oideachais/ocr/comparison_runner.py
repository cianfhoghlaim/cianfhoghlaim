"""
OCR Model Comparison Runner.

Runs multiple OCR models on the same images and compares results
using Gaelic-specific metrics.

Usage:
    from ocr import ComparisonRunner, ModelRegistry

    registry = ModelRegistry()
    runner = ComparisonRunner(registry)

    # Compare models on an image
    result = runner.compare_single(
        image=pil_image,
        ground_truth="Bhí sé ag dul abhaile",
        models=["qwen2.5-vl-7b", "gpt-4o"],
    )

    # Print comparison
    for model_name, output in result.outputs.items():
        print(f"{model_name}: CER={output.cer:.2%}")
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from .model_registry import ModelRegistry, OCRModel
from .gaelic_metrics import GaelicMetrics, GaelicEvaluationResult


@dataclass
class ModelOutput:
    """Output from a single model."""

    model_name: str
    transcription: str
    cer: float
    wer: float
    evaluation: GaelicEvaluationResult | None = None
    latency_ms: float = 0.0
    usage: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_name": self.model_name,
            "transcription": self.transcription,
            "cer": self.cer,
            "wer": self.wer,
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "latency_ms": self.latency_ms,
            "usage": self.usage,
            "error": self.error,
        }


@dataclass
class ComparisonResult:
    """Result of comparing multiple models."""

    image_id: str
    ground_truth: str
    outputs: dict[str, ModelOutput]
    best_model: str
    best_cer: float
    comparison_time: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "image_id": self.image_id,
            "ground_truth": self.ground_truth,
            "outputs": {k: v.to_dict() for k, v in self.outputs.items()},
            "best_model": self.best_model,
            "best_cer": self.best_cer,
            "comparison_time": self.comparison_time,
            "metadata": self.metadata,
        }

    def get_ranking(self) -> list[tuple[str, float]]:
        """Get models ranked by CER (best first)."""
        return sorted(
            [(name, output.cer) for name, output in self.outputs.items()],
            key=lambda x: x[1],
        )


class ComparisonRunner:
    """
    Run OCR comparisons across multiple models.
    """

    def __init__(
        self,
        registry: ModelRegistry | None = None,
        metrics: GaelicMetrics | None = None,
        max_workers: int = 4,
    ):
        """
        Initialize comparison runner.

        Args:
            registry: Model registry (creates default if None)
            metrics: Gaelic metrics calculator
            max_workers: Max parallel model runs
        """
        self.registry = registry or ModelRegistry()
        self.metrics = metrics or GaelicMetrics()
        self.max_workers = max_workers

    def compare_single(
        self,
        image: Any,
        ground_truth: str,
        models: list[str] | None = None,
        parallel: bool = True,
        prompt: str | None = None,
    ) -> ComparisonResult:
        """
        Compare models on a single image.

        Args:
            image: PIL Image or numpy array
            ground_truth: Reference transcription
            models: Model names to compare (default: all local)
            parallel: Run models in parallel
            prompt: Custom OCR prompt

        Returns:
            ComparisonResult with all model outputs
        """
        if models is None:
            models = [m.name for m in self.registry.get_local_models()]

        outputs: dict[str, ModelOutput] = {}

        if parallel:
            outputs = self._run_parallel(image, ground_truth, models, prompt)
        else:
            outputs = self._run_sequential(image, ground_truth, models, prompt)

        # Find best model
        best_model = min(outputs.items(), key=lambda x: x[1].cer)

        return ComparisonResult(
            image_id=f"img_{hash(str(image))[:8]}",
            ground_truth=ground_truth,
            outputs=outputs,
            best_model=best_model[0],
            best_cer=best_model[1].cer,
            comparison_time=datetime.now().isoformat(),
        )

    def _run_single_model(
        self,
        model_name: str,
        image: Any,
        ground_truth: str,
        prompt: str | None,
    ) -> ModelOutput:
        """Run a single model and evaluate."""
        try:
            model = self.registry.get_model(model_name)

            start_time = time.time()
            result = model.transcribe(image, prompt=prompt)
            latency_ms = (time.time() - start_time) * 1000

            transcription = result.get("transcription", "")
            evaluation = self.metrics.evaluate(transcription, ground_truth)

            return ModelOutput(
                model_name=model_name,
                transcription=transcription,
                cer=evaluation.cer,
                wer=evaluation.wer,
                evaluation=evaluation,
                latency_ms=latency_ms,
                usage=result.get("usage", {}),
            )

        except Exception as e:
            return ModelOutput(
                model_name=model_name,
                transcription="",
                cer=1.0,
                wer=1.0,
                error=str(e),
            )

    def _run_parallel(
        self,
        image: Any,
        ground_truth: str,
        models: list[str],
        prompt: str | None,
    ) -> dict[str, ModelOutput]:
        """Run models in parallel."""
        outputs = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._run_single_model, model, image, ground_truth, prompt): model
                for model in models
            }

            for future in as_completed(futures):
                model_name = futures[future]
                try:
                    output = future.result()
                    outputs[model_name] = output
                except Exception as e:
                    outputs[model_name] = ModelOutput(
                        model_name=model_name,
                        transcription="",
                        cer=1.0,
                        wer=1.0,
                        error=str(e),
                    )

        return outputs

    def _run_sequential(
        self,
        image: Any,
        ground_truth: str,
        models: list[str],
        prompt: str | None,
    ) -> dict[str, ModelOutput]:
        """Run models sequentially."""
        outputs = {}

        for model_name in models:
            output = self._run_single_model(model_name, image, ground_truth, prompt)
            outputs[model_name] = output

        return outputs

    def compare_batch(
        self,
        images: list[Any],
        ground_truths: list[str],
        models: list[str] | None = None,
        parallel: bool = True,
        progress_callback: Any | None = None,
    ) -> list[ComparisonResult]:
        """
        Compare models on a batch of images.

        Args:
            images: List of images
            ground_truths: List of reference transcriptions
            models: Model names to compare
            parallel: Run models in parallel
            progress_callback: Optional callback(current, total)

        Returns:
            List of ComparisonResult objects
        """
        if len(images) != len(ground_truths):
            raise ValueError("Images and ground truths must have same length")

        results = []
        total = len(images)

        for i, (image, gt) in enumerate(zip(images, ground_truths)):
            result = self.compare_single(image, gt, models, parallel)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total)

        return results

    def get_aggregate_metrics(
        self,
        results: list[ComparisonResult],
    ) -> dict[str, dict[str, float]]:
        """
        Calculate aggregate metrics across all comparisons.

        Args:
            results: List of comparison results

        Returns:
            Dictionary of model -> aggregated metrics
        """
        model_metrics: dict[str, list[dict[str, float]]] = {}

        for result in results:
            for model_name, output in result.outputs.items():
                if model_name not in model_metrics:
                    model_metrics[model_name] = []

                model_metrics[model_name].append(
                    {
                        "cer": output.cer,
                        "wer": output.wer,
                        "latency_ms": output.latency_ms,
                        "tironian_accuracy": output.evaluation.tironian_accuracy
                        if output.evaluation
                        else 0.0,
                        "fada_accuracy": output.evaluation.fada_accuracy
                        if output.evaluation
                        else 0.0,
                    }
                )

        aggregated = {}

        for model_name, metrics_list in model_metrics.items():
            n = len(metrics_list)
            aggregated[model_name] = {
                "mean_cer": sum(m["cer"] for m in metrics_list) / n,
                "mean_wer": sum(m["wer"] for m in metrics_list) / n,
                "mean_latency_ms": sum(m["latency_ms"] for m in metrics_list) / n,
                "mean_tironian_accuracy": sum(m["tironian_accuracy"] for m in metrics_list) / n,
                "mean_fada_accuracy": sum(m["fada_accuracy"] for m in metrics_list) / n,
                "sample_count": n,
            }

        return aggregated

    def export_results(
        self,
        results: list[ComparisonResult],
        output_path: str | Path,
        format: str = "json",
    ) -> Path:
        """
        Export comparison results to file.

        Args:
            results: List of comparison results
            output_path: Output file path
            format: Output format (json, csv)

        Returns:
            Path to output file
        """
        import json

        output_path = Path(output_path)

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "results": [r.to_dict() for r in results],
                        "aggregate": self.get_aggregate_metrics(results),
                        "exported_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

        elif format == "csv":
            import csv

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header
                models = set()
                for r in results:
                    models.update(r.outputs.keys())
                models = sorted(models)

                header = ["image_id", "ground_truth"]
                for model in models:
                    header.extend([f"{model}_transcription", f"{model}_cer", f"{model}_wer"])
                writer.writerow(header)

                # Data rows
                for result in results:
                    row = [result.image_id, result.ground_truth]
                    for model in models:
                        if model in result.outputs:
                            output = result.outputs[model]
                            row.extend([output.transcription, output.cer, output.wer])
                        else:
                            row.extend(["", "", ""])
                    writer.writerow(row)

        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path
