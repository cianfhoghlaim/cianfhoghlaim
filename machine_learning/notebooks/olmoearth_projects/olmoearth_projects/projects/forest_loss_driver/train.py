"""rslearn training components for forest loss driver classification."""

from typing import Any

import torch
from rslearn.train.tasks.classification import ClassificationTask
from rslearn.utils import Feature

CATEGORY_MAPPING = {
    "agriculture-generic": "agriculture",
    "agriculture-small": "agriculture",
    "agriculture-mennonite": "agriculture",
    "agriculture-rice": "agriculture",
    "coca": "agriculture",
    "flood": "river",
}


class ForestLossTask(ClassificationTask):
    """Forest loss task.

    It is a classification task but just adds some additional pre-processing because of
    the format of the labels where the labels are hierarchical but we want to remap
    them to a particular flat set.
    """

    def process_inputs(
        self,
        raw_inputs: dict[str, torch.Tensor | list[Feature]],
        metadata: dict[str, Any],
        load_targets: bool = True,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Processes the data into targets.

        This is modified to do category remapping.

        Args:
            raw_inputs: raster or vector data to process
            metadata: metadata about the patch being read
            load_targets: whether to load the targets or only inputs

        Returns:
            tuple (input_dict, target_dict) containing the processed inputs and targets
                that are compatible with both metrics and loss functions
        """
        if not load_targets:
            return {}, {}

        data = raw_inputs["targets"]
        for feat in data:
            for property_name, property_value in self.filters:
                if feat.properties.get(property_name) != property_value:
                    continue
            if self.property_name not in feat.properties:
                continue

            class_name = feat.properties[self.property_name]
            if class_name in CATEGORY_MAPPING:
                class_name = CATEGORY_MAPPING[class_name]
            if class_name not in self.classes:
                continue
            class_id = self.classes.index(class_name)

            return {}, {
                "class": torch.tensor(class_id, dtype=torch.int64),
                "valid": torch.tensor(1, dtype=torch.float32),
            }

        if not self.allow_invalid:
            raise Exception(
                f"no feature found providing class label for window {metadata['window_name']}"
            )

        return {}, {
            "class": torch.tensor(0, dtype=torch.int64),
            "valid": torch.tensor(0, dtype=torch.float32),
        }
