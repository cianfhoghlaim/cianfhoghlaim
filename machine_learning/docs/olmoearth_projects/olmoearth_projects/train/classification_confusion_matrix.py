"""Compute confusion matrix for ClassificationTask."""

from typing import Any

import numpy as np
import wandb
from rslearn.train.lightning_module import RslearnLightningModule


class CMLightningModule(RslearnLightningModule):
    """Lightning module extended with confusion matrix for ClassificationTask."""

    def on_validation_epoch_start(self) -> None:
        """Initialize val confusion matrix."""
        self.probs: list = []
        self.y_true: list = []

    def on_val_forward(
        self,
        inputs: list[dict[str, Any]],
        targets: list[dict[str, Any]],
        model_outputs: dict[str, Any],
    ) -> None:
        """Hook to run after the forward pass of the model during validation.

        Args:
            inputs: The input batch.
            targets: The target batch.
            model_outputs: The output of the model, with keys "outputs" and "loss_dict", and possibly other keys.
        """
        for output, target in zip(model_outputs["outputs"], targets):
            if not target["valid"]:
                continue
            self.probs.append(output.cpu().numpy())
            self.y_true.append(target["class"].cpu().numpy())

    def on_validation_epoch_end(self) -> None:
        """Submit the val confusion matrix."""
        self.logger.experiment.log(
            {
                "val_cm": wandb.plot.confusion_matrix(
                    probs=np.stack(self.probs),
                    y_true=np.stack(self.y_true),
                    class_names=self.task.classes,
                )
            }
        )

    def on_test_epoch_start(self) -> None:
        """Initialize test confusion matrix."""
        self.probs = []
        self.y_true = []

    def on_test_forward(
        self,
        inputs: list[dict[str, Any]],
        targets: list[dict[str, Any]],
        model_outputs: dict[str, Any],
    ) -> None:
        """Hook to run after the forward pass of the model during testing.

        Args:
            inputs: The input batch.
            targets: The target batch.
            model_outputs: The output of the model, with keys "outputs" and "loss_dict", and possibly other keys.
        """
        for output, target in zip(model_outputs["outputs"], targets):
            if not target["valid"]:
                continue
            self.probs.append(output.cpu().numpy())
            self.y_true.append(target["class"].cpu().numpy())

    def on_test_epoch_end(self) -> None:
        """Submit the test confusion matrix."""
        self.logger.experiment.log(
            {
                "test_cm": wandb.plot.confusion_matrix(
                    probs=np.stack(self.probs),
                    y_true=np.stack(self.y_true),
                    class_names=self.task.classes,
                )
            }
        )
