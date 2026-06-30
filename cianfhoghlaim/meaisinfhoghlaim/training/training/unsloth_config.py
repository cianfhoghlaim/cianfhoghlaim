"""
Unsloth Training Configuration for Qwen2-VL Fine-tuning.

Hyperparameters optimized for Irish handwriting recognition based on:
- taighde_teanga/Finetuning Qwen3-VL for Gaelic OCR.md
- taighde_new/document-intelligence-ocr.md

Key optimizations:
- High LoRA rank (64+) for visual nuances
- Vision layer fine-tuning enabled
- 4-bit quantization for memory efficiency
- Gradient checkpointing for VRAM savings

Usage:
    from training import UnslothConfig

    config = UnslothConfig.for_gaelic_ocr()
    # or
    config = UnslothConfig(
        model_name="unsloth/Qwen2-VL-7B-Instruct-bnb-4bit",
        lora=LoRAConfig(r=64),
    )
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LoRAConfig:
    """LoRA adapter configuration."""

    r: int = 64  # High rank for visual nuances (Gaelic script)
    lora_alpha: int = 64
    lora_dropout: float = 0.0
    target_modules: list[str] = field(
        default_factory=lambda: [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )
    bias: str = "none"
    use_gradient_checkpointing: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Unsloth."""
        return {
            "r": self.r,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "target_modules": self.target_modules,
            "bias": self.bias,
            "use_gradient_checkpointing": self.use_gradient_checkpointing,
        }


@dataclass
class VisionConfig:
    """Vision encoder configuration."""

    finetune_vision_layers: bool = True  # Critical for Gaelic script
    min_pixels: int = 256 * 28 * 28  # 200,704
    max_pixels: int = 1280 * 28 * 28  # 1,003,520
    image_factor: int = 28
    max_image_tokens: int = 4096

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "finetune_vision_layers": self.finetune_vision_layers,
            "min_pixels": self.min_pixels,
            "max_pixels": self.max_pixels,
            "image_factor": self.image_factor,
            "max_image_tokens": self.max_image_tokens,
        }


@dataclass
class TrainingConfig:
    """Training hyperparameters."""

    max_seq_length: int = 4096
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    max_steps: int = -1  # -1 = use num_train_epochs
    num_train_epochs: int = 3
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    optim: str = "adamw_8bit"
    lr_scheduler_type: str = "cosine"
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 500
    save_total_limit: int = 3
    seed: int = 42
    fp16: bool = False
    bf16: bool = True  # Use bfloat16 for stability
    dataloader_num_workers: int = 4
    remove_unused_columns: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to training arguments."""
        return {
            "max_seq_length": self.max_seq_length,
            "per_device_train_batch_size": self.per_device_train_batch_size,
            "per_device_eval_batch_size": self.per_device_eval_batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "warmup_steps": self.warmup_steps,
            "max_steps": self.max_steps,
            "num_train_epochs": self.num_train_epochs,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "optim": self.optim,
            "lr_scheduler_type": self.lr_scheduler_type,
            "logging_steps": self.logging_steps,
            "eval_steps": self.eval_steps,
            "save_steps": self.save_steps,
            "save_total_limit": self.save_total_limit,
            "seed": self.seed,
            "fp16": self.fp16,
            "bf16": self.bf16,
            "dataloader_num_workers": self.dataloader_num_workers,
            "remove_unused_columns": self.remove_unused_columns,
        }


@dataclass
class UnslothConfig:
    """
    Complete Unsloth training configuration.
    """

    # Model
    model_name: str = "unsloth/Qwen2-VL-7B-Instruct-bnb-4bit"
    load_in_4bit: bool = True
    use_flash_attention: bool = True

    # Components
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    # Paths
    output_dir: str = "./outputs"
    cache_dir: str | None = None
    dataset_path: str = "./training_data"

    # MLflow
    mlflow_experiment_name: str = "gaelic-ocr-finetuning"
    mlflow_tracking_uri: str = "mlruns"

    # Data
    train_file: str = "train_dense_ocr.jsonl"
    eval_file: str = "val_dense_ocr.jsonl"
    max_train_samples: int | None = None
    max_eval_samples: int | None = None

    @classmethod
    def for_gaelic_ocr(cls) -> "UnslothConfig":
        """
        Optimized configuration for Gaelic OCR.

        Based on research recommendations:
        - High LoRA rank (64) for subtle visual nuances
        - Vision layer fine-tuning enabled
        - 4-bit quantization for memory efficiency
        """
        return cls(
            model_name="unsloth/Qwen2-VL-7B-Instruct-bnb-4bit",
            lora=LoRAConfig(
                r=64,
                lora_alpha=64,
                target_modules=[
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
            ),
            vision=VisionConfig(
                finetune_vision_layers=True,
                min_pixels=256 * 28 * 28,
                max_pixels=1280 * 28 * 28,
            ),
            training=TrainingConfig(
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                learning_rate=2e-4,
                num_train_epochs=3,
            ),
        )

    @classmethod
    def for_quick_test(cls) -> "UnslothConfig":
        """
        Quick configuration for testing pipeline.
        """
        return cls(
            model_name="unsloth/Qwen2-VL-2B-Instruct-bnb-4bit",
            lora=LoRAConfig(
                r=16,
                lora_alpha=16,
            ),
            training=TrainingConfig(
                per_device_train_batch_size=1,
                gradient_accumulation_steps=2,
                max_steps=100,
                logging_steps=10,
                eval_steps=50,
            ),
        )

    @classmethod
    def for_mlx_local(cls) -> "UnslothConfig":
        """
        Configuration for local Apple Silicon training.
        """
        return cls(
            model_name="mlx-community/Qwen2-VL-7B-Instruct-4bit",
            load_in_4bit=True,
            lora=LoRAConfig(
                r=32,
                lora_alpha=32,
            ),
            training=TrainingConfig(
                per_device_train_batch_size=1,
                gradient_accumulation_steps=8,
                bf16=False,  # MLX handles precision internally
            ),
        )

    @classmethod
    def for_modal_cloud(cls) -> "UnslothConfig":
        """
        Configuration for Modal cloud GPU training.
        """
        return cls(
            model_name="unsloth/Qwen2-VL-7B-Instruct-bnb-4bit",
            lora=LoRAConfig(
                r=64,
                lora_alpha=64,
            ),
            training=TrainingConfig(
                per_device_train_batch_size=4,
                gradient_accumulation_steps=2,
                num_train_epochs=5,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert full config to dictionary."""
        return {
            "model_name": self.model_name,
            "load_in_4bit": self.load_in_4bit,
            "use_flash_attention": self.use_flash_attention,
            "lora": self.lora.to_dict(),
            "vision": self.vision.to_dict(),
            "training": self.training.to_dict(),
            "output_dir": self.output_dir,
            "cache_dir": self.cache_dir,
            "dataset_path": self.dataset_path,
            "mlflow_experiment_name": self.mlflow_experiment_name,
            "mlflow_tracking_uri": self.mlflow_tracking_uri,
            "train_file": self.train_file,
            "eval_file": self.eval_file,
            "max_train_samples": self.max_train_samples,
            "max_eval_samples": self.max_eval_samples,
        }

    def save(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        import yaml

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def load(cls, path: str | Path) -> "UnslothConfig":
        """Load configuration from YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            model_name=data.get("model_name", cls.model_name),
            load_in_4bit=data.get("load_in_4bit", True),
            use_flash_attention=data.get("use_flash_attention", True),
            lora=LoRAConfig(**data.get("lora", {})),
            vision=VisionConfig(**data.get("vision", {})),
            training=TrainingConfig(**data.get("training", {})),
            output_dir=data.get("output_dir", "./outputs"),
            cache_dir=data.get("cache_dir"),
            dataset_path=data.get("dataset_path", "./training_data"),
            mlflow_experiment_name=data.get("mlflow_experiment_name", "gaelic-ocr"),
            mlflow_tracking_uri=data.get("mlflow_tracking_uri", "mlruns"),
            train_file=data.get("train_file", "train_dense_ocr.jsonl"),
            eval_file=data.get("eval_file", "val_dense_ocr.jsonl"),
            max_train_samples=data.get("max_train_samples"),
            max_eval_samples=data.get("max_eval_samples"),
        )
