"""
HTR model training using SAM3 and similar architectures.

Trains handwriting text recognition models for Celtic manuscripts.
"""

from __future__ import annotations

from dagster import (
    asset,
    AssetExecutionContext,
    Config,
    Output,
    MetadataValue,
)


class HTRTrainingConfig(Config):
    """Configuration for HTR training."""

    model_name: str = "sam3-celtic-htr"
    base_model: str = "SAM3"
    batch_size: int = 16
    epochs: int = 50
    learning_rate: float = 1e-4
    gpu_provider: str = "modal"  # modal, thundercompute, local


@asset(
    group_name="htr_training",
    description="Configure HTR training run",
)
def htr_training_config(
    context: AssetExecutionContext,
    config: HTRTrainingConfig,
    htr_training_dataset: dict,
) -> Output[dict]:
    """Configure HTR training run."""
    training_config = {
        "model": {
            "name": config.model_name,
            "base": config.base_model,
            "architecture": "encoder-decoder",
            "encoder": "ViT-L",
            "decoder": "transformer",
        },
        "training": {
            "batch_size": config.batch_size,
            "epochs": config.epochs,
            "learning_rate": config.learning_rate,
            "optimizer": "AdamW",
            "scheduler": "cosine",
            "warmup_steps": 1000,
        },
        "data": {
            "train_samples": htr_training_dataset["train_samples"],
            "val_samples": htr_training_dataset["val_samples"],
            "augmentation": [
                "random_crop",
                "color_jitter",
                "gaussian_blur",
            ],
        },
        "gpu_provider": config.gpu_provider,
        "estimated_cost": "$40-80",  # Based on Modal A100 pricing
    }

    return Output(
        training_config,
        metadata={
            "model_name": MetadataValue.text(config.model_name),
            "epochs": MetadataValue.int(config.epochs),
            "gpu_provider": MetadataValue.text(config.gpu_provider),
        },
    )


@asset(
    group_name="htr_training",
    description="Train HTR model",
    deps=[htr_training_config],
)
def trained_htr_model(
    context: AssetExecutionContext,
    htr_training_config: dict,
) -> Output[dict]:
    """Train HTR model on Celtic manuscript data."""
    # In production, this would:
    # 1. Submit training job to Modal/ThunderCompute
    # 2. Monitor training progress
    # 3. Save checkpoints

    model_info = {
        "name": htr_training_config["model"]["name"],
        "status": "pending",
        "checkpoint_path": None,
        "metrics": {
            "cer": None,  # Character Error Rate
            "wer": None,  # Word Error Rate
        },
    }

    context.log.info(f"Would train {model_info['name']} on {htr_training_config['gpu_provider']}")

    return Output(
        model_info,
        metadata={
            "model_name": MetadataValue.text(model_info["name"]),
            "status": MetadataValue.text(model_info["status"]),
        },
    )


# Export assets
htr_training_assets = [
    htr_training_config,
    trained_htr_model,
]
