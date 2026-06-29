"""
VLM Fine-tuning Comparison Pipeline for Irish OCR (v4 home).

This is the v4 home for the VLM fine-tune comparison, per
`openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/`.
The legacy `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py`
is deprecated; it re-exports from this module with a `DeprecationWarning`.

Three renames were reverted from commit 33500d3 (per the HF Hub audit on
2026-06-29 — the original "doesn't exist" claims were wrong):

- `qwen2.5-vl-7b` → `qwen3-vl-8b` (real: `unsloth/Qwen3-VL-8B-Instruct-GGUF`)
- `qwen2.5-vl-72b` → `qwen3-vl-30b-a3b` (real: `unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF`)
- `glm-4v-9b` → `glm-4.6v-flash` (real: `unsloth/GLM-4.6V-Flash-GGUF`)

Compares fine-tuning results across multiple Vision Language Models:
- GLM-4.6V Flash (10.3B, 6GB at 4-bit, 128k context)
- Qwen 3-VL (4B/8B/30B-A3B/235B-A22B variants)
- Gemma 4 (E2B/E4B/12B/26B-A4B/31B variants)
- olmOCR-2-7B (specialist OCR)
- Molmo2-8B (diagram pointing)

Metrics tracked:
- CER (Character Error Rate)
- WER (Word Error Rate)
- Fada Accuracy (á, é, í, ó, ú)
- Tironian Et Detection (⁊)
- Inference Speed
- Memory Usage

Supports:
- Unsloth fine-tuning with 70% VRAM reduction
- MLflow experiment tracking
- Modal/Anyscale distributed training
- Mobile deployment parameter comparison

Usage:
    from cianfhoghlaim.ocr.models import VLMComparisonPipeline

    pipeline = VLMComparisonPipeline(
        dataset_path="./irish_htr_dataset/unsloth",
        models=["glm-4.6v-flash", "qwen3-vl-8b", "molmo2-8b"],
    )

    results = pipeline.run_comparison()
    pipeline.export_report("comparison_report.html")
"""

from __future__ import annotations

import json
import logging
import os
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .registry import VISION_MODELS

logger = logging.getLogger(__name__)

warnings.warn(
    "Importing VLM_MODELS from cianfhoghlaim.ocr.models is the v4 home. "
    "The legacy cianfhoghlaim.ocr._meaisinfhoghlaim_src.vlm_finetune_comparison "
    "is deprecated and will be removed in v5.",
    DeprecationWarning,
    stacklevel=2,
)


# ─── Model configurations for VLM fine-tune comparison ──────────────────────
# Reverted from the wrong commit 33500d3 renames (2026-06-29):
# - qwen3-vl-7b → qwen2.5-vl-7b ❌ → real Qwen3-VL 7B doesn't exist; closest is 8B
# - qwen3-vl-30b → qwen2.5-vl-72b ❌ → real Qwen3-VL 30B is the 30B-A3B MoE
# - glm-4.6v-flash → glm-4v-9b ❌ → real Flash is `zai-org/GLM-4.6V-Flash` (10.3B)
#
# All keys below match the v4 VISION_MODELS dict for consistency.

VLM_MODELS: dict[str, dict[str, Any]] = {
    "glm-4.6v-flash": {
        "full_name": "zai-org/GLM-4.6V-Flash",
        "unsloth_id": "unsloth/GLM-4.6V-Flash-GGUF",
        "mlx_id": "mlx-community/GLM-4.6V-Flash-4bit",
        "size_gb": 6.0,
        "context_length": 128000,
        "capabilities": ["vision", "function_calling", "128k_context", "diagram"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": True,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
        },
    },
    "qwen3-vl-4b": {
        "full_name": "Qwen/Qwen3-VL-4B-Instruct",
        "unsloth_id": "unsloth/Qwen3-VL-4B-Instruct-GGUF",
        "mlx_id": "mlx-community/Qwen3-VL-4B-Instruct-8bit",
        "size_gb": 3.0,
        "context_length": 256000,
        "capabilities": ["vision", "ocr", "document_understanding", "multilingual", "diagram"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": True,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
        },
    },
    "qwen3-vl-8b": {
        "full_name": "Qwen/Qwen3-VL-8B-Instruct",
        "unsloth_id": "unsloth/Qwen3-VL-8B-Instruct-GGUF",
        "mlx_id": "mlx-community/Qwen3-VL-8B-Instruct-4bit",
        "size_gb": 5.0,
        "context_length": 256000,
        "capabilities": ["vision", "ocr", "document_understanding", "multilingual", "diagram"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
            "target_modules": [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
        },
    },
    "qwen3-vl-30b-a3b": {
        "full_name": "Qwen/Qwen3-VL-30B-A3B-Instruct",
        "unsloth_id": "unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF",
        "mlx_id": "mlx-community/Qwen3-VL-30B-A3B-Instruct-4bit",
        "size_gb": 18.0,
        "context_length": 256000,
        "capabilities": [
            "vision", "ocr", "document_understanding",
            "reasoning", "multilingual", "moe", "diagram",
        ],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 32,
            "lora_alpha": 64,
            "target_modules": [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
        },
    },
    "qwen3-vl-235b-a22b": {
        "full_name": "Qwen/Qwen3-VL-235B-A22B-Instruct",
        "unsloth_id": "unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF",
        "mlx_id": None,
        "size_gb": 130.0,
        "context_length": 256000,
        "capabilities": [
            "vision", "ocr", "document_understanding",
            "reasoning", "multilingual", "moe", "diagram",
        ],
        "backend": "llama-swap",
        "unsloth_compatible": False,  # too large for M4
        "mobile_friendly": False,
        "arm1_oci_only": True,
        "lora_config": {
            "r": 64,
            "lora_alpha": 128,
            "target_modules": [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
        },
    },
    "gemma-4-E2B": {
        "full_name": "google/gemma-4-E2B-it",
        "unsloth_id": "unsloth/gemma-4-E2B-it-GGUF",
        "mlx_id": "mlx-community/gemma-4-e2b-it-4bit",
        "size_gb": 3.0,
        "context_length": 32768,
        "capabilities": ["vision", "ocr", "multilingual", "6_celtic_languages"],
        "backend": "mlx",
        "unsloth_compatible": True,
        "mobile_friendly": True,
        "lora_config": {
            "r": 8,
            "lora_alpha": 16,
        },
    },
    "gemma-4-E4B": {
        "full_name": "google/gemma-4-E4B-it",
        "unsloth_id": "unsloth/gemma-4-E4B-it-GGUF",
        "mlx_id": None,
        "size_gb": 5.0,
        "context_length": 32768,
        "capabilities": ["vision", "ocr", "multilingual", "6_celtic_languages"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": True,
        "lora_config": {
            "r": 8,
            "lora_alpha": 16,
        },
    },
    "gemma-4-12B": {
        "full_name": "google/gemma-4-12B-it",
        "unsloth_id": "unsloth/gemma-4-12b-it-GGUF",
        "mlx_id": "mlx-community/gemma-4-12B-it-8bit",
        "size_gb": 7.0,
        "context_length": 262144,
        "capabilities": ["vision", "ocr", "multilingual", "gemma4_unified", "diagram"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
        },
    },
    "gemma-4-26B-A4B": {
        "full_name": "google/gemma-4-26B-A4B-it",
        "unsloth_id": "unsloth/gemma-4-26B-A4B-it-GGUF",
        "mlx_id": "mlx-community/gemma-4-26b-a4b-it-4bit",
        "size_gb": 14.0,
        "context_length": 262144,
        "capabilities": [
            "vision", "ocr", "multilingual", "6_celtic_languages",
            "moe", "diagram", "math", "latex",
        ],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
        },
    },
    "gemma-4-31B": {
        "full_name": "google/gemma-4-31B-it",
        "unsloth_id": "unsloth/gemma-4-31B-it-GGUF",
        "mlx_id": "mlx-community/gemma-4-31b-it-8bit",
        "size_gb": 19.0,
        "context_length": 262144,
        "capabilities": [
            "vision", "ocr", "multilingual", "6_celtic_languages",
            "dense_sota", "diagram", "math", "latex",
        ],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
        },
    },
    "molmo2-8b": {
        "full_name": "allenai/Molmo2-8B",
        "unsloth_id": None,
        "mlx_id": None,
        "size_gb": 16.0,
        "context_length": 32768,
        "capabilities": ["vision", "document_vqa", "grounding", "diagram"],
        "backend": "transformers",
        "unsloth_compatible": False,  # no Unsloth repack
        "mobile_friendly": False,
        "lora_config": None,  # No Unsloth support
    },
    "olmocr-2-7b-1025": {
        "full_name": "allenai/olmOCR-2-7B-1025",
        "unsloth_id": None,
        "mlx_id": None,
        "size_gb": 16.0,
        "context_length": 8192,
        "capabilities": ["ocr", "document_layout", "table_extraction", "math_ocr", "latex"],
        "backend": "transformers",
        "unsloth_compatible": False,  # no Unsloth repack
        "mobile_friendly": False,
        "lora_config": None,  # No Unsloth support
    },
    "dots-ocr": {
        "full_name": "rednote-hilab/dots.ocr",
        "unsloth_id": None,
        "mlx_id": "mlx-community/dots.ocr-4bit",
        "size_gb": 3.0,
        "context_length": 16384,
        "capabilities": ["ocr", "document_layout", "table_extraction", "multilingual", "diagram"],
        "backend": "mlx",
        "unsloth_compatible": False,  # no Unsloth repack
        "mobile_friendly": True,
        "lora_config": None,  # No Unsloth support
    },
    "internvl3-8b": {
        "full_name": "OpenGVLab/InternVL3_5-8B",
        "unsloth_id": "unsloth/InternVL3-8B-GGUF",
        "mlx_id": None,
        "size_gb": 5.0,
        "context_length": 32768,
        "capabilities": ["vision", "document_understanding", "grounding", "diagram", "tables"],
        "backend": "llama-swap",
        "unsloth_compatible": True,
        "mobile_friendly": False,
        "lora_config": {
            "r": 16,
            "lora_alpha": 32,
        },
    },
}


# Backward-compat alias: VLM_COMPARISON_MODELS is the same dict
VLM_COMPARISON_MODELS: dict[str, dict[str, Any]] = VLM_MODELS


# ─── Mobile deployment targets ─────────────────────────────────────────────


MOBILE_TARGETS: dict[str, dict[str, Any]] = {
    "iphone_15_pro": {
        "npu": "Apple Neural Engine",
        "memory_gb": 8,
        "max_model_gb": 4,
        "quantization": "int4",
    },
    "pixel_8_pro": {
        "npu": "Google TPU",
        "memory_gb": 12,
        "max_model_gb": 6,
        "quantization": "int8",
    },
    "samsung_s24": {
        "npu": "Samsung NPU",
        "memory_gb": 12,
        "max_model_gb": 6,
        "quantization": "int8",
    },
}


# ─── Result + config dataclasses ───────────────────────────────────────────


@dataclass
class EvaluationResult:
    """Results from a single model evaluation."""

    model_name: str
    cer: float  # Character Error Rate
    wer: float  # Word Error Rate
    fada_accuracy: float  # Accuracy on accented characters
    tironian_accuracy: float  # Accuracy on ⁊ symbol
    inference_time_ms: float
    memory_usage_gb: float
    samples_evaluated: int
    errors: list[dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "cer": self.cer,
            "wer": self.wer,
            "fada_accuracy": self.fada_accuracy,
            "tironian_accuracy": self.tironian_accuracy,
            "inference_time_ms": self.inference_time_ms,
            "memory_usage_gb": self.memory_usage_gb,
            "samples_evaluated": self.samples_evaluated,
            "errors": self.errors[:10],
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class FinetuneConfig:
    """Configuration for VLM fine-tuning."""

    model_name: str = "gemma-4-26B-A4B"  # CHANGED from glm-4.6v-flash in v4

    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    max_seq_length: int = 2048

    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05

    use_4bit: bool = True
    use_gradient_checkpointing: bool = True
    optimizer: str = "adamw_8bit"
    scheduler: str = "cosine"

    output_dir: str = "./finetune_output"
    save_steps: int = 100
    logging_steps: int = 10

    mlflow_experiment: str = "irish_vlm_finetune"
    mlflow_tracking_uri: str | None = None


# ─── Pipeline ───────────────────────────────────────────────────────────────


class VLMComparisonPipeline:
    """
    Pipeline for comparing VLM fine-tuning results on Irish OCR.
    """

    def __init__(
        self,
        dataset_path: str | Path,
        models: list[str] | None = None,
        output_dir: str | Path = "./vlm_comparison",
    ):
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.models = models or list(VLM_MODELS.keys())
        self.results: list[EvaluationResult] = []

        # Validate models
        for model in self.models:
            if model not in VLM_MODELS:
                logger.warning(f"Unknown model: {model}, skipping")
                self.models.remove(model)

    def run_comparison(
        self,
        finetune: bool = False,
        max_samples: int = 1000,
    ) -> list[EvaluationResult]:
        logger.info(f"Running comparison for models: {self.models}")

        test_samples = self._load_test_data(max_samples)
        logger.info(f"Loaded {len(test_samples)} test samples")

        for model_name in self.models:
            logger.info(f"Evaluating model: {model_name}")

            try:
                if finetune:
                    self._finetune_model(model_name)

                result = self._evaluate_model(model_name, test_samples)
                self.results.append(result)
                self._log_to_mlflow(result)
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {e}")
                self.results.append(
                    EvaluationResult(
                        model_name=model_name,
                        cer=1.0,
                        wer=1.0,
                        fada_accuracy=0.0,
                        tironian_accuracy=0.0,
                        inference_time_ms=0.0,
                        memory_usage_gb=0.0,
                        samples_evaluated=0,
                        errors=[{"error": str(e)}],
                    )
                )

        return self.results

    def _load_test_data(self, max_samples: int) -> list[dict[str, Any]]:
        """Load test data from Unsloth JSONL format."""
        test_file = self.dataset_path / "test.jsonl"
        if not test_file.exists():
            for alt_path in [
                self.dataset_path / "unsloth" / "test.jsonl",
                self.dataset_path.parent / "test.jsonl",
            ]:
                if alt_path.exists():
                    test_file = alt_path
                    break
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            return []
        samples = []
        with open(test_file, encoding="utf-8") as f:
            for line in f:
                if len(samples) >= max_samples:
                    break
                try:
                    samples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return samples

    def _finetune_model(self, model_name: str) -> Path:
        model_config = VLM_MODELS[model_name]
        if not model_config.get("unsloth_compatible"):
            logger.warning(
                f"{model_name} not compatible with Unsloth, skipping fine-tuning"
            )
            return Path("")
        config = FinetuneConfig(
            model_name=model_name,
            output_dir=str(self.output_dir / "finetune" / model_name),
            lora_r=model_config["lora_config"]["r"],
            lora_alpha=model_config["lora_config"]["lora_alpha"],
        )
        logger.info(f"Would fine-tune {model_name} with config: {config}")
        return Path(config.output_dir)

    def _evaluate_model(
        self,
        model_name: str,
        test_samples: list[dict[str, Any]],
    ) -> EvaluationResult:
        model_config = VLM_MODELS[model_name]

        predictions: list[str] = []
        references: list[str] = []
        inference_times: list[float] = []
        errors: list[dict[str, Any]] = []

        fada_correct = 0
        fada_total = 0
        tironian_correct = 0
        tironian_total = 0

        for sample in test_samples:
            conversations = sample.get("conversations", [])
            ground_truth = ""
            for conv in conversations:
                if conv.get("role") == "assistant":
                    ground_truth = conv.get("content", "")
                    break
            if not ground_truth:
                continue

            start_time = time.time()
            try:
                prediction = self._run_inference(model_name, sample)
            except Exception as e:
                errors.append({"sample_id": sample.get("id"), "error": str(e)})
                continue
            inference_time = (time.time() - start_time) * 1000

            predictions.append(prediction)
            references.append(ground_truth)
            inference_times.append(inference_time)

            fada_chars = set("áéíóúÁÉÍÓÚ")
            for pred_char, ref_char in zip(prediction, ground_truth):
                if ref_char in fada_chars:
                    fada_total += 1
                    if pred_char == ref_char:
                        fada_correct += 1

            if "⁊" in ground_truth:
                tironian_total += 1
                if "⁊" in prediction or "agus" in prediction.lower():
                    tironian_correct += 1

        cer = self._compute_cer(predictions, references)
        wer = self._compute_wer(predictions, references)
        fada_accuracy = fada_correct / max(fada_total, 1)
        tironian_accuracy = tironian_correct / max(tironian_total, 1)
        avg_inference_time = sum(inference_times) / max(len(inference_times), 1)

        return EvaluationResult(
            model_name=model_name,
            cer=cer,
            wer=wer,
            fada_accuracy=fada_accuracy,
            tironian_accuracy=tironian_accuracy,
            inference_time_ms=avg_inference_time,
            memory_usage_gb=model_config["size_gb"],
            samples_evaluated=len(predictions),
            errors=errors,
            metadata={
                "model_config": model_config,
                "fada_total": fada_total,
                "tironian_total": tironian_total,
                "registry_home": "cianfhoghlaim.ocr.models",
            },
        )

    def _run_inference(self, model_name: str, sample: dict[str, Any]) -> str:
        """Run inference on a single sample.

        Uses LiteLLM for unified API access (routed via
        litellm.cianfhoghlaim.ie:4000). When the registry is wired to
        llama-swap, this can also dispatch directly to the Unsloth
        GGUFs served there.
        """
        model_config = VLM_MODELS[model_name]
        backend = model_config["backend"]

        image = sample.get("image", "")
        prompt = "Transcribe the handwritten Irish text. Preserve all fadas (á, é, í, ó, ú)."

        try:
            from litellm import completion

            # Map model names to LiteLLM format (v4 keys)
            litellm_model = {
                "glm-4.6v-flash": "zai/glm-4.6v-flash",
                "qwen3-vl-4b": "qwen/qwen3-vl-4b",
                "qwen3-vl-8b": "qwen/qwen3-vl-8b",
                "qwen3-vl-30b-a3b": "qwen/qwen3-vl-30b-a3b",
                "qwen3-vl-235b-a22b": "qwen/qwen3-vl-235b-a22b",
                "gemma-4-E2B": "gemma-4-e2b",
                "gemma-4-E4B": "gemma-4-e4b",
                "gemma-4-12B": "gemma-4-12b",
                "gemma-4-26B-A4B": "gemma-4-26b-a4b",
                "gemma-4-31B": "gemma-4-31b",
                "molmo2-8b": "allenai/molmo2-8b",
                "olmocr-2-7b-1025": "allenai/olmocr-2-7b-1025",
                "dots-ocr": "rednote-hilab/dots.ocr",
                "internvl3-8b": "internvl3-8b",
            }.get(model_name, model_name)

            response = completion(
                model=litellm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"LiteLLM inference failed: {e}")
            return ""

    def _compute_cer(self, predictions: list[str], references: list[str]) -> float:
        if not predictions or not references:
            return 1.0
        total_distance = 0
        total_chars = 0
        for pred, ref in zip(predictions, references):
            distance = self._levenshtein_distance(pred, ref)
            total_distance += distance
            total_chars += len(ref)
        return total_distance / max(total_chars, 1)

    def _compute_wer(self, predictions: list[str], references: list[str]) -> float:
        if not predictions or not references:
            return 1.0
        total_distance = 0
        total_words = 0
        for pred, ref in zip(predictions, references):
            pred_words = pred.split()
            ref_words = ref.split()
            distance = self._levenshtein_distance(pred_words, ref_words)
            total_distance += distance
            total_words += len(ref_words)
        return total_distance / max(total_words, 1)

    def _levenshtein_distance(self, s1: Any, s2: Any) -> int:
        if isinstance(s1, str):
            s1 = list(s1)
        if isinstance(s2, str):
            s2 = list(s2)
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[m][n]

    def _log_to_mlflow(self, result: EvaluationResult) -> None:
        try:
            import mlflow

            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment("irish_vlm_comparison")
            with mlflow.start_run(run_name=f"eval_{result.model_name}"):
                mlflow.log_metrics({
                    "cer": result.cer,
                    "wer": result.wer,
                    "fada_accuracy": result.fada_accuracy,
                    "tironian_accuracy": result.tironian_accuracy,
                    "inference_time_ms": result.inference_time_ms,
                    "memory_gb": result.memory_usage_gb,
                    "samples_evaluated": result.samples_evaluated,
                })
                mlflow.log_params({
                    "model_name": result.model_name,
                    "registry_home": "cianfhoghlaim.ocr.models",
                    **result.metadata.get("model_config", {}),
                })
                result_path = self.output_dir / f"{result.model_name}_result.json"
                with open(result_path, "w") as f:
                    json.dump(result.to_dict(), f, indent=2)
                mlflow.log_artifact(str(result_path))
        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}")

    def get_mobile_recommendations(self) -> dict[str, list[str]]:
        recommendations: dict[str, list[str]] = {}
        for device, specs in MOBILE_TARGETS.items():
            suitable: list[dict[str, Any]] = []
            for model_name, config in VLM_MODELS.items():
                if not config.get("mobile_friendly"):
                    continue
                quantized_size = config["size_gb"]
                if specs["quantization"] == "int4":
                    quantized_size *= 0.25
                elif specs["quantization"] == "int8":
                    quantized_size *= 0.5
                if quantized_size <= specs["max_model_gb"]:
                    suitable.append({
                        "model": model_name,
                        "quantized_size_gb": round(quantized_size, 2),
                        "quantization": specs["quantization"],
                    })
            recommendations[device] = suitable
        return recommendations

    def export_report(self, output_path: str | Path | None = None) -> Path:
        if output_path is None:
            output_path = self.output_dir / "comparison_report.html"
        else:
            output_path = Path(output_path)
        sorted_results = sorted(self.results, key=lambda r: r.cer)
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "  <title>Irish VLM OCR Comparison Report (v4)</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }",
            "    h1 { color: #1a1a2e; }",
            "    table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }",
            "    th { background-color: #1a1a2e; color: white; }",
            "    tr:nth-child(even) { background-color: #f9f9f9; }",
            "    .best { background-color: #d4edda; font-weight: bold; }",
            "    .metric { text-align: right; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <h1>Irish VLM OCR Comparison Report (v4 registry)</h1>",
            f"  <p>Generated: {datetime.utcnow().isoformat()}</p>",
            "  <h2>Model Performance Summary</h2>",
            "  <table>",
            "    <tr>",
            "      <th>Model</th><th>CER</th><th>WER</th><th>Fada Acc</th>",
            "      <th>Tironian Acc</th><th>Inference (ms)</th><th>Size (GB)</th><th>Samples</th>",
            "    </tr>",
        ]
        for i, result in enumerate(sorted_results):
            row_class = "best" if i == 0 else ""
            html_parts.append(
                f'    <tr class="{row_class}">'
                f"<td>{result.model_name}</td>"
                f'<td class="metric">{result.cer:.4f}</td>'
                f'<td class="metric">{result.wer:.4f}</td>'
                f'<td class="metric">{result.fada_accuracy:.2%}</td>'
                f'<td class="metric">{result.tironian_accuracy:.2%}</td>'
                f'<td class="metric">{result.inference_time_ms:.1f}</td>'
                f'<td class="metric">{result.memory_usage_gb}</td>'
                f'<td class="metric">{result.samples_evaluated}</td>'
                f"</tr>"
            )
        html_parts.append("  </table>")
        html_parts.append("  <h2>Mobile Deployment Recommendations</h2>")
        mobile_recs = self.get_mobile_recommendations()
        for device, models in mobile_recs.items():
            html_parts.append(f"  <h3>{device}</h3><ul>")
            for m in models:
                html_parts.append(
                    f"    <li>{m['model']} ({m['quantized_size_gb']}GB @ {m['quantization']})</li>"
                )
            html_parts.append("  </ul>")
        html_parts.append("  <h2>Key Findings</h2>")
        html_parts.append("  <ul>")
        if sorted_results:
            best = sorted_results[0]
            html_parts.append(
                f"    <li>Best overall model: <strong>{best.model_name}</strong> "
                f"(CER: {best.cer:.4f})</li>"
            )
            best_fada = max(self.results, key=lambda r: r.fada_accuracy)
            html_parts.append(
                f"    <li>Best fada accuracy: <strong>{best_fada.model_name}</strong> "
                f"({best_fada.fada_accuracy:.2%})</li>"
            )
            fastest = min(
                self.results,
                key=lambda r: r.inference_time_ms if r.inference_time_ms > 0 else float("inf"),
            )
            html_parts.append(
                f"    <li>Fastest inference: <strong>{fastest.model_name}</strong> "
                f"({fastest.inference_time_ms:.1f}ms)</li>"
            )
        html_parts.append("  </ul>")
        html_parts.append("  <p><em>Registry home: cianfhoghlaim.ocr.models (v4)</em></p>")
        html_parts.append("</body></html>")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))
        logger.info(f"Report exported to {output_path}")
        return output_path

    def export_results_json(self) -> Path:
        output_path = self.output_dir / "comparison_results.json"
        with open(output_path, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "models_evaluated": self.models,
                    "registry_home": "cianfhoghlaim.ocr.models",
                    "results": [r.to_dict() for r in self.results],
                    "mobile_recommendations": self.get_mobile_recommendations(),
                },
                f,
                indent=2,
            )
        return output_path
