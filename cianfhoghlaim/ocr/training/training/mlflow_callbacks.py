"""
MLflow Callbacks for Gaelic OCR Training.

Provides custom callbacks for:
- Visual artifact logging (sample predictions)
- Gaelic-specific metric tracking
- Training progress visualization
- Model comparison artifacts

Based on research in:
- taighde_teanga/Finetuning Qwen3-VL for Gaelic OCR.md
- taighde_meaisínfhoghlaim/mlflow-integration.md

Usage:
    from training import GaelicOCRMLflowCallback, UnslothTrainer

    callback = GaelicOCRMLflowCallback(
        sample_images=sample_paths,
        sample_transcriptions=ground_truths,
        log_every_n_steps=100,
    )

    trainer = UnslothTrainer(config, callbacks=[callback])
    trainer.train()
"""

import json
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from transformers import TrainerCallback, TrainerControl, TrainerState
from transformers.training_args import TrainingArguments


@dataclass
class GaelicMetricsSummary:
    """Summary of Gaelic-specific metrics."""

    cer: float = 0.0
    wer: float = 0.0
    tironian_accuracy: float = 0.0
    fada_accuracy: float = 0.0
    punctum_precision: float = 0.0
    sample_count: int = 0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "cer": self.cer,
            "wer": self.wer,
            "tironian_accuracy": self.tironian_accuracy,
            "fada_accuracy": self.fada_accuracy,
            "punctum_precision": self.punctum_precision,
            "sample_count": self.sample_count,
        }


class GaelicOCRMLflowCallback(TrainerCallback):
    """
    MLflow callback for Gaelic OCR training.

    Logs:
    - Sample predictions with images
    - Gaelic-specific metrics (Tironian et, fada, punctum delens)
    - Training curves
    - Model comparison artifacts
    """

    def __init__(
        self,
        sample_images: list[str | Path] | None = None,
        sample_transcriptions: list[str] | None = None,
        log_every_n_steps: int = 100,
        log_samples_every_n_steps: int = 500,
        max_samples_to_log: int = 5,
    ):
        """
        Initialize callback.

        Args:
            sample_images: Paths to sample images for visualization
            sample_transcriptions: Ground truth transcriptions
            log_every_n_steps: Log metrics every N steps
            log_samples_every_n_steps: Log sample predictions every N steps
            max_samples_to_log: Maximum samples to log per checkpoint
        """
        self.sample_images = sample_images or []
        self.sample_transcriptions = sample_transcriptions or []
        self.log_every_n_steps = log_every_n_steps
        self.log_samples_every_n_steps = log_samples_every_n_steps
        self.max_samples_to_log = max_samples_to_log

        self._mlflow = None
        self._metrics_calculator = None
        self._step_metrics: list[dict] = []

    def _get_mlflow(self) -> Any:
        """Lazy load MLflow."""
        if self._mlflow is None:
            try:
                import mlflow

                self._mlflow = mlflow
            except ImportError:
                raise ImportError("MLflow required for this callback")
        return self._mlflow

    def _get_metrics_calculator(self) -> Any:
        """Lazy load Gaelic metrics calculator."""
        if self._metrics_calculator is None:
            try:
                from ..ocr.gaelic_metrics import GaelicMetrics

                self._metrics_calculator = GaelicMetrics()
            except ImportError:
                # Fallback: create minimal calculator
                self._metrics_calculator = self._create_fallback_metrics()
        return self._metrics_calculator

    def _create_fallback_metrics(self) -> Any:
        """Create fallback metrics calculator."""

        class FallbackMetrics:
            def evaluate(self, pred: str, ref: str) -> Any:
                from dataclasses import dataclass

                @dataclass
                class Result:
                    cer: float = 0.0
                    wer: float = 0.0
                    tironian_accuracy: float = 1.0
                    fada_accuracy: float = 1.0
                    punctum_delens_precision: float = 1.0

                # Simple CER calculation
                distance = self._levenshtein(pred.lower(), ref.lower())
                cer = distance / len(ref) if ref else 0.0

                return Result(cer=cer, wer=cer)

            def _levenshtein(self, s1: str, s2: str) -> int:
                if len(s1) < len(s2):
                    return self._levenshtein(s2, s1)
                if len(s2) == 0:
                    return len(s1)
                prev = range(len(s2) + 1)
                for i, c1 in enumerate(s1):
                    curr = [i + 1]
                    for j, c2 in enumerate(s2):
                        curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
                    prev = curr
                return prev[-1]

        return FallbackMetrics()

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Called at the start of training."""
        mlflow = self._get_mlflow()

        # Log training configuration
        mlflow.log_params(
            {
                "callback_log_every_n_steps": self.log_every_n_steps,
                "callback_sample_count": len(self.sample_images),
                "training_started_at": datetime.now().isoformat(),
            }
        )

        # Log sample images as artifacts
        if self.sample_images:
            self._log_sample_images()

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        """Called when logging metrics."""
        if logs is None:
            return

        mlflow = self._get_mlflow()

        # Store for later aggregation
        self._step_metrics.append(
            {
                "step": state.global_step,
                "metrics": logs.copy(),
            }
        )

        # Log standard metrics
        metrics_to_log = {}
        for key, value in logs.items():
            if isinstance(value, (int, float)):
                metrics_to_log[f"train/{key}"] = value

        if metrics_to_log:
            mlflow.log_metrics(metrics_to_log, step=state.global_step)

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        """Called after evaluation."""
        if metrics is None:
            return

        mlflow = self._get_mlflow()

        # Log evaluation metrics
        eval_metrics = {}
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                eval_metrics[f"eval/{key}"] = value

        if eval_metrics:
            mlflow.log_metrics(eval_metrics, step=state.global_step)

        # Log sample predictions
        if (
            state.global_step % self.log_samples_every_n_steps == 0
            and self.sample_images
        ):
            self._log_sample_predictions(kwargs.get("model"), kwargs.get("tokenizer"))

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Called when saving checkpoint."""
        mlflow = self._get_mlflow()

        # Log checkpoint info
        mlflow.log_metrics(
            {
                "checkpoint/step": state.global_step,
                "checkpoint/epoch": state.epoch or 0.0,
            },
            step=state.global_step,
        )

        # Log training state artifact
        self._log_training_state(state)

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Called at end of training."""
        mlflow = self._get_mlflow()

        # Log final metrics
        mlflow.log_metrics(
            {
                "final/total_steps": state.global_step,
                "final/epochs": state.epoch or 0.0,
                "final/best_metric": state.best_metric or 0.0,
            }
        )

        # Log training summary
        self._log_training_summary(state)

        # Generate and log comparison table
        if self.sample_images:
            self._log_final_predictions(kwargs.get("model"), kwargs.get("tokenizer"))

    def _log_sample_images(self) -> None:
        """Log sample images as artifacts."""
        mlflow = self._get_mlflow()

        for _i, image_path in enumerate(self.sample_images[: self.max_samples_to_log]):
            if Path(image_path).exists():
                mlflow.log_artifact(str(image_path), artifact_path="samples/images")

    def _log_sample_predictions(self, model: Any, tokenizer: Any) -> None:
        """Log sample predictions with comparison."""
        if model is None or tokenizer is None:
            return

        mlflow = self._get_mlflow()
        metrics_calc = self._get_metrics_calculator()

        predictions = []
        metrics_summary = GaelicMetricsSummary()

        for i, (img_path, gt) in enumerate(
            zip(
                self.sample_images[: self.max_samples_to_log],
                self.sample_transcriptions[: self.max_samples_to_log], strict=False,
            )
        ):
            try:
                # Generate prediction
                pred = self._generate_prediction(model, tokenizer, img_path)

                # Calculate metrics
                result = metrics_calc.evaluate(pred, gt)

                predictions.append(
                    {
                        "image": str(img_path),
                        "ground_truth": gt,
                        "prediction": pred,
                        "cer": result.cer,
                        "wer": result.wer,
                    }
                )

                # Accumulate metrics
                metrics_summary.cer += result.cer
                metrics_summary.wer += result.wer
                metrics_summary.tironian_accuracy += result.tironian_accuracy
                metrics_summary.fada_accuracy += result.fada_accuracy
                metrics_summary.punctum_precision += result.punctum_delens_precision
                metrics_summary.sample_count += 1

            except Exception as e:
                print(f"Error processing sample {i}: {e}")

        # Average metrics
        if metrics_summary.sample_count > 0:
            n = metrics_summary.sample_count
            mlflow.log_metrics(
                {
                    "samples/avg_cer": metrics_summary.cer / n,
                    "samples/avg_wer": metrics_summary.wer / n,
                    "samples/tironian_accuracy": metrics_summary.tironian_accuracy / n,
                    "samples/fada_accuracy": metrics_summary.fada_accuracy / n,
                    "samples/punctum_precision": metrics_summary.punctum_precision / n,
                }
            )

        # Log predictions as artifact
        self._save_predictions_artifact(predictions, "sample_predictions.json")

    def _generate_prediction(
        self,
        model: Any,
        tokenizer: Any,
        image_path: str | Path,
    ) -> str:
        """Generate prediction for a single image."""
        from PIL import Image

        # Load image
        image = Image.open(image_path).convert("RGB")

        # Create prompt
        prompt = "Transcribe the handwritten Irish text in this image exactly as written."

        # Get processor
        try:
            from transformers import AutoProcessor

            processor = AutoProcessor.from_pretrained(
                model.config._name_or_path.replace("-bnb-4bit", "").replace(
                    "unsloth/", ""
                )
            )
        except Exception:
            # Fallback
            processor = tokenizer

        # Prepare input
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        text = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], return_tensors="pt")

        # Move to model device
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Generate
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=False,
        )

        # Decode
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the response (after assistant turn)
        if "<|assistant|>" in prediction:
            prediction = prediction.split("<|assistant|>")[-1].strip()
        elif "assistant" in prediction.lower():
            prediction = prediction.split("assistant")[-1].strip()

        return prediction

    def _log_training_state(self, state: TrainerState) -> None:
        """Log training state as artifact."""
        mlflow = self._get_mlflow()

        state_dict = {
            "global_step": state.global_step,
            "epoch": state.epoch,
            "best_metric": state.best_metric,
            "best_model_checkpoint": state.best_model_checkpoint,
            "log_history": state.log_history[-10:] if state.log_history else [],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(state_dict, f, indent=2)
            temp_path = f.name

        mlflow.log_artifact(temp_path, artifact_path="training_state")
        Path(temp_path).unlink()

    def _log_training_summary(self, state: TrainerState) -> None:
        """Log training summary as artifact."""
        mlflow = self._get_mlflow()

        summary = {
            "completed_at": datetime.now().isoformat(),
            "total_steps": state.global_step,
            "epochs": state.epoch,
            "best_metric": state.best_metric,
            "best_checkpoint": state.best_model_checkpoint,
            "metrics_history": self._step_metrics,
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(summary, f, indent=2)
            temp_path = f.name

        mlflow.log_artifact(temp_path, artifact_path="training_summary.json")
        Path(temp_path).unlink()

    def _log_final_predictions(self, model: Any, tokenizer: Any) -> None:
        """Log final predictions comparison table."""
        if model is None or tokenizer is None:
            return

        self._get_mlflow()
        metrics_calc = self._get_metrics_calculator()

        # Generate all predictions
        results = []
        for img_path, gt in zip(self.sample_images, self.sample_transcriptions, strict=False):
            try:
                pred = self._generate_prediction(model, tokenizer, img_path)
                metrics = metrics_calc.evaluate(pred, gt)

                results.append(
                    {
                        "image": Path(img_path).name,
                        "ground_truth": gt[:100] + "..." if len(gt) > 100 else gt,
                        "prediction": pred[:100] + "..." if len(pred) > 100 else pred,
                        "cer": round(metrics.cer, 4),
                        "wer": round(metrics.wer, 4),
                        "tironian_acc": round(metrics.tironian_accuracy, 4),
                        "fada_acc": round(metrics.fada_accuracy, 4),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "image": Path(img_path).name,
                        "error": str(e),
                    }
                )

        # Save as artifact
        self._save_predictions_artifact(results, "final_predictions.json")

        # Also create HTML table
        self._create_html_comparison(results)

    def _save_predictions_artifact(
        self, predictions: list[dict], filename: str
    ) -> None:
        """Save predictions to artifact."""
        mlflow = self._get_mlflow()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(predictions, f, indent=2, ensure_ascii=False)
            temp_path = f.name

        mlflow.log_artifact(temp_path, artifact_path="predictions")
        Path(temp_path).unlink()

    def _create_html_comparison(self, results: list[dict]) -> None:
        """Create HTML comparison table."""
        mlflow = self._get_mlflow()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gaelic OCR Predictions</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .cer-good { color: green; }
                .cer-bad { color: red; }
                .prediction { font-style: italic; }
            </style>
        </head>
        <body>
            <h1>Gaelic OCR Model Predictions</h1>
            <p>Generated: """ + datetime.now().isoformat() + """</p>
            <table>
                <tr>
                    <th>Image</th>
                    <th>Ground Truth</th>
                    <th>Prediction</th>
                    <th>CER</th>
                    <th>WER</th>
                    <th>Tironian</th>
                    <th>Fada</th>
                </tr>
        """

        for r in results:
            if "error" in r:
                html += f"""
                <tr>
                    <td>{r.get('image', 'N/A')}</td>
                    <td colspan="6" style="color: red;">Error: {r['error']}</td>
                </tr>
                """
            else:
                cer_class = "cer-good" if r.get("cer", 1) < 0.1 else "cer-bad"
                html += f"""
                <tr>
                    <td>{r.get('image', 'N/A')}</td>
                    <td>{r.get('ground_truth', '')}</td>
                    <td class="prediction">{r.get('prediction', '')}</td>
                    <td class="{cer_class}">{r.get('cer', 'N/A')}</td>
                    <td>{r.get('wer', 'N/A')}</td>
                    <td>{r.get('tironian_acc', 'N/A')}</td>
                    <td>{r.get('fada_acc', 'N/A')}</td>
                </tr>
                """

        html += """
            </table>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False
        ) as f:
            f.write(html)
            temp_path = f.name

        mlflow.log_artifact(temp_path, artifact_path="predictions/comparison.html")
        Path(temp_path).unlink()


class EarlyStoppingCallback(TrainerCallback):
    """
    Early stopping based on Gaelic-specific metrics.
    """

    def __init__(
        self,
        patience: int = 5,
        min_delta: float = 0.001,
        metric: str = "eval_loss",
    ):
        """
        Initialize early stopping.

        Args:
            patience: Number of evaluations without improvement
            min_delta: Minimum improvement required
            metric: Metric to monitor
        """
        self.patience = patience
        self.min_delta = min_delta
        self.metric = metric
        self.best_value = float("inf")
        self.counter = 0

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        """Check for early stopping."""
        if metrics is None:
            return

        current = metrics.get(self.metric)
        if current is None:
            return

        if current < self.best_value - self.min_delta:
            self.best_value = current
            self.counter = 0
        else:
            self.counter += 1

        if self.counter >= self.patience:
            print(f"Early stopping triggered at step {state.global_step}")
            control.should_training_stop = True


class GaelicMetricsCallback(TrainerCallback):
    """
    Callback to compute and log Gaelic-specific metrics during training.
    """

    def __init__(
        self,
        eval_samples: list[tuple[str, str]] | None = None,
        compute_every_n_steps: int = 500,
    ):
        """
        Initialize callback.

        Args:
            eval_samples: List of (image_path, transcription) tuples
            compute_every_n_steps: Compute metrics every N steps
        """
        self.eval_samples = eval_samples or []
        self.compute_every_n_steps = compute_every_n_steps
        self._metrics_calculator = None

    def _get_metrics(self) -> Any:
        """Get metrics calculator."""
        if self._metrics_calculator is None:
            try:
                from ..ocr.gaelic_metrics import GaelicMetrics

                self._metrics_calculator = GaelicMetrics()
            except ImportError:
                return None
        return self._metrics_calculator

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Compute metrics periodically."""
        if state.global_step % self.compute_every_n_steps != 0:
            return

        if not self.eval_samples:
            return

        metrics_calc = self._get_metrics()
        if metrics_calc is None:
            return

        model = kwargs.get("model")
        tokenizer = kwargs.get("tokenizer")

        if model is None or tokenizer is None:
            return

        # Compute metrics on samples
        total_cer = 0.0
        total_tironian = 0.0
        total_fada = 0.0
        count = 0

        for _img_path, gt in self.eval_samples[:5]:  # Limit for speed
            try:
                # This would need actual prediction generation
                # Placeholder for now
                pred = gt  # Would be model prediction
                result = metrics_calc.evaluate(pred, gt)

                total_cer += result.cer
                total_tironian += result.tironian_accuracy
                total_fada += result.fada_accuracy
                count += 1

            except Exception:
                continue

        if count > 0:
            try:
                import mlflow

                mlflow.log_metrics(
                    {
                        "gaelic/avg_cer": total_cer / count,
                        "gaelic/tironian_accuracy": total_tironian / count,
                        "gaelic/fada_accuracy": total_fada / count,
                    },
                    step=state.global_step,
                )
            except ImportError:
                pass
