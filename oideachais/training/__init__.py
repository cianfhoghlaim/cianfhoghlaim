"""
Training module for Irish OCR fine-tuning.

Provides:
- UnslothConfig: Hyperparameter configuration
- UnslothTrainer: Training orchestration
- MLflowCallbacks: Visual artifact logging
- ModalJob: Cloud GPU training
"""

from .mlflow_callbacks import GaelicOCRMLflowCallback
from .unsloth_config import (
    LoRAConfig,
    TrainingConfig,
    UnslothConfig,
    VisionConfig,
)
from .unsloth_trainer import UnslothTrainer

__all__ = [
    "UnslothConfig",
    "LoRAConfig",
    "VisionConfig",
    "TrainingConfig",
    "UnslothTrainer",
    "GaelicOCRMLflowCallback",
]
