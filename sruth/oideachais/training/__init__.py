"""
Training module for Irish OCR fine-tuning.

Provides:
- UnslothConfig: Hyperparameter configuration
- UnslothTrainer: Training orchestration
- MLflowCallbacks: Visual artifact logging
- ModalJob: Cloud GPU training
"""

from .unsloth_config import (
    UnslothConfig,
    LoRAConfig,
    VisionConfig,
    TrainingConfig,
)
from .unsloth_trainer import UnslothTrainer
from .mlflow_callbacks import GaelicOCRMLflowCallback

__all__ = [
    "UnslothConfig",
    "LoRAConfig",
    "VisionConfig",
    "TrainingConfig",
    "UnslothTrainer",
    "GaelicOCRMLflowCallback",
]
